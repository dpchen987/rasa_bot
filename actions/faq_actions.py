from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUttered, UserUtteranceReverted, SlotSet
from rasa_sdk.executor import CollectingDispatcher


# 当外界输入是faq意图时，需要对会话标记为非首句并且将会话进行回滚，并根据需要考虑是否将机器人之前的回复(外界输出之后机器人的回复)进行二次输出
class ActionGoBack(Action):

    def name(self) -> Text:
        return "action_faq"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 首句标志槽位，用于标记外界输入是不是首句
        first_sentence_used = int(tracker.get_slot('slot_first_sentence_used'))
        if first_sentence_used == 0:
            first_sentence_used = 1

        # current_state = tracker.current_state()
        # events = current_state['events']
        # event_list = []
        # for index in range(len(events) - 3, 0, -1):
        #     tmp_event = events[index]
        #     if len(event_list) >= 1:
        #         break
        #     elif tmp_event['event'] == 'bot':
        #         if not tmp_event.get('metadata'):
        #             continue
        #         if not tmp_event['metadata'].get('utter_action'):
        #             if tmp_event.get('text'):
        #                 event_list.append(tmp_event)
        #             continue
        #         if 'faq' in tmp_event['metadata']['utter_action']:
        #             continue
        #         event_list.append(tmp_event)
        #
        # # 去除不存在回复的情况
        # if len(event_list) <= 0:
        #     return [SlotSet('slot_first_sentence_used', first_sentence_used)]
        #
        # utter_action_list = []
        # utter_text_list = []
        # for bot_event in event_list:
        #     if bot_event['metadata'].get('utter_action'):
        #         utter_action = bot_event['metadata'].get('utter_action')
        #         utter_action_list.append(utter_action)
        #     elif bot_event.get('text'):
        #         text = bot_event['text']
        #         utter_text_list.append(text)
        #
        # if len(utter_action_list) + len(utter_text_list) <= 0:
        #     return [SlotSet('slot_first_sentence_used', first_sentence_used)]
        #
        # utter_action_list = list(reversed(utter_action_list))
        # utter_text_list = list(reversed(utter_text_list))
        # for action_name in utter_action_list:
        #     if action_name:
        #         dispatcher.utter_message(response=action_name)
        #
        # for action_text in utter_text_list:
        #     if action_text:
        #         dispatcher.utter_message(text=text)
        #
        # return [UserUtteranceReverted(), SlotSet('slot_first_sentence_used', first_sentence_used)]

        return [SlotSet('slot_first_sentence_used', first_sentence_used)]


# 在运单号表单激活状态下，对faq进行回滚，并将机器人之前的回复(外界输出之后机器人的回复)进行二次输出
class ActionFaqCondition(Action):

    def name(self) -> Text:
        return "action_faq_condition"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 从跟踪器tracker中获取最近机器人的回复事件
        current_state = tracker.current_state()
        events = current_state['events']
        event_list = []
        for index in range(len(events) - 3, 0, -1):
            tmp_event = events[index]
            if len(event_list) >= 1:
                break
            elif tmp_event['event'] == 'bot':
                if not tmp_event.get('metadata'):
                    continue
                if not tmp_event['metadata'].get('utter_action'):
                    if tmp_event.get('text'):
                        event_list.append(tmp_event)
                    continue
                if 'faq' in tmp_event['metadata']['utter_action']:
                    continue
                event_list.append(tmp_event)

        # 去除不存在回复的情况
        if len(event_list) <= 0:
            return []

        # 从机器人最近的回复事件中获取话术或者话术名称
        utter_action_list = []
        utter_text_list = []
        for bot_event in event_list:
            if bot_event['metadata'].get('utter_action'):
                utter_action = bot_event['metadata'].get('utter_action')
                utter_action_list.append(utter_action)
            elif bot_event.get('text'):
                text = bot_event['text']
                utter_text_list.append(text)

        if len(utter_action_list) + len(utter_text_list) <= 0:
            return []

        # 将机器人的回复按照顺序传递给调度台dispatcher
        utter_action_list = list(reversed(utter_action_list))
        utter_text_list = list(reversed(utter_text_list))
        for action_name in utter_action_list:
            if action_name:
                dispatcher.utter_message(response=action_name)

        for action_text in utter_text_list:
            if action_text:
                dispatcher.utter_message(text=text)

        # 最后返回一个“用户回退事件”，该事件的目的是忽略外界的这一轮输入
        return [UserUtteranceReverted()]