from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUttered, UserUtteranceReverted, SlotSet,  ActionExecuted
from rasa_sdk.executor import CollectingDispatcher
import re

# 当外界输入是faq意图时，需要对会话标记为非首句并且将会话进行回滚，并根据需要考虑是否将机器人之前的回复(外界输出之后机器人的回复)进行二次输出
class ActionGoBack(Action):

    def name(self) -> Text:
        return "action_faq"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 
        from pprint import pprint
        # pprint("tracker.slots")
        # pprint(tracker.slots)
        # pprint("tracker.events")
        # pprint(tracker.events)
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
        # print(utter_action_list)
        # print(utter_text_list)
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
    

express_id_pat1 = re.compile("(?<![A-Za-z])g\\d{9,13}")
express_id_pat2 = re.compile("(?<![A-Za-z])ytd?\\d{12,14}")
express_id_pat3 = re.compile("(?<![A-Za-z])ytg\\d{11,13}")
express_id_pat4 = re.compile("(?<!\\d)\\d{13}(?!\\d)")
exp_numbers = re.compile(r"[yY][tT][dg]?[\d 零令林一幺妖二两三四五六七八九]*[\d零令林一幺妖二两三四五六七八九]")
repat_numbers = re.compile(r"[\d零令林一幺妖二两三四五六七八九][\d 零令林一幺妖二两三四五六七八九]*[\d零令林一幺妖二两三四五六七八九]")
numbers_dict = {" ": "", "零": "0", "令": "0", "林": "0", "一": "1", "幺": "1", "妖": "1",  "二": "2", "两": "2", "三": "3", "四": "4","五": "5", "六": "6", "七": "7", "八": "8", "九": "9"}   
# 在运单号表单激活状态下，分次读取客户说的运单号片断，拼成完整的运单号
class ActionExpPieceCollect(Action):

    def name(self) -> Text:
        # return "action_faq_condition"
        return "action_exp_piece_collect"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # 从跟踪器tracker中获取最近机器人的回复事件
        current_state = tracker.current_state()
        answer_text = tracker.latest_message['text']
        express_id_piece = tracker.get_slot('slot_express_id_piece')
        print('express_id_piece before:', express_id_piece)
        exp_numbers_mth = exp_numbers.search(answer_text)
        exp_pc_mth = repat_numbers.search(answer_text)
        _event = []
        if exp_numbers_mth:
            exp_numbers_txt = exp_numbers_mth.group()
            for k in numbers_dict:
                if k in exp_numbers_txt:
                    exp_numbers_txt = exp_numbers_txt.replace(k, numbers_dict[k])
            _event.append(SlotSet('slot_express_id_piece', exp_numbers_txt))
            print('express_id_piece after:', exp_numbers_txt)
            if len(exp_numbers_txt) > 15:
                dispatcher.utter_message(text='运单号无效，请提供正确的快递单号！')
                _event.pop()
                _event.append(SlotSet('slot_express_id', express_id_piece))
            elif len(exp_numbers_txt) > 9 and (express_id_pat1.search(exp_numbers_txt) or express_id_pat2.search(exp_numbers_txt) or express_id_pat3.search(exp_numbers_txt) or express_id_pat4.search(exp_numbers_txt)):
                _event.append(SlotSet('slot_express_id', exp_numbers_txt))
            else:
                dispatcher.utter_message(response='utter_ask_continue_express_id')
        elif exp_pc_mth:
            exp_pc_txt = exp_pc_mth.group()
            for k in numbers_dict:
                if k in exp_pc_txt:
                    exp_pc_txt = exp_pc_txt.replace(k, numbers_dict[k])
            express_id_piece = express_id_piece + exp_pc_txt if express_id_piece else exp_pc_txt
            _event.append(SlotSet('slot_express_id_piece', express_id_piece))
            print('express_id_piece after:', express_id_piece)
            if len(express_id_piece) > 15:
                dispatcher.utter_message(text='运单号无效，请提供正确的快递单号！')
                _event.pop()
                _event.append(SlotSet('slot_express_id', express_id_piece))
            elif len(express_id_piece) > 9 and (express_id_pat1.search(express_id_piece) or express_id_pat2.search(express_id_piece) or express_id_pat3.search(express_id_piece) or express_id_pat4.search(express_id_piece)):
                _event.append(SlotSet('slot_express_id', express_id_piece))
            else:
                dispatcher.utter_message(response='utter_ask_continue_express_id')
        
        # 以下代码待删除
        
        # 最后返回一个“用户回退事件”，该事件的目的是忽略外界的这一轮输入
        return _event
        # return [UserUtteranceReverted()] + _event + [ActionExecuted('action_validate_slot_mappings')]
        # return [UserUtteranceReverted()] + _event + [ActionExecuted('validate_collect_express_id_form')]
        # return [UserUtteranceReverted()] + _event + [ActionExecuted('collect_express_id_form')] + [ActionExecuted('validate_collect_express_id_form')]
    
class ActionInputServicer(Action):

    def name(self) -> Text:
        return "action_input_servicer"

    def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        metadata = tracker.latest_message.get("metadata")
        print(metadata)
        dispatcher.utter_message(text='标准话术执行率：90%')
        dispatcher.utter_message(text='违规话术识别：无违规话术')
        return [UserUtteranceReverted()]