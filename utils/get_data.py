import json
import pandas as pd

with open(r'results/intent_errors.json', encoding='utf-8') as f:
    data = json.load(f)

dict_res = {'text':[], 'intent': [], 'pred': []}
for i in data:
    dict_res['text'].append(i['text'])
    dict_res['intent'].append(i['intent'])
    dict_res['pred'].append(i['intent_prediction']['name'])

df = pd.DataFrame(dict_res)
print(df.head())
df.to_excel('intent_error.xlsx', index=False)