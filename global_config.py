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
            '您好小圆正在查询中请耐心等待哦!',
            '您好因咨询量过大请耐心等待客服小姐姐已经在竭力查询了哦!',
            '稍等',
            '请稍等',
            '这边马上帮您查看一下请稍等'
        ]
        self.apologizes = [
            '非常抱歉给您带来不好的服务体验小圆表示深深的歉意',
            '非常抱歉确实给您添麻烦了',
            '亲对于因为物流给您带来的麻烦我们感到万分抱歉我会尽快为您解决问题。',
            '非常抱歉给您添麻烦了',
            '亲亲很抱歉的确是我们的工作没有做好给您带来不好的体验小圆在此再说声抱歉哦',
            '抱歉亲',
            '抱歉'
        ]
        self.registering = [
            '好哒亲我正在给您登记处理哦！请不要走开稍等哦',
            '亲亲请稍等片刻小圆为您登记中',
            '收到 亲亲正在给您登记处理哦您稍等',
            '稍等哈小圆在给您登记哦！',
            '好的亲正在登记请稍等',
            '小圆正在登记您的问题请稍等哦',
            '请稍等正在登记哦',
            '稍等给您登记',
            '请稍等 我这边正在帮您登记',
            '请不要离开这边正在帮您登记~~~',
            '亲亲这边正在帮您登记,请稍等片刻哦!',
            '请稍等 正在为您登记哦！',
            '请您稍等正在为您登记'
        ]
        self.appease = [
            '放心 既然找到小圆 一定给您处理好的呢',
            '亲我一定尽全力帮助您解决问题请您放心',
            '亲 请您放心我们会很重视您的问题 并尽快给您处理好的感谢您的理解',
            '知道您比较着急 小圆刚已让后台专员帮您加急优先处理了亲',
            '亲亲您的问题我已备注为“重要+紧急”网点优先先给你处理请放心专员会给你个满意的答复哦',
            '我这边追问站点人员核实一下是怎么回事核实好之后给您一个准确的答复',
            '这边给您对接专员核实网点具体原因尽快联系您给您一个结果',
            '亲小圆先核实下请相信我们一定会给您一个满意的答复。'
        ]
        self.urge = [
            '小圆帮您加急',
            '这就给您催促网点处理',
            '这边帮您催促',
            '好的亲小圆这边帮您加急催促',
            '这边小圆为您加急催促尽快送达哦亲',
            '帮您优先通知他们处理亲亲',
            '已经帮您催促了请耐心等候一下',
            '小圆帮您催促了',
            '这里给您加急催促一下亲亲',
        ]
        self.greet = [
            "您好, 请问有什么可以帮您",
            "您好, 亲亲",
            "您好，圆通速递很高兴为您服务。请问有什么可以帮到您？",
            "亲亲您好, 我是人工客服小圆, 很高兴为您服务。请问有什么能帮到您的吗?",
            "您好, 亲~",
            "您好 亲亲~",
            "您好,很高兴为您服务! 请问有什么可以帮您?",
            "亲您好! 圆通速递很高兴为您服务 请问有什么可以帮到您的?",
            "亲亲~您好!",
            "您好,很高兴为您服务! 请问有什么可以帮到您?",
            "亲亲, 小圆人工客服, 请问有什么可以帮您?",
            "请问有什么可以帮您?",
            "亲您好! 请问有什么可以帮您?"
            "您好很荣幸为您服务",
            "有什么可以帮您?",
            "您好圆通速递很高兴为您服务请问有什么可以帮您",
            "亲您好 请问有什么可以帮到您的呢",
            "您好亲亲 很高兴为您服务",
            "您好！很高兴为您服务。请问有什么可以帮您",
            "亲亲您好！很高兴为您服务, 请问有什么可以帮您",
            "亲 请问有什么可以帮您的吗?",
            "您好！很高兴为您服务请问 有什么可以帮您的?",
            "您好 很高兴为您服务请问 有什么可以帮您？",
            "您好亲！请问有什么可以帮到您吖~~",
            "亲 您好！",
            "您这边是什么问题呢 亲？",
            "您好 请问有什么可以帮您?",
            "您好 有什么可以帮您？",
            "你好 请问有什么可以帮您？",
            "您好 圆通快递很高兴为您服务！",
            "请问有什么可以帮您的 亲？",
            "亲亲 有什么可以帮到您的呢？",
            "您好 圆通速递很高兴为您服务！请问有什么可以帮到您？"
        ]

    def generate_resp_randomly(self, source_resp=None):
        if source_resp is None:
            return random.sample(self.please_wait+self.apologizes+self.appease+self.registering+self.urge, 1)[0]
        return random.sample(source_resp, 1)[0]
