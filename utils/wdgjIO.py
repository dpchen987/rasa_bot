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
            except Exception as e:
                logger.exception(f"exception: {request.json} {e}")
            logger.info(f"response: {collector.messages}, time: {time.time() - start_time:.2f}")    
            return response.json(collector.messages)

        return custom_webhook
