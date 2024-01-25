import pandas as pd

df = pd.read_csv('230000.csv', sep='\t')
df = df[df['turn'] == '问']
df = df.dropna()
df = df[(~df['pred'].isin(['faq', 'inform', 'nlu_fallback', 'affirm', 'deny', 'no_other_questions', 'do_not_return', 'has_received',
                           'complaint']))]
print(df.head(20))
# df['intent_change'] = df.groupby(['id'])['pred'].transform(lambda x: ''.join(str(x).strip('\n')))
df['intent_change'] = df.groupby(['id'])['pred'].transform(lambda x: x.str.cat(sep=' '))
df = df[['id', 'intent_change']].drop_duplicates()
print(df.head())
df.to_csv('23000_intent.csv', sep='\t')
