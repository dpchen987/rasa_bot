#!/bin/bash

# 删除精准命中数据
echo "cd utils && python corpus_accurate_hit.py && cd .."
cd utils && python corpus_accurate_hit.py && cd ..

echo "rm -rf corpus_dict.json"
rm -rf corpus_dict.json

# 删除历史测试数据
echo "rm -rf train_test_split"
rm -rf train_test_split
echo "rm -rf results"
rm -rf results
echo "rm -rf .rasa"
rm -rf .rasa
echo "rm -rf nohup.out"
rm nohup.out

# 生成新数据集
echo "rasa data split nlu --random-seed 999"
rasa data split nlu --random-seed 999

# 训练。这里不能用nohup命令，否则会立刻跳过 rasa train，执行后面的 rasa test
echo "rasa train nlu -u train_test_split/training_data.yml"
rasa train nlu -u train_test_split/training_data.yml

# 测试
echo "rasa test nlu -u train_test_split/test_data.yml"
rasa test nlu -u train_test_split/test_data.yml