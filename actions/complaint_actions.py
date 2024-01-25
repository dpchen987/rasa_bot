from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# 该动作主要作用是根据投诉所处的上下文，来对投诉槽位“slot_complaint_key”进行赋值，该槽位会用于后续流程的判断
class ActionConfirmSet(Action):
    def name(self) -> Text:
        return "action_complaint"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        has_context = 0
        if tracker.get_slot('slot_core_intent') not in ["no_intent", "inform", "check_weight", "consult"]:
            has_context = 1
        return [SlotSet("slot_complaint_key", has_context)]