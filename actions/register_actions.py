from typing import Any, Text, Dict, List
import json
import requests
import logging

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

import sys
sys.path.append("..")
from global_config import WEB_URL, intent_map, intent_list


class ActionRegister(Action):
    """登记流程-根据意图出相应的已登记话术"""

    def name(self) -> Text:
        return "action_register"

    def __init__(self):
        self.url = WEB_URL + 'wdgj-chatbot-server/waybillInfo/checkUnFinshWork'

    # 判断跟踪器tracker中是否有运单号
    def has_workorder(self, dispatcher: CollectingDispatcher, tracker: Tracker):
        # 从跟踪器tracker中获取“运单号槽位”的值
        slot_express_id = tracker.get_slot('slot_express_id')
        if not slot_express_id:
            logging.warning("Express id is None!")
            return False

        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_express_id).upper()
        payload = json.dumps({"phone": tracker.get_slot('slot_phone'), "waybillNo": slot_express_id})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        if not isinstance(response, dict):
            dispatcher.utter_message(json_message={"story": "register", "api_exception": 3})
            logging.warning(" API exception occurred!")
            return False

        if response['status'] != 0:
            dispatcher.utter_message(json_message={"story": "register", "api_exception": 2})
            logging.warning(" API exception occurred!")
            return False

        if response['data']:
            dispatcher.utter_message(json_message={"story": "register"})
            return True

        # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(json_message={"story": "register"})
        return False

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 告知已登记
        dispatcher.utter_message(response='utter_register_is_signing')
        dispatcher.utter_message(response='utter_register_has_signed_base')
        # 马上去处理。与告知已登记可以二选一，也可以都用
        # slot_core_intent = tracker.get_slot('slot_core_intent')
        # if intent_map.get(slot_core_intent) is not None and \
        #         'utter_'+intent_map.get(slot_core_intent)+'_reply' in intent_list:
        #     dispatcher.utter_message(response='utter_'+intent_map.get(slot_core_intent)+'_reply')
        # else:
        #     dispatcher.utter_message(response='utter_register_to_process_now')
        # 是否还有别的问题，根据是否有运单号出不同的引导结束话术
        if self.has_workorder(dispatcher, tracker):
            dispatcher.utter_message(response='utter_guide_to_end_has_workorder')
        else:
            dispatcher.utter_message(response='utter_guide_to_end')

        # 对标记引导结束槽位“slot_guide_to_end”进行赋值
        return [SlotSet("slot_guide_to_end", 1)]