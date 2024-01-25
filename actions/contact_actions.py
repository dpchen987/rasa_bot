from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


# 该动作会将更址和退回的计数槽位值分别进行赋值，目的是判断上文是更址还是退回
class ActionChangeAddress(Action):
    def name(self) -> Text:
        return "action_contact"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_change_address_count, slot_return_count_key = tracker.get_slot('slot_change_address_count'), tracker.get_slot('slot_return_count')
        # 两个值都为零，说明前面没有更址或退回的意图
        if slot_change_address_count == 0 and slot_return_count_key == 0:
            cur_intent = tracker.get_intent_of_latest_message()
            if cur_intent and cur_intent in ["ask_to_contact", "has_contacted", "cannot_contact_seller"]:
                return [SlotSet('slot_unable_contact_key', 1)]
            elif cur_intent in ["unable_to_contact"]:
                return [SlotSet('slot_unable_contact_key', 2)]
        else:
            # 更址意图计数槽位“slot_change_address_count_key”和退回意图计数槽位“slot_return_count_key”，两者的作用均是用于后续流程的判断
            return [SlotSet('slot_change_address_count_key', tracker.get_slot('slot_change_address_count')),
                SlotSet('slot_return_count_key', tracker.get_slot('slot_return_count'))]
