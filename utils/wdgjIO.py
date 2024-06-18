import re
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
                            r"无[聊语]|恶心|[气去]死|倒霉|md|没.{,3}[眼耳脑]|[眼耳脑听].{,3}[坏病问题]|[眼耳脑].{,3}干.{,3}用|嘴.{,3}干净|[真太好]烦|活该|正常.{,3}[都可能].{,4}理解|[说讲]人话")
guide_upgrade_pat = re.compile(r"邮.{,3}[政局]|123[104]5|消.{,5}协|市民热线|监管部门|媒体|报道|举报|曝光|第三方.{,5}投诉|(?:其他|别的).{,2}(?:渠道|地方|方式).{,3}投诉|升级|第三方")
customer_be_threatened_pat = re.compile(r"恐吓.{,3}我|威胁.{,3}我|[搞弄].{,3}我|[要叫让说].{,3}晚上.{,3}[不别].{,3}[出门]|[揍打骂抱摸]我|自杀|强[奸暴]|偷窥|调戏")
upgrade_intention_pat = re.compile(r"邮.{,3}[政局]|123[104]5|315|消.{,5}协|市民热线|监管部门|媒体|报道|举报|曝光|第三方.{,5}投诉|(?:其他|别的).{,2}(?:渠道|地方|方式).{,3}投诉"
                                   r"新闻|记者|报社|栏目组|微博|朋友圈|起诉|升级|管理部门|报[案警]|法院")
customer_praise_pat = re.compile(r"(?:我|怎么|方[式法]|途径)[^不]{,3}表扬你|给你?.{,3}(?:好评|赞)|(?:我|怎么|方[式法]|途径)[^不]{,3}好评|表扬你|好评")
# response_untimely_pat = re.compile(r"[不别].{,3}静音|在.{,5}吗|有没有.{,3}听|能不能.{,3}听|听.{,5}了[吗没么嘛]|[能有]听.{,6}[吧么嘛]|[问跟]你{,3}[话]|人呢|说话[呀啊]|不说话|回[话答]||||")
                            
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

            logger.info(f"query: {request.json}")
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
                # 不合规回复check
                if collector.messages and collector.messages[-1].get('last_message'):
                    last_message = collector.messages[-1].get('last_message')
                    if last_message['intent_name'] == 'incorrect_language' and not incrt_lang_pat.search(last_message['text']):
                        logger.info(f"incorrect_lang_skip: {request.json}")
                        last_message['intent_name'] = 'incorrect_lang_skip'
                    if last_message['intent_name'] == 'guide_upgrade_intention' and not guide_upgrade_pat.search(last_message['text']):
                        logger.info(f"guide_upgrade_skip: {request.json}")
                        last_message['intent_name'] = 'guide_upgrade_skip'
                    if last_message['intent_name'] == 'upgrade_intention' and not upgrade_intention_pat.search(last_message['text']):
                        logger.info(f"upgrade_intention_skip: {request.json}")
                        last_message['intent_name'] = 'upgrade_intention_skip'
                    if last_message['intent_name'] == 'customer_be_threatened' and not customer_be_threatened_pat.search(last_message['text']):
                        logger.info(f"customer_be_threatened_skip: {request.json}")
                        last_message['intent_name'] = 'customer_be_threatened_skip'
                    if last_message['intent_name'] == 'customer_praise' and not customer_praise_pat.search(last_message['text']):
                        logger.info(f"customer_praise_skip: {request.json}")
                        last_message['intent_name'] = 'customer_praise_skip'
            except Exception as e:
                logger.exception(f"exception: {request.json} {e}")
            logger.info(f"response: {collector.messages}, time: {time.time() - start_time:.2f}")    
            return response.json(collector.messages)

        return custom_webhook
