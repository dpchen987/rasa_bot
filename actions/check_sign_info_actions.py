import json
import requests
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


import logging

import sys
sys.path.append("..")
import deploy_config

# 该动作调用后端接口来查询签收信息
class ActionCheckSignInfo(Action):
    """用户查询签收信息"""

    def name(self) -> Text:
        return "action_check_sign_info"

    def __init__(self):
        self.url = deploy_config.WEB_URL + '/wdgj-chatbot-server/intention/utter/querySignInfo'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # test
        dispatcher.utter_message(text='签收信息查询')
        return []
        # 从跟踪器tracker中获取“运单号槽位”的值
        slot_express_id = tracker.get_slot('slot_express_id')
        if not slot_express_id:
            logging.error('slot express id is None!')
            return []

        # 将运单号中的字母转化为大写以适配后端接口规则
        slot_express_id = str(slot_express_id).upper()
        payload = json.dumps({"waybillNo": slot_express_id})
        headers = {'Content-Type': 'application/json'}
        response = json.loads(requests.request("POST", self.url, headers=headers, data=payload).text)

        # 对后端返回的数据内容格式进行判断，进而返回对应的状态值，后续会根据状态值进行判断并返回对应的值
        status = deploy_config.resp_has_exception(response)
        # 对该流程进行分类，供自动登记工单中的大小类自动识别使用
        dispatcher.utter_message(json_message={"story": "check_sign_info", "api_exception": status})

        if status == 2 or status == 3:
            logging.error('API exception occurred!')
            return []
        if status == 1:
            logging.error('API response is None')
            return []
        # 从后端查询的信息如果不为空则将该信息传递到调度台dispatcher以供机器人输出
        messages = response['data']['messages']
        for message in messages:
            utter_message = message['utterMessage']
            if not utter_message or len(utter_message) == 0:
                continue
            dispatcher.utter_message(text=utter_message)

        return []