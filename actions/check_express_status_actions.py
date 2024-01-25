# This files contains your custom actions which can be used to run
# custom Python code.
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import json
import requests
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import logging
from datetime import datetime

import sys
sys.path.append("..")
import global_config

# 该动作调用后端接口来进行查件
class CheckExpressStatusAction(Action):
    """查件流程"""

    def name(self) -> Text:
        return "action_check_express_status"

    def __init__(self):
        self.url = global_config.WEB_URL + 'wdgj-chatbot-server/intention/utter/queryUrgeTraceNew'

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
        status = global_config.resp_has_exception(response)
        # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(json_message={"story": "check_express_status", "api_exception": status})

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
            return [SlotSet('slot_core_intent', tracker.get_intent_of_latest_message())]
        if register_or_not == 0:
            return [SlotSet('slot_core_intent', tracker.get_intent_of_latest_message()),
                    SlotSet('slot_confirm', 0)]

        return []


if __name__ == "__main__":
    a = CheckExpressStatusAction()
