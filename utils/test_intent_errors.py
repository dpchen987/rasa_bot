import json
import math
import re

input_file = 'intent_errors.json'

# 加载 JSON 文件
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

import pandas as pd

intent_name_error_count = {}

for key in data:
    if key['intent'] not in intent_name_error_count:
        intent_name_error_count[key['intent']] = 1
    else:
        intent_name_error_count[key['intent']] += 1


# 根据value值进行排序
sorted_dict = sorted(intent_name_error_count.items(), key=lambda x: x[1], reverse=True)

df = pd.DataFrame(sorted_dict)

df.to_excel("intent_error_output1201.xlsx", index=False)
