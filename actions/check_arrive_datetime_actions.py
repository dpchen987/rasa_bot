import json
import requests
from typing import Any, Text, Dict, List
from datetime import datetime

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import logging

import sys
sys.path.append("..")
import deploy_config

# 该动作调用后端接口来判断预计到达时间
class ActionCheckArriveDatetime(Action):
    """什么时候到"""

    def name(self) -> Text:
        return "action_check_arrive_datetime"

    def __init__(self):
        self.url = deploy_config.WEB_URL+'wdgj-chatbot-server/intention/utter/queryPreArriveTimeNew'

    # 判断后端返回的信息是否是物流信息
    def is_logistics_track(self, str):
        if len(str) < 10:
            return False
        try:
            datetime.strptime(str[:10], '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # test
        dispatcher.utter_message(text='快件到达时间查询')
        return []
        # 如果之前已经触发过某个流程，现在切换到预计达到时间
        slot_core_intent = tracker.get_slot('slot_core_intent')
        slot_phone = tracker.get_slot('slot_phone')
        if deploy_config.intent_map.get(slot_core_intent) is not None and deploy_config.intent_map.get(slot_core_intent) != 'check_arrive_datetime':
            # 从其他流程切换到预计到达时间，直接走登记，没有电话则抛出要电话话术，有电话则抛出正在登记、已经登记好了、引导结束等话术并重置会话
            if slot_phone is not None:
                dispatcher.utter_message(response='utter_register_is_signing')
                dispatcher.utter_message(response='utter_register_has_signed_base')
                dispatcher.utter_message(response='utter_guide_to_end_has_workorder')
                # dispatcher.utter_message(response='action_session_start')

                # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
                dispatcher.utter_message(json_message={"story": "check_arrive_datetime", "api_exception": None})
                # 对出现过引导结束话术的地方进行标记，供其他相关流程使用
                return [SlotSet("slot_guide_to_end", 1)]
            else:
                # dispatcher.utter_message(response='utter_apologize_reply')
                dispatcher.utter_message(response='utter_ask_phone_appease')
                # dispatcher.utter_message(response='action_session_start')

                dispatcher.utter_message(json_message={"story": "check_arrive_datetime", "api_exception": None})
                return []

        # 从跟踪器tracker中获取“运单号槽位”的值
        slot_express_id = tracker.get_slot('slot_express_id')
        if not slot_express_id:
            logging.error('slot express id is None!')
            return []

        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_express_id).upper()
        payload = json.dumps({"phone": tracker.get_slot('slot_phone'), "waybillNo": slot_express_id})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        # 对后端返回的数据内容格式进行判断，进而返回对应的状态值，后续会根据状态值进行判断并返回对应的值
        status = deploy_config.resp_has_exception(response)
        # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(json_message={"story": "check_arrive_datetime", "api_exception": status})

        if status == 2 or status == 3:
            logging.error('API exception occurred!')
            return []
        if status == 1:
            logging.error('API response is None')
            return []

        messages = response['data']['messages']
        # 获取“有无播报物流槽位”，后续会根据该槽位值判断是否应该播报物流信息messages
        has_logistics_track = tracker.get_slot('slot_has_logistics_track')
        # 使用一个集合存储后端返回的action编码，如果该编码为“5”，则表明该流程不需要登记
        action_num = set()
        register_or_not = 1   # 默认需要登记，登记标志值为“1”
        for message in messages:
            utter_message = message['utterMessage']
            if message['action']:
                action_num.add(message['action'])
            if not utter_message or len(utter_message) == 0:
                continue
            # 后端返回的信息不是物流信息，则将该信息传递到调度台dispatcher以供机器人输出
            if not self.is_logistics_track(utter_message):
                dispatcher.utter_message(text=utter_message)
            # 如果之前没有播报过物流信息且后端返回的信息为物流信息，则将该物流信息传递到调度台dispatcher以供机器人输出，并将“有无播报物流槽位”由默认值“no”赋值为“yes”
            elif has_logistics_track == 'no':
                dispatcher.utter_message(text=utter_message, json_message={"labels": "播报物流"})
                has_logistics_track = 'yes'

        # 如果存储action编码的集合中有“5”，则表明该流程无需登记，将登记标志值赋值为“0”即可
        if 5 in action_num:
            register_or_not = 0

        # 根据登记标志值进行判断进而返回不同的值，如果不需要登记，则需要将槽位“slot_confirm”值设置为“0”(该值默认为“1”)
        # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
        if register_or_not == 1:
            return [SlotSet('slot_core_intent', tracker.get_intent_of_latest_message()),
                    SlotSet('slot_has_logistics_track', has_logistics_track)]
        if register_or_not == 0:
            return [SlotSet('slot_core_intent', tracker.get_intent_of_latest_message()),
                    SlotSet('slot_has_logistics_track', has_logistics_track),
                    SlotSet('slot_confirm', 0)]

        return []