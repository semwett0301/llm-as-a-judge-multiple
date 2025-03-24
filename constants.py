TEMPERATURE = 0

SPLIT_TYPE_TO_PATH = {
    'IBM-BERT': '/IBM6BERT',
    'IBM-pure': '/IBM6PURE',
}

QUERY_TYPE_TO_PATH = {
    'split': '/EqualSplit',
    'pure': '/Pure'
}

SPLIT_NUM_TO_PATH = {
    2: '/Split2',
    4: '/Split4'
}

ANSWER_MODEL_PAIRS = [
    ['gpt-3.5-turbo', 'claude-v1'],
    ['llama-13b', 'vicuna-13b'],
    ['alpaca-13b', 'vicuna-13b'],
    ['gpt-3.5-turbo', 'gpt-4'],
    ['gpt-4', 'claude-v1'],
    ['vicuna-13b', 'vicuna-7b'],
    ['vicuna-7b', 'alpaca-13b'],
    ['gpt-4', 'vicuna-13b']
]

JUDGES = ['gpt-3.5-turbo'] # 'gpt-3.5-turbo'  'chatglm',  'qwen', 'claude2',  'gpt4newtx'
VERSIONS = ['new'] # ['new','old','likert']