import re
from typing import Text

import pandas as pd


"""
用于扩充语料时，过滤掉已有训练样本
"""


def remove_mark(text: Text) -> Text:
    """去除语料中实体标记所带来的符号，将其还原为原始语料"""
    text = text.replace('用户（收件人）：', '').replace('@圆通快递 ', '')
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


corpus = list(pd.read_json('../corpus_dict.json', orient='index').to_dict()[0].keys())
pd = pd.read_excel('../to_filter.xls')

with open('../filtered.txt', 'w') as f:
    for val in pd.values:
        if remove_mark(str(val[0])) not in corpus:
            f.write(str(val[1]) + ' : ' + str(val[0]).replace('用户（收件人）：', '').replace('@圆通快递 ', '').replace('\n', '') + '\n')