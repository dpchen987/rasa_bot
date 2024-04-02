import requests
import json
from typing import Text, Any, Dict
import re
import random

from rasa_sdk import Tracker, ValidationAction, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import sys
sys.path.append("..")
import global_config



express_id_pat1 = re.compile("(?<![A-Za-z])g\\d{9,13}")
express_id_pat2 = re.compile("(?<![A-Za-z])ytd?\\d{12,14}")
express_id_pat3 = re.compile("(?<![A-Za-z])ytg\\d{11,13}")
express_id_pat4 = re.compile("(?<!\\d)\\d{13}(?!\\d)")
collect_phone_pat1 = re.compile("电话|号码|手机号")
exp_numbers = re.compile(r"[yY][tT]+[dg]?[\d 零令林一幺妖二两三四五六七八九]*")
phone_numbers = re.compile(r"(?<![A-Za-z\d])[1幺妖][3-9三四五六七八九][\d 零令林一幺妖二两三四五六七八九]{,9}(?![A-Za-z\d])")
repat_numbers = re.compile(r"(?<![点月块])[\d零令林一幺妖二两三四五六七八九][\d 零令林一幺妖二两三四五六七八九]*[\d零令林一幺妖二两三四五六七八九](?![点号月块个位])")
numbers_dict = {" ": "", "零": "0", "令": "0", "林": "0", "一": "1", "幺": "1", "妖": "1",  "二": "2", "两": "2", "三": "3", "四": "4","五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}   
# 对机器人识别的槽位进行验证(比如运单号、电话等槽位)
class ValidatePredefinedSlots(ValidationAction):
    def __init__(self):
        self.check_url = global_config.WEB_URL+'wdgj-chatbot-server/waybillInfo/checkWaybillNo'

    def is_first_in(self, tracker: Tracker) -> bool:
        """判断用户输入的第一句是通过metadata传入的词槽"""

        # 从跟踪器tracker中获取首句标志槽位
        slot_first_sentence_used = int(tracker.get_slot('slot_first_sentence_used'))
        current_tracker = tracker.current_state()
        # 根据metadata不为空判断是首句。slot_first_sentence_used=1表示前面已经回复过faq
        if len(current_tracker['events']) > 0 and current_tracker['events'][0].get('name') is not None and \
                current_tracker['events'][0]['name'] == 'session_started_metadata' and slot_first_sentence_used == 0:
            return True

        return False

    async def extract_slot_user_messages(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        # 保存最近的n个用户输入信息
        print("--- extract slot user_messages --->")
        user_messages = str(tracker.get_slot('slot_user_messages'))
        user_messages = eval(user_messages)
        message_text = tracker.latest_message['text']
        user_message = {'intent': tracker.get_intent_of_latest_message(), 'text':message_text, 'usr_type': 1 if message_text.startswith('模型文本') else 0}
        # print('user_messages', type(user_messages), user_messages)

        if not user_messages:
            user_messages = [user_message]
        else:
            user_messages.append(user_message)
            if len(user_messages) > 10: user_messages = user_messages[-10:]
        return {'slot_user_messages': user_messages}
    
    async def extract_slot_phone_collect(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        # 保存最近的n个用户输入信息
        print("--- extract slot phone_collect --->")
        intent_latest = tracker.get_intent_of_latest_message()
        text_latest = tracker.latest_message['text']
        phone_collect = tracker.get_slot('slot_phone_collect')
        # print(phone_collect)
        if phone_collect and intent_latest in ['check_express_status','check_arrive_datetime','signed_but_bot_received','home_delivery']:
            print(intent_latest)
            return {'slot_phone_collect': False}
        elif phone_collect and 'yt' in text_latest:
            return {'slot_phone_collect': False}
        elif not phone_collect and intent_latest in ['phone_number_required', 'provided_phone', 'confirm_whose_phone']:
            return {'slot_phone_collect': True}
        # 根据前面的对话内容判断是否在聊手机号相关内容
        user_messages = eval(str(tracker.get_slot('slot_user_messages')))
        if phone_collect and intent_latest != "inform":
            for inf in reversed(user_messages):
                if inf['intent'] in ['phone_number_required', 'provided_phone', 'confirm_whose_phone']:
                    return
                if collect_phone_pat1.search(inf['text']): return
            return {'slot_phone_collect': False}

    # 验证槽位
    def validate_slot_user_messages(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot phone."""
        print("--- validate slot user_messages --->")
        slot_user_messages = str(slot_value)
        if slot_user_messages:
            return {"slot_user_messages": slot_user_messages}
    # 验证槽位
    def validate_slot_phone_collect(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot phone."""
        print("--- validate slot phone_collect --->")
        slot_phone_collect = str(slot_value)
        if slot_phone_collect:
            return {"slot_phone_collect": slot_phone_collect}

    # 运单号槽位抽取
    async def extract_slot_express_id(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        # 从metadata抽取运单号
        print("--- extract slot express_id --->")
        meta_exp_id = tracker.latest_message.get("metadata").get("express_id")
        if meta_exp_id:
            print('metadata exp_id:', meta_exp_id)
            return {"slot_express_id": meta_exp_id}
        # 从express_id_piece抽取运单号
        intent_latest = tracker.get_intent_of_latest_message()
        express_id_piece = tracker.get_slot('slot_express_id_piece')
        if express_id_piece and len(express_id_piece) > 9 and (express_id_pat1.search(express_id_piece) or express_id_pat2.search(express_id_piece) or express_id_pat3.search(express_id_piece) or express_id_pat4.search(express_id_piece)):
            print('extract express_id:', express_id_piece)
            return {"slot_express_id": express_id_piece}

    # 运单号槽位抽取
    async def extract_slot_express_id_piece(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        # 从metadata抽取运单号
        if tracker.get_slot('slot_phone_collect'): return
        print("--- extract slot express_id piece --->")
        tem = None
        # 从metadata抽取运单号
        express_id_piece = tracker.get_slot('slot_express_id_piece')
        print("tracker_slot_express_id_piece:", express_id_piece)
        current_state = tracker.current_state()
        active_loop = current_state['active_loop']

        answer_text = tracker.latest_message['text']
        intent_latest = tracker.get_intent_of_latest_message()
        # print('tem_piece before:', tem)
        exp_numbers_mth = exp_numbers.search(answer_text)
        exp_pc_mth = repat_numbers.search(answer_text)
        # _event = []
        if exp_numbers_mth:
            exp_numbers_txt = exp_numbers_mth.group()
            for k in numbers_dict:
                if k in exp_numbers_txt:
                    exp_numbers_txt = exp_numbers_txt.replace(k, numbers_dict[k])
            # _event.append(SlotSet('slot_express_id_piece_piece', exp_numbers_txt))
            tem = exp_numbers_txt if len(exp_numbers_txt) <= 15 else "clear"
        if tem:
            print('tem_piece prefix:', tem)
            return {"slot_express_id_piece": tem}
        if exp_pc_mth:
            exp_pc_txt = exp_pc_mth.group()
            for k in numbers_dict:
                if k in exp_pc_txt:
                    exp_pc_txt = exp_pc_txt.replace(k, numbers_dict[k])
            # 重复检测
            if express_id_piece:
                max_window = min(len(express_id_piece), len(exp_pc_txt))
                for wlen in range(max_window, 1, -1):
                    if express_id_piece[-1 * wlen:] == exp_pc_txt[:wlen]:
                        print(exp_pc_txt, "--replace-->", exp_pc_txt[wlen:])
                        exp_pc_txt = exp_pc_txt[wlen:]
                        break

            express_id_piece = express_id_piece + exp_pc_txt if express_id_piece else exp_pc_txt
            # _event.append(SlotSet('slot_express_id_piece_piece', express_id_piece))
            tem = express_id_piece if len(express_id_piece) <= 15 else "clear"
        if tem and (express_id_piece.startswith("yt") or 'name' in active_loop):
            print('tem_piece end:', tem)
            return {"slot_express_id_piece": tem}
        if tem and intent_latest in ['inform', 'service_code']:
            print('tem_piece end:', tem)
            return {"slot_express_id_piece": tem}

    # 验证槽位
    def validate_slot_express_id_piece(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot phone."""

        print("--- validate slot express_id piece --->")
        slot_express_id_piece = str(slot_value)
        slot_express_id = tracker.get_slot("slot_express_id")
        # validation succeeded
        if slot_express_id_piece == "clear":
            return {"slot_express_id_piece": None}
        if slot_express_id_piece:
            if express_id_pat1.search(slot_express_id_piece) or express_id_pat2.search(slot_express_id_piece) or express_id_pat3.search(slot_express_id_piece) or express_id_pat4.search(slot_express_id_piece):
                dispatcher.utter_message(text= f'运单号：{slot_express_id_piece}')
                return {"slot_express_id_piece": None}
            else:
                dispatcher.utter_message(text= f'运单号：{slot_express_id_piece}_')
                return {"slot_express_id_piece": slot_express_id_piece}

    # 运单号槽位抽取
    async def extract_slot_phone_piece(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        # 从metadata抽取运单号
        # 从跟踪器的metadata中获取运单号实体
        if not tracker.get_slot('slot_phone_collect'): return
        print("--- extract slot phone piece --->")
        tem = None
        # 从metadata抽取运单号
        phone_piece = tracker.get_slot('slot_phone_piece')
        print("tracker_slot_phone_piece", phone_piece)
        current_state = tracker.current_state()
        active_loop = current_state['active_loop']

        answer_text = tracker.latest_message['text']
        intent_latest = tracker.get_intent_of_latest_message()
        phone_numbers_mth = phone_numbers.search(answer_text) if not phone_piece else None
        exp_pc_mth = repat_numbers.search(answer_text) if phone_piece else None
        # _event = []
        if phone_numbers_mth:
            phone_numbers_txt = phone_numbers_mth.group()
            for k in numbers_dict:
                if k in phone_numbers_txt:
                    phone_numbers_txt = phone_numbers_txt.replace(k, numbers_dict[k])
            # _event.append(SlotSet('slot_phone_piece_piece', phone_numbers_txt))
            tem = phone_numbers_txt
        if tem:
            print('tem_phone piece prefix:', tem)
            return {"slot_phone_piece": tem}
        if exp_pc_mth:
            exp_pc_txt = exp_pc_mth.group()
            for k in numbers_dict:
                if k in exp_pc_txt:
                    exp_pc_txt = exp_pc_txt.replace(k, numbers_dict[k])
            # 重复检测
            if phone_piece:
                max_window = min(len(phone_piece), len(exp_pc_txt))
                for wlen in range(max_window, 1, -1):
                    if phone_piece[-1 * wlen:] == exp_pc_txt[:wlen]:
                        print(exp_pc_txt, "--replace-->", exp_pc_txt[wlen:])
                        exp_pc_txt = exp_pc_txt[wlen:]
                        break

            phone_piece = phone_piece + exp_pc_txt if phone_piece else exp_pc_txt
            # _event.append(SlotSet('slot_phone_piece_piece', phone_piece))
            tem = phone_piece if len(phone_piece) <= 11 else "clear"
        if tem and intent_latest in ['inform', 'service_code']:
            print('tem_phone_piece end:', tem)
            return {"slot_phone_piece": tem}

    # 验证槽位
    def validate_slot_phone_piece(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot phone."""
        print("--- validate slot phone_piece --->")
        slot_phone_piece = str(slot_value)
        slot_phone = tracker.get_slot("slot_phone")
        # validation succeeded
        if slot_phone_piece == "clear":
            dispatcher.utter_message(text= f'电话号码不太对，请您重新说一次~')
            return {"slot_phone_piece": None}
        if slot_phone_piece:
            print("validate_slot_phone_piece")
            if len(slot_phone_piece) == 11:
                dispatcher.utter_message(text= f'电话：{slot_phone_piece}')
                return {"slot_phone_piece": None}
            else:
                dispatcher.utter_message(text= f'电话：{slot_phone_piece}_')
                return {"slot_phone_piece": slot_phone_piece}


    # 验证运单号槽位
    def validate_slot_express_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot express_id."""
        print("--- validate slot express_id --->")
        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_value).upper()

        # 用户首句发送的是单号，需要回复一句问候语
        if self.is_first_in(tracker) and len(slot_express_id) == len(tracker.latest_message['text']):
            # resp_tools = global_config.RespTools()
            # dispatcher.utter_message(text=resp_tools.generate_resp_randomly(resp_tools.greet))
            # dispatcher.utter_message(response='utter_greet')
            dispatcher.utter_message(response='utter_help')

        # 单号验证
        if slot_express_id.isdigit():
            pre = ['YT', 'YTD', 'YTG', 'G']  # G开头的共12位，其他共15位
            for p in pre:
                slot_express_id = p+slot_express_id
                payload = json.dumps({"waybillNo": slot_express_id})
                headers = {'Content-Type': 'application/json'}
                response = requests.request("POST", self.check_url, headers=headers, data=payload)
                # validation succeeded
                if json.loads(response.text)['data']:
                    return {"slot_express_id": slot_express_id}
        else:
            payload = json.dumps({"waybillNo": slot_express_id})
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", self.check_url, headers=headers, data=payload)
            # validation succeeded
            if json.loads(response.text)['data']:
                return {"slot_express_id": slot_express_id}
        # 从跟踪器的metadata中获取运单号实体
        exp_id = tracker.latest_message.get("metadata").get("express_id")
        if exp_id:
            print("踪器的metadata中获取运单号---")
            return {"slot_express_id": exp_id}
        # validation failed
        dispatcher.utter_message(text="运单号不正确，麻烦您重新提供一下")
        return {"slot_express_id": None}

    # 手机号槽位抽取
    async def extract_slot_phone(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        # 从metadata抽取运单号
        print("--- extract slot phone --->")
        if not tracker.get_slot('slot_phone_collect'): return
        meta_phone = tracker.latest_message.get("metadata").get("phone")
        if meta_phone:
            print('meta phone:', meta_phone)
            return {"slot_phone": meta_phone}
        # 从metadata抽取运单号
        intent_latest = tracker.get_intent_of_latest_message()
        phone_piece = tracker.get_slot('slot_phone_piece')
        if phone_piece and len(phone_piece) == 11:
            print('extract phone:', phone_piece)
            return {"slot_phone": phone_piece}

        # if tem and intent_latest in ['inform', 'service_code']:
        #     print('tem_phone end:', tem)
        #     return {"slot_phone": tem}
        
    # 验证手机号槽位
    def validate_slot_phone(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot phone."""

        def validate_phone_number(number):
            pattern = r'^1[3-9]\d{9}$'
            return re.match(pattern, number) is not None
        print("--- validate slot phone --->")
        slot_phone = str(slot_value)

        # validation succeeded

        if validate_phone_number(slot_phone):
            return {"slot_phone": slot_phone}
        # 从跟踪器的metadata中获取电话实体
        p = tracker.latest_message.get("metadata").get("phone")
        if p:
            return {"slot_phone": p}
        # validation failed
        dispatcher.utter_message(text="电话号码不正确，麻烦您重新提供一下")
        return {"slot_phone": None}


if __name__ == '__main__':
    # 测试示例
    numbers = [
        "13812345678",  # 中国移动
        "18598765432",  # 中国联通
        "13355557777",  # 中国电信
        "19912345678",  # 中国电信
        "10000000000",  # 不合法号码
        "2819000910395",  # 不合法号码
        "343534",         # 不合法号码
        "YT324534",     # 不合法号码
        "19512265668",
        "12234567281"
    ]