import sys
import logging
from typing import Any, Text, Dict, List
from pprint import pprint
from rasa_sdk import Action, Tracker
from rasa_sdk.events import (
    ActionExecuted,
    SlotSet,
    SessionStarted,
)
sys.path.append("..")



# 这个动作的作用是重置会话状态，也就是清除历史会话记录，就好像回到第一次访问机器人一样，需要注意的是，该动作不会清除那些诸如电话、运单号等关键槽位信息
class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    @staticmethod
    def _slot_set_events_from_tracker(
        tracker: Tracker,
    ):
        """Fetch SlotSet events from tracker and carry over key, value and metadata."""
        # print(tracker.applied_events())

        # for event in tracker.applied_events():
        #
        #     if event['event'] == 'slot' and event['name'] != 'requested_slot':
        #         # print(event)
        #         print('name', event['name'])
        #         print('value', event['value'])

        return [
            SlotSet(key=event['name'], value=event['value'])
            for event in tracker.applied_events()
            if event['event'] == 'slot' and event['name'] != 'requested_slot'
        ]

    def run(
      self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ):
        _events = [SessionStarted()]
        if domain['session_config']['carry_over_slots_to_new_session']:
            _events.extend(self._slot_set_events_from_tracker(tracker))

        # 在一个SenderId初次调用时,会获取后端传入的用户类型(user_type)、电话(phone)、运单号(express_id)等信息
        # Do something with the metadata
        metadata = tracker.get_slot("session_started_metadata")
        if metadata is not None:
            user_type = metadata.get('user_type', None)
            phone = metadata.get('phone', None)
            express_id = metadata.get('express_id', None)
            if user_type is not None:
                _events.append(SlotSet('slot_user_type', user_type))
            if phone is not None:
                _events.append(SlotSet('slot_phone', phone))
            if express_id is not None:
                _events.append(SlotSet('slot_express_id', express_id))
        else:
            logging.warning('metadata is None!')

        # 每次该动作都会将绝大多数影响会话的槽位进行初始化，目的是可以成功的切换到其他流程
        # initialize related slots
        if tracker.get_slot("slot_phone_key") != 0:
            _events.append(SlotSet("slot_phone_key", 0))
        if tracker.get_slot("slot_sign_status_key") != "onTheWay":
            _events.append(SlotSet("slot_sign_status_key", 'onTheWay'))
        if tracker.get_slot("slot_history_workorder_key") != "noWorkorder":
            _events.append(SlotSet("slot_history_workorder_key", 'noWorkorder'))
        if tracker.get_slot("slot_complaint_count_key") != 0:
            _events.append(SlotSet("slot_complaint_count_key", 0))
        if tracker.get_slot("slot_home_delivery_count_key") != 0:
            _events.append(SlotSet("slot_home_delivery_count_key", 0))
        if tracker.get_slot("slot_signed_but_not_received_count_key") != 0:
            _events.append(SlotSet("slot_signed_but_not_received_count_key", 0))
        if tracker.get_slot("slot_urge_count_key") != 0:
            _events.append(SlotSet("slot_urge_count_key", 0))
        if tracker.get_slot("slot_return_count_key") != 0:
            _events.append(SlotSet("slot_return_count_key", 0))
        if tracker.get_slot("slot_consult_invoice_count_key") != 0:
            _events.append(SlotSet("slot_consult_invoice_count_key", 0))
        if tracker.get_slot("slot_change_address_count_key") != 0:
            _events.append(SlotSet("slot_change_address_count_key", 0))
        if tracker.get_slot("slot_angry_count_key") != 0:
            _events.append(SlotSet("slot_angry_count_key", 0))
        if tracker.get_slot("slot_swearing_count_key") != 0:
            _events.append(SlotSet("slot_swearing_count_key", 0))
        if tracker.get_slot("slot_phone_latest_key") != 0:
            _events.append(SlotSet("slot_phone_latest_key", 0))
        if tracker.get_slot("slot_express_id_latest_key") != 0:
            _events.append(SlotSet("slot_express_id_latest_key", 0))
        if tracker.get_slot("slot_when_to_contact_count_key") != 0:
            _events.append(SlotSet("slot_when_to_contact_count_key", 0))
        if tracker.get_slot("slot_confirm_key") != 1:
            _events.append(SlotSet("slot_confirm_key", 1))
        if tracker.get_slot("slot_complaint_key") != 0:
            _events.append(SlotSet("slot_complaint_key", 0))
        if tracker.get_slot("slot_user_type_key") != "收件人":
            _events.append(SlotSet("slot_user_type_key", '收件人'))
        if tracker.get_slot("slot_core_intent_key") != "no_intent":
            _events.append(SlotSet("slot_core_intent_key", 'no_intent'))
        if tracker.get_slot("slot_check_weight_key") != 0:
            _events.append(SlotSet("slot_check_weight_key", 0))
        if tracker.get_slot("slot_order_id_latest_key") != 0:
            _events.append(SlotSet("slot_order_id_latest_key", 0))
        if tracker.get_slot("slot_hurry_key") != 0:
            _events.append(SlotSet("slot_hurry_key", 0))
        if tracker.get_slot("slot_is_receiver_key") != "no_intent":
            _events.append(SlotSet("slot_is_receiver_key", 'no_intent'))
        if tracker.get_slot("slot_ask_comments_key") != 0:
            _events.append(SlotSet("slot_ask_comments_key", 0))
        if tracker.get_slot("slot_jt_express_key") != 0:
            _events.append(SlotSet("slot_jt_express_key", 0))
        if tracker.get_slot("slot_sf_express_key") != 0:
            _events.append(SlotSet("slot_sf_express_key", 0))
        if tracker.get_slot("slot_zt_express_key") != 0:
            _events.append(SlotSet("slot_zt_express_key", 0))
        if tracker.get_slot("slot_st_express_key") != 0:
            _events.append(SlotSet("slot_st_express_key", 0))
        if tracker.get_slot("slot_yd_express_key") != 0:
            _events.append(SlotSet("slot_yd_express_key", 0))
        if tracker.get_slot("slot_yz_express_key") != 0:
            _events.append(SlotSet("slot_yz_express_key", 0))
        if tracker.get_slot("slot_bs_express_key") != 0:
            _events.append(SlotSet("slot_bs_express_key", 0))
        if tracker.get_slot("slot_db_express_key") != 0:
            _events.append(SlotSet("slot_db_express_key", 0))
        if tracker.get_slot("slot_jd_express_key") != 0:
            _events.append(SlotSet("slot_jd_express_key", 0))
        if tracker.get_slot("slot_unable_contact_key") != 1:
            _events.append(SlotSet("slot_unable_contact_key", 1))
        if tracker.get_slot("slot_express_id_form_max_count") != 0:
            _events.append(SlotSet("slot_express_id_form_max_count", 0))

        # 最后需要添加action_listen事件，以监听外界的输入
        _events.append(ActionExecuted('action_listen'))
        # the session should begin with a `session_started` event and an `action_listen`
        # as a user message follows

        return _events


