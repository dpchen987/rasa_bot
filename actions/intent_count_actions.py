from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa.shared.core.domain import Domain
from rasa_sdk.executor import CollectingDispatcher

import logging

import sys
sys.path.append("..")
import global_config


# 对需要计数的意图进行计数，并将计数结果赋值给每个意图对于的计数槽位，以用于流程分支判断
class ActionIntentCount(Action):
    def name(self) -> Text:
        return "action_intent_count"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: "Domain",) -> List[Dict[str, Any]]:
        """Runs action. Please see parent class for the full docstring."""
        intent_dict = dict()
        # 催中转
        intent_dict['urge'] = 'urge'
        intent_dict['too_slow'] = 'urge'
        intent_dict['urge_to_process'] = 'urge'
        intent_dict['urge_to_send'] = 'urge'
        intent_dict['sup_urge'] = 'urge'
        intent_dict['ask_send_on_time'] = 'urge'
        intent_dict['add_money'] = 'urge'
        intent_dict['logistics_not_updated'] = 'urge'
        intent_dict['send_wrong_address'] = 'urge'
        intent_dict['has_not_received_yet'] = 'urge'
        intent_dict['hurry'] = 'urge'
        # 退回
        intent_dict['return'] = 'return'
        # 签收未收到
        intent_dict['pretend_signed'] = 'signed_but_not_received'
        intent_dict['has_not_received'] = 'signed_but_not_received'
        # 送货上门
        intent_dict['home_delivery'] = 'home_delivery'
        # 投诉
        intent_dict['complaint'] = 'complaint'
        intent_dict['complaint_logistics'] = 'complaint'
        intent_dict['complaint_courier'] = 'complaint'
        intent_dict['complaint_net_station'] = 'complaint'
        intent_dict['complaint_did_not_sent_to_doorstep'] = 'complaint'
        intent_dict['complaint_service'] = 'complaint'
        intent_dict['complaint_courier_station'] = 'complaint'
        intent_dict['complaint_customer_service'] = 'complaint'
        # 更址
        intent_dict['change_address'] = 'change_address'
        intent_dict['write_wrong_address'] = 'change_address'
        intent_dict['if_can_change_address'] = 'change_address'
        intent_dict['address_is_wrong'] = 'change_address'
        intent_dict['change_address_or_not'] = 'change_address'
        # 咨询发票
        intent_dict['consult_invoice'] = 'consult_invoice'
        # 生气-安抚
        intent_dict['angry'] = 'angry'
        intent_dict['threaten_complaint'] = 'angry'
        intent_dict['no_use'] = 'angry'
        intent_dict['swearing'] = 'swearing'
        intent_dict['grumble_logistics_net_courier'] = 'angry'
        intent_dict['not_accept_apology'] = 'angry'
        intent_dict['not_arrive_threaten_complaint'] = 'angry'
        intent_dict['not_process_threaten_complaint'] = 'angry'

        # 何时回复
        intent_dict['when_to_contact'] = 'when_to_contact'

        intent = str(tracker.latest_message.get('intent')['name'])

        if intent_dict.get(intent) is None:
            logging.warning('Intent map did not get current intent')
            return []
        # 根据计数意图名称拼接获取该意图对应的计数槽位
        count_name = 'slot_' + intent_dict.get(intent) + '_count'
        if tracker.get_slot(count_name) is None:
            logging.warning('Tracker did not get the intent to count')
            return []

        # 从跟踪器tracker中获取该意图计数槽位的值，然后再进行进行计数操作(加1)
        intent_count = int(tracker.get_slot(count_name)) + 1
        # 对意图计数槽位和意图计数判断两个槽位进行更新
        return [SlotSet(count_name, intent_count), SlotSet(f"{count_name}"+"_key", intent_count)]
