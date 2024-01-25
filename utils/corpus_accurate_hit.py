import copy
import os
import re
from typing import Text

import yaml
import json

# 从训练数据中生成精准命中文件、冲突样本、意图统计文件等
def main():
    source_path = "../data/nlu"
    target_path = "../corpus_dict.json"
    problem_path = "../conflict_examples.txt"
    intent_statics_path = "../intent_statics.txt"
    store_corpus_dict = {}
    store_corpus_dict_bak = {}
    conflict_examples_dict = {}
    intent_statics = {}
    for root, dirs, files in os.walk(source_path):
        # responses下的语料不需要添加
        if "responses" in root:
            continue

        for file in files:
            file_path = os.path.join(root, file)
            if file_path.split('/')[-1][0] == '.':
                continue
            f = open(file_path, 'r', encoding='utf-8')
            yml_config = yaml.load(f, Loader=yaml.FullLoader)
            if yml_config is None:
                print(file + ': is empty!!!')
                continue
            nlu = yml_config.get('nlu')
            for intent_examples in nlu:
                intent = intent_examples.get('intent')
                if not intent:
                    # print(intent_examples)
                    continue
                # if "/" in intent:
                #     intent = intent.split("/")[0]
                intent_name = intent
                if intent_name[3] == '/':
                    intent_name = intent_name.replace('/', '_')
                intent_statics[intent_name] = 0
                for sen in intent_examples.get('examples').split("\n"):
                    if len(sen) == 0:
                        continue
                        
                    intent_statics[intent_name] += 1

                    sen = sen.lower()
                    raw_sen = copy.deepcopy(sen)[2:].strip()
                    sen = remove_mark(sen[2:].strip())
                    if store_corpus_dict.get(sen) is None:
                        store_corpus_dict[sen] = intent
                        store_corpus_dict_bak[sen] = raw_sen
                    else:
                        if conflict_examples_dict.get(sen) is not None:
                            conflict_examples_dict[sen].append(raw_sen)
                        else:
                            conflict_examples_dict[sen] = []
                            conflict_examples_dict[sen].append(store_corpus_dict_bak.get(sen))
                            conflict_examples_dict[sen].append(raw_sen)

        with open(target_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(store_corpus_dict, ensure_ascii=False))

        conflict_examples = [key + ' ======== ' + ' ## '.join(value) + '\n' for key, value in conflict_examples_dict.items()]

        total = sum([v for k, v in intent_statics.items()])
        intent_statics_sorted = sorted(intent_statics.items(), key=lambda x: x[1], reverse=True)
        intent_statics_list = [e[0] + ' == ' + str(e[1]) + '\n' for e in intent_statics_sorted] + ["\n", "total == "+str(total)]

        with open(problem_path, 'w', encoding='utf-8') as file:
            file.writelines(conflict_examples)
            
        with open(intent_statics_path, 'w', encoding='utf-8') as file:
            file.writelines(intent_statics_list)


def remove_mark(text: Text) -> Text:
    """去除语料中实体标记所带来的符号，将其还原为原始语料"""
    pattern = "\[[^\[\]\(\)]+]([({][^\[\]\(\)]+[)}])"
    res = re.finditer(pattern, text)
    if not res:
        return text
    for i in res:
        repl = i.group()
        repl = re.sub(r"[\[\]]", "", repl)
        repl = repl.replace(i.group(1), "")
        text = text.replace(i.group(), repl)

    cleaned_string = re.sub(r'[^\w\u4e00-\u9fff]', '', text)

    # 如果去除符号后的字符串为空，就返回原始字符串，否则返回去除符号后的字符串
    return text if not cleaned_string else cleaned_string

    # raw_text = copy.deepcopy(text)
    # cleaned_string = ''.join(re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', text))

    # # 如果去除符号后的字符串为空，就返回原始字符串，否则返回去除符号后的字符串
    # return raw_text if not cleaned_string else cleaned_string


if __name__ == '__main__':
    main()