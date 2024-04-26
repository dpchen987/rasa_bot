import json
import random

import requests
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUttered, ActionExecutionRejected, UserUtteranceReverted, ActionExecuted, Restarted, \
    SlotSet, SessionStarted
from rasa_sdk.executor import CollectingDispatcher

import logging

import sys

from utils.prohibit_goods import prohibit_goods

sys.path.append("..")
import global_config

'''
  咨询相关action
  - action_consult_expressman_phone
  - action_consult_send_item
  - action_consult_receive_station_info #派件网点
  - action_consult_send_station_info    #发件网点    
  - action_consult_post_info            #自提点(驿站)
  - action_form_count_rollback
'''

# 该动作调用后端接口来查询快递员电话
class ActionConsultExpressmanPhone(Action):

    def name(self) -> Text:
        return "action_consult_expressman_phone"

    def __init__(self):
        self.url = global_config.WEB_URL+'wdgj-chatbot-server/consult/expressman'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 从跟踪器tracker中获取“运单号槽位”的值
        # test
        dispatcher.utter_message(text='快递员电话查询')
        return []
        slot_express_id = tracker.get_slot('slot_express_id')

        if not slot_express_id:
            logging.warning('slot express id is None!')
            return [SlotSet('slot_core_intent', 'consult')]

        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_express_id).upper()
        payload = json.dumps({"waybillNo": slot_express_id})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        if not isinstance(response, dict):
            dispatcher.utter_message(json_message={"story": "consult_expressman_phone", "api_exception": 3})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if response['status'] != 0:
            dispatcher.utter_message(json_message={"story": "consult_expressman_phone", "api_exception": 2})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if not response['data'] or \
                not response['data']['retMsg']:
            dispatcher.utter_message(json_message={"story": "consult_expressman_phone", "api_exception": 1})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if response['data'].get('status') != 0:
            logging.error('API exception occurred!')
            dispatcher.utter_message(json_message={"story": "consult_expressman_phone", "api_exception": 2})
            return [SlotSet('slot_core_intent', 'consult')]

        # 从后端查询的信息如果不为空则将该信息传递到调度台dispatcher以供机器人输出
        dispatcher.utter_message(text=response['data']['retMsg'])
        # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(json_message={"story": "consult_expressman_phone"})

        # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
        return [SlotSet('slot_core_intent', 'consult')]


# 该动作调用后端接口来查询快递物品能不能寄
class ActionConsultSendItem(Action):

    def name(self) -> Text:
        return "action_consult_send_item"

    def __init__(self):
        self.url = global_config.WEB_URL+'wdgj-chatbot-server/consult/sendingItems'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # test
        dispatcher.utter_message(text='邮寄物品查询')
        return []
        # 禁寄物品的种类
        prohibit_goods_type = ["爆炸物品", "枪支弹药", "毒品及吸毒工具", "易燃气体", "易燃液体", "易燃固体", "日常易燃产品",
                               "毒性物质", "放射性物质", "腐蚀性物质", "生化制品,传染性,感染性物质", "低害物质", "非法出版物,印刷品,音像制品",
                               "管制器具", "非管制器具", "间谍专用器材", "氧化剂和过氧化物", "贵重物品", "非法伪造物品",
                               "濒危野生动物及其制品", "易燃压力罐", "大型压力容器", "普通压力罐", "活物类", "国家机关公文类",
                               "不明液体和粉末类", "电池类", "内置锂电池产品"]
        # 限寄物品的种类
        limit_goods_type = ["电器类", "易碎易坏品", "液体类"]

        # 从跟踪器tracker中获取“物品槽位”的值
        slot_item = tracker.get_slot('slot_item')
        if slot_item is None:
            logging.warning("There is no slot_item")
            # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
            return [SlotSet('slot_core_intent', 'consult')]
        slot_item = str(slot_item)
        payload = json.dumps({"items": slot_item})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        if not isinstance(response, dict):
            dispatcher.utter_message(json_message={"story": "consult_send_item", "api_exception": 3})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if response['status'] != 0:
            dispatcher.utter_message(json_message={"story": "consult_send_item", "api_exception": 2})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if not response['data']:
            dispatcher.utter_message(json_message={"story": "consult_send_item", "api_exception": 1})
            logging.error('API response is None!')
            return [SlotSet('slot_core_intent', 'consult')]

        # 通过后端接口的返回值获取该物品所属的类别
        item_type = response['data'].get("subType")
        # 对物品类别分别进行判断，然后将满足条件的话术名称传输给调度器dispatcher以供机器人输出
        if item_type in prohibit_goods_type:
            dispatcher.utter_message(response='utter_consult_prohibite_goods')
        elif item_type in limit_goods_type:
            dispatcher.utter_message(response='utter_consult_can_not_post')
            dispatcher.utter_message(response='utter_consult_station_if_can_post')
        elif item_type == '烟草类':
            dispatcher.utter_message(response='utter_consult_cigarette_good')
        else:
            dispatcher.utter_message(response='utter_consult_can_post')

        # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(json_message={"story": "consult_send_item"})

        # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
        return [SlotSet('slot_core_intent', 'consult')]


# 该动作调用后端接口来查询派件网点信息
class ActionConsultReceiveStationInfo(Action):

    def name(self) -> Text:
        return "action_consult_receive_station_info"

    def __init__(self):
        self.url = global_config.WEB_URL+'wdgj-chatbot-server/consult/orgInfo'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # test
        dispatcher.utter_message(text='派件网点信息查询')
        return []
        # 从跟踪器tracker中获取“运单号槽位”的值# 从跟踪器tracker中获取“运单号槽位”的值
        slot_express_id = tracker.get_slot('slot_express_id')
        if slot_express_id is None:
            logging.warning("There is no slot_express_id")
            # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
            return [SlotSet('slot_core_intent', 'consult')]

        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_express_id).upper()
        payload = json.dumps({"waybillNo": slot_express_id})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        if not isinstance(response, dict):
            dispatcher.utter_message(json_message={"story": "consult_receive_station_info", "api_exception": 3})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if response['status'] != 0:
            dispatcher.utter_message(json_message={"story": "consult_receive_station_info", "api_exception": 2})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if not response['data']:
            dispatcher.utter_message(json_message={"story": "consult_receive_station_info", "api_exception": 1})
            logging.error('API response is None')
            return [SlotSet('slot_core_intent', 'consult')]

        # 抛出正在查询话术“utter_consult_check”，对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(response='utter_consult_check', json_message={"story": "consult_receive_station_info"})

        # 根据后端接口返回的值，分别获取地址、电话和姓名等，并且尽可能多返回所获取的信息
        org_address = response['data'].get('orgAddress')
        cs_phone = response['data'].get('csPhone')
        org_name = response['data'].get('orgName')
        if org_address and cs_phone and org_name:
            res_text = f"{org_name}({org_address})，联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_address and cs_phone:
            res_text = f"{org_address}，联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_name and cs_phone:
            res_text = f"{org_name}，联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_name and org_address:
            res_text = f"{org_name}({org_address})"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if cs_phone:
            res_text = f"联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_address:
            res_text = f"{org_address}"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_name:
            res_text = f"{org_name}"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]

        return [SlotSet('slot_core_intent', 'consult')]


# 该动作调用后端接口来查询发件网点信息
class ActionConsultSendStationInfo(Action):

    def name(self) -> Text:
        return "action_consult_send_station_info"

    def __init__(self):
        self.url = global_config.WEB_URL+'wdgj-chatbot-server/consult/sendingOrgInfo'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # test
        dispatcher.utter_message(text='发件网点信息查询')
        return []
        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = tracker.get_slot('slot_express_id')
        if slot_express_id is None:
            logging.warning("There is no slot_express_id")
            # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
            return [SlotSet('slot_core_intent', 'consult')]

        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_express_id).upper()
        payload = json.dumps({"waybillNo": slot_express_id})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        if not isinstance(response, dict):
            dispatcher.utter_message(json_message={"story": "consult_send_station_info", "api_exception": 3})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if response['status'] != 0:
            dispatcher.utter_message(json_message={"story": "consult_send_station_info", "api_exception": 2})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if not response['data']:
            dispatcher.utter_message(json_message={"story": "consult_send_station_info", "api_exception": 1})
            logging.error('API response is None')
            return [SlotSet('slot_core_intent', 'consult')]

        # 抛出正在查询话术“utter_consult_check”，对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(response='utter_consult_check', json_message={"story": "consult_send_station_info"})

        # 根据后端接口返回的值，分别获取地址、电话和姓名等，并且尽可能多返回所获取的信息
        org_address = response['data'].get('orgAddress')
        cs_phone = response['data'].get('csPhone')
        org_name = response['data'].get('orgName')
        if org_address and cs_phone and org_name:
            res_text = f"{org_name}({org_address})，联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_address and cs_phone:
            res_text = f"{org_address}，联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_name and cs_phone:
            res_text = f"{org_name}，联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_name and org_address:
            res_text = f"{org_name}({org_address})"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if cs_phone:
            res_text = f"联系电话：{cs_phone}。"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_address:
            res_text = f"{org_address}"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        if org_name:
            res_text = f"{org_name}"
            dispatcher.utter_message(text=res_text)
            return [SlotSet('slot_core_intent', 'consult')]
        return [SlotSet('slot_core_intent', 'consult')]


# 该动作调用后端接口来查询驿站信息
class ActionConsultPostInfo(Action):

    def name(self) -> Text:
        return "action_consult_post_info"

    def __init__(self):
        self.url = global_config.WEB_URL + 'wdgj-chatbot-server/consult/yiInfo'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # test
        dispatcher.utter_message(text='驿站信息查询')
        return []
        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = tracker.get_slot('slot_express_id')
        if slot_express_id is None:
            logging.warning("There is no slot_express_id")
            # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
            return [SlotSet('slot_core_intent', 'consult')]

        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_express_id).upper()
        payload = json.dumps({"waybillNo": slot_express_id})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        if not isinstance(response, dict):
            dispatcher.utter_message(json_message={"story": "consult_post_info", "api_exception": 3})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if response['status'] != 0:
            dispatcher.utter_message(json_message={"story": "consult_post_info", "api_exception": 2})
            logging.error('API exception occurred!')
            return [SlotSet('slot_core_intent', 'consult')]

        if not response['data']:
            dispatcher.utter_message(json_message={"story": "consult_post_info", "api_exception": 1})
            logging.error('API response is None')
            return [SlotSet('slot_core_intent', 'consult')]

        if isinstance(response['data'].get('retMsg'), str) and response['data']['retMsg'] == "":
            dispatcher.utter_message(response='utter_default', json_message={"story": "consult_post_info", "api_exception": 1})
            return [SlotSet('slot_core_intent', 'consult')]

        # 抛出正在查询话术“utter_consult_check”
        dispatcher.utter_message(response='utter_consult_check')
        # 从后端查询的信息如果不为空则将该信息传递到调度台dispatcher以供机器人输出，对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(text=response['data']['retMsg'], json_message={"story": "consult_post_info"})

        # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
        return [SlotSet('slot_core_intent', 'consult')]


# 对表单填槽进行计数，达到指定次数后抛出相应话术
class ActionDefaultFallbackConsultSendItem(Action):
    """填槽失败计数并回滚，当填槽失败两次时需要抛出相应话术
    """

    def name(self) -> Text:
        return "action_form_count_rollback"

    # 记录填槽失败次数以及存储最近轮次机器人的回复
    def _count_slot_failure_num(self, events: "List[Event]"):
        """判断是连续填槽失败"""

        failure_count = 0
        failure_flag = False  # 一轮对话中是否是填槽失败标识

        action_name_list = []   # 需要回滚的action列表
        form_name = None
        for index in range(len(events) - 1, 0, -1):
            tmp_event = events[index]

            # 判断有没有填槽失败，如果有，则进行计数
            if tmp_event['event'] == 'action_execution_rejected':
                if form_name is None:
                    form_name = tmp_event['name']
                    failure_count += 1
                elif form_name == tmp_event['name']:
                    failure_count += 1

            # 遇到”active_loop“事件则结束计数
            if tmp_event['event'] == 'active_loop':
                if tmp_event['name'] == form_name:
                    failure_flag = True

            # 提取最近轮次回复
            if tmp_event['event'] == 'bot' and failure_count <= 1 and tmp_event.get('metadata') and\
                    tmp_event.get('metadata').get('utter_action'):
                utter_action = tmp_event['metadata']['utter_action']

                action_name_list.append(utter_action)

            # 填槽失败计数结束后跳出计数循环
            if failure_flag and action_name_list:
                break

        return failure_count, action_name_list


    def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        current_state = tracker.current_state()

        events = current_state['events']
        # from pprint import pprint
        # pprint(events)
        # 判断当前对话是否存在填槽
        active_loop = current_state['active_loop']
        if 'name' not in active_loop:
            return []
        _event = []
        # express_id_piece = tracker.get_slot('slot_express_id_piece')
        # express_id = tracker.get_slot('slot_express_id')
        express_id_piece = tracker.get_slot('slot_express_id_piece')
        express_id = tracker.get_slot('slot_express_id')
        user_messages = tracker.get_slot('slot_user_messages')
        phone_collect = tracker.get_slot('slot_phone_collect')
        if express_id_piece:
            _event.append(SlotSet('slot_express_id_piece', express_id_piece))
        if express_id:
            _event.append(SlotSet('slot_express_id', express_id))
        if user_messages:
            _event.append(SlotSet('slot_user_messages', user_messages))
        if phone_collect:
            _event.append(SlotSet('slot_phone_collect', phone_collect))

        save_slots = ['slot_name', 'slot_user_type', 'slot_big_category', 'slot_small_category']
        for slot in save_slots:
            slot_value = tracker.get_slot(slot)
            if slot_value: 
                _event.append(SlotSet(slot, slot_value))
        # 计算出填槽失败次数和最近轮次机器人的回复
        failure_count, action_name_list = self._count_slot_failure_num(events)

        action_name_list = list(reversed(action_name_list))

        # 填槽失败达到次数的情况抛出对于日志
        logging.debug(f"action_form_count_rollback unknown number:'{failure_count}'")

        # 获取预先设置的运单号填槽失败最大次数槽位
        slot_express_id_form_count = tracker.slots.get("slot_express_id_form_max_count", 0)
        slot_express_id_form_count += 1
        print('slot_express_id_form_max_count', slot_express_id_form_count)
        # 设置一个值max_count用来存储上述槽位值，主要是用于防止上述槽位没有配置的情况
        max_count = 5

        if slot_express_id_form_count == 1:
            dispatcher.utter_message(text='麻烦您提供一下YT+13位数的圆通运单号，我帮您看一下')
        # elif express_id_piece and not express_id and slot_express_id_form_count < max_count:
        #     # 获取最近的text，防止重复输出
        #     last_bot_text = ''
        #     for evt in reversed(events):
        #         if evt['event'] == 'user': break
        #         if evt['event'] == 'bot':
        #             last_bot_text = evt['text']
        #             break
        #     if last_bot_text != f'运单号：{express_id_piece}_':
        #         # 在收集运单号的过程中
        #         dispatcher.utter_message(text= f'运单号：{express_id_piece}_')
        # if slot_express_id_form_count:
        #     max_count = slot_express_id_form_count
        # 当填槽失败次数达到填槽失败最大次数，则指定话术名称传递到调度台dispatcher以供机器人输出
        if False and slot_express_id_form_count >= max_count:
            # dispatcher.utter_message(text='请继续说您的运单号')
            # 最后返回一个会话重启事件，以将会话重置
            return [SessionStarted()]
        else:
            _event.append(SlotSet('slot_express_id_form_max_count', slot_express_id_form_count))
            # 如果填槽失败次数在最大次数范围内，则将机器人的回复逐一传递到调度台dispatcher以供机器人输出
            # for action_name in action_name_list:
            #     dispatcher.utter_message(response=action_name)
            # 最后返回一个“用户回退事件”，该事件的目的是忽略外界的这一轮的输入
            # return []
            return [UserUtteranceReverted()] + _event

