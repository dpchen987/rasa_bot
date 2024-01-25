import re
import asyncio
import structlog
import inspect
from sanic import Sanic, Blueprint, response
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable, NoReturn
import json, copy

import rasa.utils.endpoints
from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

logger = structlog.getLogger(__name__)


# 目前使用的rasa使用的IO，目的是对外界输入进行预处理
class WdgjIO(InputChannel):
    def name(self) -> Text:
        """Name of your custom channel."""
        return "wdgj"


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

            logger.info(" ", query=f"{text}")
            logger.info(" ", metadata=json.dumps(copy.deepcopy(metadata), ensure_ascii=False, indent=4))

            #先对text进行首尾去除空格处理
            text = text.strip()

            # 对"....."之类的无语意图不做处理
            if len(set(text) - {'。', '…', '.', '？', '?'}) == 0:
                await on_new_message(
                    UserMessage(
                        text,
                        collector,
                        sender_id,
                        input_channel=input_channel,
                        metadata=metadata,
                    )
                )
            else:
                text = text.replace("&hellip;", "…").replace("&mdash;", "—").replace("&nbsp;", " ").replace("👌🏻", "ok")
                # 处理系统消息,只提取单号
                if len(text) > 20 and ("我要咨询的单据是" in text or "【系统消息】用户发送了一个" in text):
                    text = text[len(text)-15:]

                # 需要保留符号："-"(防止去除后字符串变为13或19位纯数字，从而误识别为运单号或订单号)
                comp = re.compile('[^A-Z^a-z^0-9^\u4e00-\u9fa5,，.。?？!！~～\[\]-]')
                text = comp.sub('', text).strip()

                # 替换表情符号
                emoji = {"👌": "[ok]", "😓": "[无语]", "🙏": "[拜托]", "😮‍💨": "[叹气]", "🥲": "[想哭]", "😅": "[尴尬]",
                         "📦": "[包裹]",
                         "🙂": "[无语]", "👋": "[击掌]", "🤣": "[笑哭]", "🉑️": "[可以]", "🈚️": "[无]", "🌪️": "[龙卷风]",
                         "🌧️": "[有雨]",
                         "😊": "[可爱]", "😇": "[天使]", "👿": "[恶魔]", "😘": "[亲亲]", "😡": "[发怒]", "🤬": "[生气]",
                         "👍🏻": "[点赞]",
                         "😭": "[大哭]", "😂": "[笑哭]", "😣": "[难受]"}
                for t in text:
                    if emoji.get(t) is not None:
                        text = text.replace(t, emoji.get(t))

                # # 去掉句尾的标点符号
                # if len(text) > 0 and text[-1] in {',', '，', '.', '。', '?', '？', '!', '！', '~', '～'}:
                #     text = text[:-1]

                # 处理手机号码前面有“+86”的情况
                text = text.replace('+86', '')
                text = text.replace('圆通快递员', '快递员').replace('圆通快递', '').replace('圆通速递', '')\
                    .replace('圆通公司', '').replace('圆通总公司', '')

                if len(text) > 0:
                    await on_new_message(
                        UserMessage(
                            text.lower(),
                            collector,
                            sender_id,
                            input_channel=input_channel,
                            metadata=metadata,
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
                        )
                    )

            return response.json(collector.messages)

        return custom_webhook