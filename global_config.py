# -*- coding:utf-8 -*-

# rasa source configure
CORPUS_DICT_PATH = 'corpus_dict.json'
RESERVED_SLOTS_LIST = ["slot_express_id", "slot_name", "slot_phone", "slot_user_type", "slot_item",
                       "slot_from_address", "slot_normal_address", "slot_invoice_type", "slot_express_id_piece",
                       "slot_phone_piece", "slot_gender", "slot_big_category", "slot_small_category", "slot_work_type", 
                       "slot_item_price", "slot_delivery_address", "slot_hello", "slot_nice_to_serve", "slot_can_i_help",
                       "slot_expose_abnormal", "slot_thanks"]
FAQ = "faq"
NO_SCRIPT_INTENT = ['angry','ask_damages','cancel_to_send','change_address_or_not','check_sign_info',
                    'delivery_address_required','faq_consult_how_to_send_item','faq_consult_send_item_door_pickup',
                    'faq_consult_want_send_item','grumble_logistics_net_courier','has_sent_or_not','hurry',
                    'incorrect_language','inform','input_servicer','is_ok','is_ok_thanks','is_ok_urge','is_receiver','is_sender',
                    'item_price_required','no_use','not_accept_apology','not_arrive_threaten_complaint',
                    'not_process_threaten_complaint','phone_number_required','predict_call_end','pretend_sent',
                    'reject_reason','threaten_complaint','useless_intent']
PREDICTION_LOOP_TIMEOUT = 0.3

CUSTUMER_INTENT_LS = []
SERVICER_INTENT_LS = ["input_servicer","predict_call_end","phone_number_required","item_price_required","delivery_address_required",
                      "incorrect_language","guide_upgrade_intention",]
