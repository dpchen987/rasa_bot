import json
import requests
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import logging

import sys
sys.path.append("..")
import global_config

# 该动作调用后端接口来查询有无历史工单
class ActionGetHistoryWorkorder(Action):
    """查询工单子流程"""

    def name(self) -> Text:
        return "action_check_workorder"

    def __init__(self):
        self.url = global_config.WEB_URL+'wdgj-chatbot-server/waybillInfo/checkUnFinshWork'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # test
        dispatcher.utter_message(text='历史工单查询')
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

        if not isinstance(response, dict):
            dispatcher.utter_message(json_message={"api_exception": 3})
            logging.error('API exception occurred!')
            return []

        if response['status'] != 0:
            dispatcher.utter_message(json_message={"api_exception": 2})
            logging.error('API exception occurred!')
            return []

        # 如果后端接口返回有值，则将历史工单槽位“slot_history_workorder_key”赋值为“hasWorkorder”，否则赋值为初始值“noWorkorder”
        # 对于主要流程中的意图，需要将该意图赋值给核心意图槽位“slot_core_intent”，以用于后续流程的判断
        if response['data']:
            return [SlotSet('slot_history_workorder_key', 'hasWorkorder'),
                   SlotSet('slot_core_intent', tracker.get_intent_of_latest_message())]
        else:
            return [SlotSet('slot_history_workorder_key', 'noWorkorder'),
                   SlotSet('slot_core_intent', tracker.get_intent_of_latest_message())]
