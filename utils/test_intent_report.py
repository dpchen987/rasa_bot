import json
import math
import re

input_file = 'intent_report.json'

# 加载 JSON 文件
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

import pandas as pd

intent_name_f1_score = {}

for key in data:
    if isinstance(data[key], dict):
        intent_name_f1_score[key] = data[key].get('f1-score')


# 根据value值进行排序
sorted_dict = sorted(intent_name_f1_score.items(), key=lambda x: x[1])

df = pd.DataFrame(sorted_dict)

df.to_excel("intent_f1_score_output1201.xlsx", index=False)
