from typing import Any, Text, Dict, List
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from global_config import intent_map


# 该动作针对后续不需要登记的意图，利用辅助词槽进行标记
class ActionConfirmSet(Action):
    def name(self) -> Text:
        return "action_confirm_set"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet('slot_confirm', 0)]


# 该动作给核心意图词槽“slot_core_intent”进行赋值，该词槽用于后续流程分支的判断
class ActionSetSlotCoreIntent(Action):
    def name(self) -> Text:
        return "action_set_slot_core_intent"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 从跟踪器tracker中获取最新的外界输入对应的意图
        last_intent = tracker.get_intent_of_latest_message()
        if last_intent not in intent_map:
            return []

        # 将上述获取到的意图映射到标准核心意图
        core_intent = intent_map.get(last_intent)

        if core_intent == 'return':
            return [SlotSet('slot_core_intent', 'return')]
        if core_intent == 'change_address':
            return [SlotSet('slot_core_intent', 'change_address')]
        if core_intent == 'inform':
            return [SlotSet('slot_core_intent', 'inform')]
        if core_intent == 'check_express_status':
            return [SlotSet('slot_core_intent', 'check_express_status')]

        return []


# 该动作为在流程中有引导结束话术的地方设置一个标记，将引导结束标记槽位“slot_guide_to_end”赋值，该槽位将用于后续流程分支的判断
class ActionSetSlotGuideToEnd(Action):
    def name(self) -> Text:
        return "action_set_slot_guide_to_end"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("slot_guide_to_end", 1)]


# 该动作为在流程中有要好评的地方设置一个标记，将要好评标记槽位“slot_ask_comments”赋值，该槽位将用于后续流程分支的判断
class ActionSetSlotAskComments(Action):
    def name(self) -> Text:
        return "action_set_slot_ask_comments"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet("slot_ask_comments", 1)]