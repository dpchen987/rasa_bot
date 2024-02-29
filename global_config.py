# -*- coding:utf-8 -*-

import logging
import random

logging.basicConfig(filename='../actions.log',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.WARNING)

# web url
# WEB_URL = "http://wdgj-chatbot-inter.yto56.com.cn:18990/"        # 生产环境
# WEB_URL = "http://10.7.36.141:18991/"                            # 生产环境，可视化版本
WEB_URL = "http://10.130.10.210:18990/"                          # 测试环境

intent_map = dict()
# 催中转
intent_map['urge'] = 'urge'
intent_map['too_slow'] = 'urge'
intent_map['urge_to_process'] = 'urge'
intent_map['urge_to_send'] = 'urge'
intent_map['sup_urge'] = 'urge'
intent_map['ask_send_on_time'] = 'urge'
intent_map['add_money'] = 'urge'
intent_map['logistics_not_updated'] = 'urge'
intent_map['send_wrong_address'] = 'urge'
intent_map['has_not_received_yet'] = 'urge'
intent_map['hurry'] = 'urge'
# 退回
intent_map['return'] = 'return'
intent_map['return_or_not'] = 'return'
# 更址
intent_map['change_address'] = 'change_address'
intent_map['write_wrong_address'] = 'change_address'
intent_map['if_can_change_address'] = 'change_address'
intent_map['address_is_wrong'] = 'change_address'
intent_map['change_address_or_not'] = 'change_address'
# 预计到达时间
intent_map['check_arrive_datetime'] = 'check_arrive_datetime'
# 查件
intent_map['no_logistics_info'] = 'check_express_status'
intent_map["check_express_status"] = 'check_express_status'
intent_map['has_sent_or_not'] = 'check_express_status'
intent_map["pretend_sent"] = 'check_express_status'
intent_map['if_has_lost'] = 'check_express_status'
# 签收未收到
intent_map['has_not_received'] = 'signed_but_bot_received'
intent_map['pretend_signed'] = 'signed_but_bot_received'
# 送货上门
intent_map['home_delivery'] = 'home_delivery'
# 催取件
intent_map['urge_to_get_express'] = 'urge_to_get_express'
# 登记
intent_map['urge_to_send_goods'] = 'register'
intent_map['specify_method_himself'] = 'register'
intent_map['specify_method_not_courier_station'] = 'register'
intent_map['request_sent_to_delivery_cabinet'] = 'register'
intent_map['specify_method_not_him_want_address'] = 'register'
intent_map['request_to_contact_via_phone'] = 'register'
intent_map['request_to_register'] = 'register'
intent_map['consult_exception_reason'] = 'register'
intent_map['cancel_to_send'] = 'register'
intent_map['ask_code'] = 'register'
intent_map['ask_damages'] = 'register'
intent_map['package_damage'] = 'register'
intent_map['package_lack'] = 'register'
intent_map['package_lost'] = 'register'
intent_map['reject_reason'] = 'register'
# 生气
intent_map['angry'] = 'angry'
intent_map['grumble_logistics_net_courier'] = 'angry'
intent_map['no_use'] = 'angry'
intent_map['threaten_complaint'] = 'angry'
intent_map['swearing'] = 'swearing'
intent_map['not_accept_apology'] = 'angry'
intent_map['not_arrive_threaten_complaint'] = 'angry'
intent_map['not_process_threaten_complaint'] = 'angry'
# 投诉
intent_map['complaint'] = 'complaint'
intent_map['complaint_logistics'] = 'complaint'
intent_map['complaint_courier'] = 'complaint'
intent_map['complaint_net_station'] = 'complaint'
intent_map['complaint_did_not_sent_to_doorstep'] = 'complaint'
intent_map['complaint_service'] = 'complaint'
intent_map['complaint_courier_station'] = 'complaint'
intent_map['complaint_customer_service'] = 'complaint'
# 咨询
intent_map['consult_station_info'] = 'consult'
intent_map['consult_send_item'] = 'consult'
intent_map['consult_send_station_info'] = 'consult'
intent_map['consult_post_info'] = 'consult'
intent_map['consult_expressman_phone'] = 'consult'
intent_map['consult_invoice'] = 'consult'
# inform
intent_map['inform'] = 'inform'
# check_weight
intent_map['check_weight'] = 'check_weight'
# faq intent
intent_map['did_not_contact_customer'] = 'faq_intent'
intent_map['unable_to_contact_courier'] = 'faq_intent'
intent_map['unable_to_contact_net_station'] = 'faq_intent'

# 需要个性化回复已登记话术的意图数组
intent_list = list()

# 判断从后端返回的数据格式是否存在问题，以及问题的种类
def resp_has_exception(d):
    if not isinstance(d, dict):
        return 3
    if d['status'] != 0:
        return 2
    if d.get('data') is None or not d['data']:
        return 1

    return None


class RespTools:
    def __init__(self):
        self.please_wait = [
            '您好，这边正在查询中，请耐心等待',
            '请稍等',
            '这边马上帮您查看一下，请稍等'
        ]
        self.apologizes = [
            '非常抱歉，给您带来不好的服务体验',
            '因为物流给您带来的麻烦我们感到非常抱歉，我会尽快为您解决问题。',
        ]
        self.registering = [
            '稍等一下，我正在给您登记处理哦！请不要挂机',
            '请稍等片刻这边为您登记中',
            '收到 正在给您登记处理，您稍等',
            '这边正在帮您登记,请稍等片刻哦!',
        ]
        self.appease = [
            '这边一定尽力帮您解决问题，请您放心',
            '请您放心我们会很重视您的问题 并尽快给您处理好的感谢您的理解',
            '您的问题我已备注为“重要+紧急”网点优先先给你处理请放心专员会给你个满意的答复哦',
            '这边给您对接专员核实网点具体情况，会尽快联系您',
        ]
        self.urge = [
            '好的，这边已经帮您做了加急处理',
            '帮您优先通知他们处理',
            '已经帮您催促了，请耐心等候一下',
        ]
        self.greet = [
            "您好，圆通速递，很高兴为您服务。请问有什么可以帮到您？",
            "您好, 这里是圆通快递客服中心, 很高兴为您服务。请问有什么能帮到您的吗?",
            "您好! 这里是圆通快递客服中心, 请问有什么可以帮您?"
            "您好 圆通快递，很高兴为您服务！",
        ]

    def generate_resp_randomly(self, source_resp=None):
        if source_resp is None:
            return random.sample(self.please_wait+self.apologizes+self.appease+self.registering+self.urge, 1)[0]
        return random.sample(source_resp, 1)[0]
