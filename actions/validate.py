import requests
import json
from typing import Text, Any, Dict
import re
import random

from rasa_sdk import Tracker, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import sys
sys.path.append("..")
import global_config


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

    # 验证运单号槽位
    def validate_slot_express_id(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate slot express_id."""

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
            return {"slot_express_id": exp_id}

        # validation failed
        utter_messages = ["亲，这个运单号不正确哦",
                          "亲，这边看到您提供的单号不对哦",
                          "您提供的单号不对哦 亲",
                          "亲，您提供的运单号不对哦"]
        dispatcher.utter_message(text=random.sample(utter_messages, 1)[0])
        return {"slot_express_id": None}

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
            pattern = r'^1[3456789]\d{9}$'
            return re.match(pattern, number) is not None

        slot_phone = str(slot_value)

        # validation succeeded

        if validate_phone_number(slot_phone):
            return {"slot_phone": slot_phone}
        # 从跟踪器的metadata中获取电话实体
        p = tracker.latest_message.get("metadata").get("phone")
        if p:
            return {"slot_phone": p}
        # validation failed
        utter_messages = ["亲，您提供的电话号码不正确，麻烦重新提供一下呢",
                          '亲，您提供的电话号码不对，麻烦重新提供一下呢',
                          '亲，这边看到您提供的电话号码不对哦。麻烦重新提供一下呢',
                          "您提供的电话号码有误亲，麻烦重新提供一下呢"]
        dispatcher.utter_message(text=random.sample(utter_messages, 1)[0])
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

    for number in numbers:
        if validate_phone_number(number):
            print(f"{number} 是一个合法的手机号码")
        else:
            print(f"{number} 不是一个合法的手机号码")