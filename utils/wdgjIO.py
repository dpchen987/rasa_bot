import re, os
import asyncio
import structlog
import inspect
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
import json, copy
import time
import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)
from .logging import logger
# logger = structlog.getLogger(__name__)

x_ge_y_pat = re.compile(r"[1-6一二两三四五六]个[\d 零令林一幺妖二两三四五六七八九]")
numbers_dict = {" ": "", "零": "0", "令": "0", "林": "0", "一": "1", "幺": "1", "妖": "1",  "二": "2", "两": "2", "三": "3", "四": "4","五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}   
yt_rep_pat = re.compile(r"[yY] {,3}7")
incrt_lang_pat = re.compile(r"[你他][妈]|神经|变态|[傻呆妈][逼bB蛋]|妈.{,4}[逼的]|[有毛]病|我[操靠草日]|[操日].{,3}[你他妈]|[滚猪狗贱瞎聋傻嫖]|什么玩意|人渣|不要脸|狗日|算什么东西|闭嘴|没.{,3}脑子|智障|废话|更年期|你大爷|[瞎胡]扯|"
                            r"无[聊语]|恶心|[气去]死|倒霉|md|没.{,3}[眼耳脑]|[眼耳脑听].{,3}[坏病问题]|[眼耳脑].{,3}干.{,3}用|嘴.{,3}干净|[真太好]烦|活该|正常.{,3}[都可能].{,4}理解|[说讲]人话|问候.{,3}全家|大爷.{,7}资格")
guide_upgrade_pat = re.compile(r"邮.{,3}[政局]|123[104]5|消.{,5}协|市民热线|监管部门|媒体|报道|举报|曝光|第三方.{,5}投诉|(?:其他|别的).{,2}(?:渠道|地方|方式).{,3}投诉|升级|第三方")
guide_upgrade_skip_pat = re.compile(r"不是.{,5}(?:我|圆通)|[您你][^可]{,3}[这快递][^可]{,3}邮政的|(?:我|这边).{,3}[给帮][你您]|[给帮][你您].{,3}(?:升级|投诉)")
customer_be_threatened_pat = re.compile(r"恐吓.{,3}我|威胁.{,3}我|[搞弄].{,3}我|[要叫让说].{,3}晚上.{,3}[不别].{,3}[出门]|[揍打骂抱摸]我|自杀|强[奸暴]|偷窥|调戏")
upgrade_intention_pat = re.compile(r"邮.{,3}[政局]|123[104]5|315|消.{,5}协|市民热线|监管部门|媒体|报道|举报|曝光|第三方.{,5}投诉|(?:其他|别的).{,2}(?:渠道|地方|方式).{,3}投诉|"
                                   r"新闻|记者|报社|栏目组|微博|朋友圈|起诉|升级|管理部门|报[案警]|法院")
customer_praise_pat = re.compile(r"(?:我|怎么|方[式法]|途径)[^不]{,3}表扬你|给你?.{,3}(?:好评|赞)|(?:我|怎么|方[式法]|途径)[^不]{,3}好评|表扬你|好评")
response_untimely_pat = re.compile(r"[不别].{,3}静音|在.{,5}吗|有没有.{,3}听|能不能.{,3}听|听.{,5}了[吗没么嘛]|[能有]听.{,6}[吧么嘛吗]|[问跟]你{,3}[呢说话]|人.{,3}呢|[说讲].{,2}[话呀啊]|不[说讲].{,2}话|[怎什么啥咋].{,3}不.{,2}[说讲话答]|"
                                   r"回[话答复]|客服.{,3}[呢在哪]|[有没].{,2}人.{,3}[吗么嘛不吧]|在.{,3}[啥什吗么嘛不吧]|在不在")
response_untimely_skip_pat = re.compile(r"听.{,3}[到见清楚]|你们|他|快递|业务员|客服|[网站签收派送转]|登记|反馈|其他|上报")
interrupt_speech_pat = re.compile(r"(?:不要|别).{,2}[说讲插抢].{,2}[话嘴]|(?:不要|别).{,2}打断|[插抢]我.{,2}话|你.{,2}[插抢]话|我.{,2}没.{,2}[说讲]完|能.{,2}[让听]我.{,2}[说讲].{,2}[吗么嘛]|[让听]我.{,3}[说讲]|[你我]说还是.{,2}[你我]说|"
                                  r"能不能.{,5}[听]|我.{,5}[说讲]完.{,2}了[吗么嘛]|闭嘴")
interrupt_speech_skip_pat = re.compile(r"听.{,3}[到见清楚]|你们|他|快递|业务员|客服|[网站签收派送转]|登记|反馈|其他|上报")
understand_insufficiently_pat = re.compile(r"你.{,3}新[人来]|你.{,5}(?:理解|能力).{,5}问题|你.{,3}[没不].{,3}(?:理解|懂|明白|[搞弄]清|清楚|明确)|我.{,3}[没不].{,3}(?:理解|懂|明白|[搞弄]清|清楚|明确).{,3}你.{,3}[说讲答]|你.{,3}到底.{,3}(?:理解?[不没]理解|清楚?不清楚|知道?不知道|懂[不没]懂)|"
                                           r"你.{,3}(?:回答|[说讲]).{,3}不是我.{,3}[想问要意思]|我.{,3}不.{,3}[说讲]过|[说讲告你].{,3}[多几十百].{,3}遍|你.{,3}培训.{,3}[了没吗吧]|你.{,3}[不没].{,3}培训|你.{,3}这.{,3}水平|你.{,3}登记好.{,3}[没吗么嘛吧]|答非所问|都.{,3}[和跟]你.{,3}说了|你.{,3}干什么.{,3}的|干什么.{,3}的你")
understand_insufficiently_skip_pat = re.compile(r"听.{,3}[到见清楚]|你们|他|快递员|业务员|客服")
perfunctory_attitude_pat = re.compile(r"你.{,5}[什么就这啥].{,5}态度|有气无力|没睡[觉醒]|你.{,5}态度.{,3}[能可].{,3}好|[能可].{,5}态度.{,3}好|[你我].{,3}是.{,3}客服|不是我.{,3}你.{,3}解决|是你.{,13}不是我|你.{,3}复读机|你.{,3}机器人|给.{,10}干[啥什嘛]|"
                                      r"[你少别].{,7}敷衍|[你少别].{,7}抬杠|你.{,7}过分|你.{,7}消极|开.{,5}玩笑|你.{,3}是.{,3}客服|你.{,5}态度.{,3}[不好恶劣太差垃圾有点些问题]|好好[说讲]话|[能会].{,5}[说讲]话|[说讲]话.{,5}[能会][不吗么嘛]")
perfunctory_attitude_skip_pat = re.compile(r"听.{,3}[到见清楚]|你们|他|快递|业务员|客服|[网站签收派送转]|登记|反馈|其他|上报")
                            
# 目前rasa使用的IO，目的是对外界输入进行预处理
class WdgjIO(InputChannel):
    def name(self) -> Text:
        """Name of your custom channel."""
        return "callassist"


    def blueprint(
            self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            sender_id = request.json.get("sender")  # method to get sender_id
            text = request.json.get("message")  # method to fetch text
            input_channel = self.name()  # method to fetch input channel

            metadata = request.json.get("metadata")
            collector = CollectingOutputChannel()

            logger.info(f"query: {request.json} pid:{os.getpid()}")
            # logger.info(f"query={text} {metadata=}")
            # logger.info(json.dumps(copy.deepcopy(metadata), ensure_ascii=False, indent=4))
            start_time = time.time()

            #先对text进行首尾去除空格处理
            text = text.strip()
            try:
                # servicer: 开头的是客服的语料
                if text.startswith('servicer'):
                    if not metadata: metadata = {}
                    metadata['servicer'] = text.replace('servicer', '').strip(":：")
                    text = '语言模型，' + metadata['servicer']
                    await on_new_message(
                        UserMessage(
                            text,
                            collector,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata,
                            call_time=start_time,
                        )
                    )
                # 对"....."之类的无语意图不做处理
                elif len(set(text) - {'。', '…', '.', '？', '?'}) == 0:
                    await on_new_message(
                        UserMessage(
                            text,
                            collector,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata,
                            call_time=start_time,
                        )
                    )
                else:
                    # 
                    yt_rep = yt_rep_pat.findall(text)
                    if yt_rep:
                        for pat in yt_rep:
                            text = text.replace(pat, 'yt')
                    # 处理三个5、一个8的情况
                    x_ge_y = x_ge_y_pat.findall(text)
                    if x_ge_y:
                        for pat in x_ge_y:
                            x = int(pat[0] if pat[0] not in numbers_dict else numbers_dict[pat[0]])
                            y = pat[-1] if pat[-1] not in numbers_dict else numbers_dict[pat[-1]]
                            text = text.replace(pat, x * y)
                    # 需要保留符号："-"(防止去除后字符串变为13或19位纯数字，从而误识别为运单号或订单号)
                    # comp = re.compile('[^A-Z^a-z^0-9^\u4e00-\u9fa5,，.。?？!！~～\[\]-]')
                    # text = comp.sub('', text).strip()
    
                    # # 去掉句尾的标点符号
                    # if len(text) > 0 and text[-1] in {',', '，', '.', '。', '?', '？', '!', '！', '~', '～'}:
                    #     text = text[:-1]
    
                    # 处理手机号码前面有“+86”的情况
                    # text = text.replace('+86', '')
                    # text = text.replace('圆通快递员', '快递员').replace('圆通快递', '').replace('圆通速递', '')\
                    #     .replace('圆通公司', '').replace('圆通总公司', '')
    
                    if len(text) > 0:
                        await on_new_message(
                            UserMessage(
                                text.lower(),
                                collector,
                                sender_id,
                                input_channel=input_channel,
                                metadata=metadata,
                                call_time=start_time,
                            )
                        )
                    else:
                        await on_new_message(
                            UserMessage(
                                '亲亲，您好',
                                collector,
                                sender_id,
                                input_channel=input_channel,
                                metadata=metadata,
                                call_time=start_time,
                            )
                        )
                # 不合规回复check and skip
                if collector.messages and collector.messages[-1].get('last_message'):
                    last_message = collector.messages[-1].get('last_message')
                    # # 客服意图
                    if last_message['intent_name'] == 'incorrect_language' and not incrt_lang_pat.search(last_message['text']):
                        logger.info(f"incorrect_lang_skip: {request.json}")
                        last_message['intent_name'] = 'incorrect_lang_skip'
                    if last_message['intent_name'] == 'guide_upgrade_intention' and (not guide_upgrade_pat.search(last_message['text']) or guide_upgrade_skip_pat.search(last_message['text'])):
                        logger.info(f"guide_upgrade_skip: {request.json}")
                        last_message['intent_name'] = 'guide_upgrade_skip'
                    # 客户意图
                    if last_message['intent_name'] == 'response_untimely' and (not response_untimely_pat.search(last_message['text']) or response_untimely_skip_pat.search(last_message['text'])):
                        logger.info(f"response_untimely_skip: {request.json}")
                        last_message['intent_name'] = 'response_untimely_skip'
                    if last_message['intent_name'] == 'interrupt_speech' and (not interrupt_speech_pat.search(last_message['text']) or interrupt_speech_skip_pat.search(last_message['text'])):
                        logger.info(f"interrupt_speech_skip: {request.json}")
                        last_message['intent_name'] = 'interrupt_speech_skip'
                    if last_message['intent_name'] == 'understand_insufficiently' and (not understand_insufficiently_pat.search(last_message['text']) or understand_insufficiently_skip_pat.search(last_message['text'])):
                        logger.info(f"understand_insufficiently_skip: {request.json}")
                        last_message['intent_name'] = 'understand_insufficiently_skip'
                    if last_message['intent_name'] == 'perfunctory_attitude' and (not perfunctory_attitude_pat.search(last_message['text']) or perfunctory_attitude_skip_pat.search(last_message['text'])):
                        logger.info(f"perfunctory_attitude_skip: {request.json}")
                        last_message['intent_name'] = 'perfunctory_attitude_skip'
                    if last_message['intent_name'] == 'customer_be_threatened' and not customer_be_threatened_pat.search(last_message['text']):
                        logger.info(f"customer_be_threatened_skip: {request.json}")
                        last_message['intent_name'] = 'customer_be_threatened_skip'
                    if last_message['intent_name'] == 'upgrade_intention' and not upgrade_intention_pat.search(last_message['text']):
                        logger.info(f"upgrade_intention_skip: {request.json}")
                        last_message['intent_name'] = 'upgrade_intention_skip'
                    if last_message['intent_name'] == 'customer_praise' and not customer_praise_pat.search(last_message['text']):
                        logger.info(f"customer_praise_skip: {request.json}")
                        last_message['intent_name'] = 'customer_praise_skip'
            except Exception as e:
                logger.exception(f"exception: {request.json} {e}")
            logger.info(f"response: {collector.messages}, time: {time.time() - start_time:.2f}")    
            return response.json(collector.messages)

        return custom_webhook
