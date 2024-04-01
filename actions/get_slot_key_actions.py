from typing import Any, Text, Dict, List

from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import global_config


# 该动作将登记标记槽位“slot_confirm_key”和要好评话术标记槽位“slot_ask_comments_key”分别赋值，以供后续流程判断使用
class ActionConfirmGet(Action):
    def name(self) -> Text:
        return "action_confirm_get"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet('slot_confirm_key', tracker.get_slot('slot_confirm')),
                SlotSet("slot_ask_comments_key", tracker.get_slot("slot_ask_comments"))]  # 用法完全一样，没必要执行2个action


# 该动作获取核心流程意图，并赋值给核心意图标记槽位“slot_core_intent_key”，以用于后续流程的判断
class ActionGetSlotCoreIntent(Action):
    def name(self) -> Text:
        return "action_get_slot_core_intent_key"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        return [SlotSet('slot_core_intent_key', tracker.get_slot('slot_core_intent'))]


# 该动作给收件人流程判断槽位“slot_is_receiver_key”赋值，赋值依据是上一个核心流程的名称，该判断槽位供后续“我是收件人”流程进行分支判断
class ActionGetSlotIsReceiverKey(Action):
    def name(self) -> Text:
        return "action_get_slot_is_receiver_key"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 从跟踪器tracker中获取核心意图槽位，并将该值映射到global_config标准核心意图
        slot_core_intent = tracker.get_slot('slot_core_intent')
        slot_core_intent = global_config.intent_map.get(slot_core_intent)
        if slot_core_intent is None:
            return [SlotSet("slot_is_receiver_key", 'no_intent')]
        if slot_core_intent == "check_weight":
            return [SlotSet("slot_is_receiver_key", 'check_weight')]
        if slot_core_intent == "return":
            return [SlotSet("slot_is_receiver_key", 'return')]
        if slot_core_intent == "change_address":
            return [SlotSet("slot_is_receiver_key", 'change_address')]


# 该动作对加急判断槽位“slot_hurry_key”进行赋值，赋值依据是前文有无引导结束话术，供后续加急(hurry)流程进行分支判断
class ActionGetSlotHurryKey(Action):
    def name(self) -> Text:
        return "action_get_slot_hurry_key"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_guide_to_end = tracker.get_slot("slot_guide_to_end")
        if slot_guide_to_end:
            return [SlotSet("slot_hurry_key", 1)]

        return []


# 该动作对用户类型判断槽位“slot_user_type_key”进行赋值，使用用户类型槽位“slot_user_type”赋值，供后续相关流程进行分支判断
class ActionSlotUserTypeKey(Action):
    def name(self) -> Text:
        return "action_slot_user_type_key"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_user_type_key = tracker.get_slot("slot_user_type")
        if slot_user_type_key:
            return [SlotSet("slot_user_type_key", slot_user_type_key)]

        return []


# 该动作对有无电话槽位“slot_phone_key”进行赋值，使用电话槽位“slot_phone”赋值，供后续相关流程进行分支判断
class ActionSetSlotPhoneKey(Action):
    def name(self) -> Text:
        return "action_set_slot_phone_key"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_phone_key = tracker.get_slot("slot_phone")
        if slot_phone_key:
            return [SlotSet("slot_phone_key", 1)]

        return []


# 对inform意图下的实体赋值给对于的槽位，以用于后续流程的判断
class ActionSetInformKey(Action):
    def name(self) -> Text:
        return "action_set_inform_key"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.latest_message.get('intent').get('name')
        from pprint import pprint
        # pprint(tracker.latest_message)
        # pprint(tracker.events)
        entities = tracker.latest_message.get('entities')
        events = tracker.events
        if tracker.get_slot('slot_express_id'):
            # 判断轮次是否有运单号收集完成
            for evt in reversed(events):
                if evt['event'] == 'user': break
                if evt['event'] == 'slot' and evt['name'] == 'slot_express_id':
                    return [SlotSet("slot_express_id_latest_key", 1)]
                
        if intent not in ['inform', 'other_express'] or len(entities) == 0:
            return []
        for ent in entities:
            if ent.get('entity') is not None:
                if ent.get('entity') == 'phone':
                    return [SlotSet("slot_phone_latest_key", 1), SlotSet("slot_phone", ent.get('value'))]
                if ent.get('entity') == 'express_id':
                    return [SlotSet("slot_express_id_latest_key", 1), SlotSet("slot_express_id", ent.get('value'))]
                if ent.get('entity') == 'order_id':
                    return [SlotSet("slot_order_id_latest_key", 1), SlotSet("slot_order_id", ent.get('value'))]
                if ent.get('entity') == 'entity_jt_express_name' or ent.get('entity') == 'entity_jt_express_id':
                    return [SlotSet("slot_jt_express_key", 1)]
                if ent.get('entity') == 'entity_sf_express_name' or ent.get('entity') == 'entity_sf_express_id':
                    return [SlotSet("slot_sf_express_key", 1)]
                if ent.get('entity') == 'entity_zt_express_name' or ent.get('entity') == 'entity_zt_express_id':
                    return [SlotSet("slot_zt_express_key", 1)]
                if ent.get('entity') == 'entity_st_express_name' or ent.get('entity') == 'entity_st_express_id':
                    return [SlotSet("slot_st_express_key", 1)]
                if ent.get('entity') == 'entity_yd_express_name' or ent.get('entity') == 'entity_yd_express_id':
                    return [SlotSet("slot_yd_express_key", 1)]
                if ent.get('entity') == 'entity_jd_express_name' or ent.get('entity') == 'entity_jd_express_id':
                    return [SlotSet("slot_jd_express_key", 1)]
                if ent.get('entity') == 'entity_yz_express_name' or ent.get('entity') == 'entity_yz_express_id':
                    return [SlotSet("slot_yz_express_key", 1)]
                if ent.get('entity') == 'entity_db_express_name' or ent.get('entity') == 'entity_db_express_id':
                    return [SlotSet("slot_db_express_key", 1)]
                if ent.get('entity') == 'entity_bs_express_name' or ent.get('entity') == 'entity_bs_express_id':
                    return [SlotSet("slot_bs_express_key", 1)]

        return []