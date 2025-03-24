import numpy as np
import matplotlib.pyplot as plt
import os
import json
from transformers import GPT2Tokenizer
import math
from matplotlib.ticker import ScalarFormatter
import argparse


plt.rcParams['pdf.fonttype'] = 42

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')

def count_token(text):
    encoded_input = tokenizer(text, return_tensors='pt')
    return encoded_input['input_ids'].shape[-1]


def generate_prompt(ans1,ans2,question_content,version='old'):
    template_init = f"\n[Question]\n{question_content}\n\n"
    names = ['A','B']
    template_init += f"[The Start of Assistant {names[0]}'s Answer]\n{ans1}\n\n[The End of Assistant {names[0]}'s Answer]\n\n[The Start of Assistant {names[1]}'s Answer]\n{ans2}\n\n[The End of Assistant {names[1]}'s Answer]\n\n"
    if version == 'old':
        system_prompt = f"We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above.\nPlease rate the helpfulness, relevance, accuracy, level of details of their responses. Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance.\nPlease first output a single line containing only two values indicating the scores for Assistant {names[0]} and {names[1]}, respectively. The two scores are separated by a space. In the subsequent line, please provide a comprehensive explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment.\n\n"
    elif version == 'new':
        system_prompt = "Please act as an impartial judge and evaluate the quality of the responses provided by two AI assistants to the user question displayed below. You should choose the assistant that follows the user's instructions and answers the user's question better. Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of their responses. Begin your evaluation by comparing the two responses and provide a short explanation. Avoid any positional biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your final verdict by strictly following this format: \"[[A]]\" if assistant A is better, \"[[B]]\" if assistant B is better, and \"[[C]]\" for a tie."
    elif version =='likert': 
        system_prompt =f"We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above.Please compare the helpfulness, relevance, accuracy, level of details of their responses. The rating should be from the set of 1, 2, 3, 4, 5, 6, or 7, where higher numbers indicated that Assistant {names[1]} was better than Assistant {names[0]}. Please first output a single line containing only one value indicating the preference between Assistant {names[0]} and {names[1]}. In the subsequent line, please provide a brief explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment."
    prompt = template_init + "[System]\n" + system_prompt 
    return prompt

def query_all(model1='llama-13b', model2='vicuna-13b', judger='gpt-3.5-turbo',split_type='equal', split_num=3, question_dir=r'../llm_judge_repo_data/data/questions/question.jsonl', answer_dir=r'../llm_judge_repo_data/data/vicuna_bench/model_answer', output_dir=r'../llm_judge_repo_data/data/vicuna_bench/order_change_judgment',version='old', query_type='pure',temperature=0.7, only_code=False, special_qid=None, additional_info = False):
    output_dir2 = output_dir
    if only_code: 
        output_dir2 = output_dir2 + '/only_code'
    if additional_info: 
        output_dir2 = output_dir2 + '/additional_info'
    if split_type =='IBM-BERT': 
        output_dir2 = output_dir2 + '/IBM6BERT'
    if split_type =='IBM-pure':
        output_dir2 = output_dir2 + '/IBM6PURE'
    if split_type =='equal' and query_type == 'split':
        output_dir2 = output_dir2 + '/EqualSplit'
    if split_type =='equal' and query_type == 'pure':
        output_dir2 = output_dir2 + '/Pure'
    if split_num==2:
        output_dir2 += 'Split2'
    output_dir = output_dir2
    model1_dir = answer_dir + '/' +model1+'.jsonl'
    model2_dir = answer_dir + '/' +model2+'.jsonl'
    model1_answers,model2_answers = [],[]
    output_file = output_dir + '/' + query_type +'_'+'temp'+ str(temperature)+ '_' + model1 + '_'+model2+'_'+ version + '_' + judger+'.jsonl'
    with open(model1_dir,'r',encoding='utf-8') as f, open(model2_dir,'r',encoding='utf-8') as f2:
        model1_answers_str = f.readlines()
        model2_answers_str = f2.readlines()
    for model1_answer_str,model2_answer_str in zip(model1_answers_str,model2_answers_str):
        model1_answer = json.loads(model1_answer_str)
        model2_answer = json.loads(model2_answer_str)
        model1_answers.append(model1_answer)
        model2_answers.append(model2_answer)
    questions_str,questions = [],[]
    with open(question_dir,'r',encoding='utf-8') as f:
        questions_str = f.readlines()
    all_token, add_token = 0,0
    for question_str in questions_str:
        question = json.loads(question_str)
        question_id,question_content,question_category = question['question_id'],question['text'],question['category']
        model1_answer_content,model2_answer_content = '',''
        for model1_answer in model1_answers:
            if model1_answer['question_id'] == question_id:
                model1_answer_content = model1_answer['choices'][0]['turns'][0]
        for model2_answer in model2_answers:
            if model2_answer['question_id'] == question_id:
                model2_answer_content = model2_answer['choices'][0]['turns'][0]
        if model1_answer_content=='' or model2_answer_content=='':
            with open(output_dir + '/' + 'error_log.txt','a',encoding='utf-8') as f:
                f.write('question_id: {}, model1 is {} and model2 is {} there is no response'.format(question_id,model1,model2))
        sys_prompt = "You are a helpful and precise assistant for checking the quality of the answer."
        if query_type == 'pure':
            prompt = generate_prompt(ans1=model1_answer_content,ans2=model2_answer_content, question_content=question_content,version=version)
        addition_prompt = f"[The Start of Assistant A's Answer]\n\n\n[The End of Assistant B's Answer]"
        all_prompt = sys_prompt + prompt 
        all_token += count_token(all_prompt)
        add_token = count_token(addition_prompt)
    print(f'all_token is {all_token}, add_token is {add_token}')
    return all_token*1.0/80, add_token


def main():
    temperature = 0
    model1='gpt-3.5-turbo'
    model2='claude-v1'
    judger= 'chatglm' #  'gpt-3.5-turbo'  'chatglm',  'qwen', 'minmax', 'claude2', 'gpt4'


    for judger in ['chatglm']:
        for version in ['new', 'old', 'likert']:

            models = [['gpt-3.5-turbo', 'claude-v1'],['llama-13b', 'vicuna-13b'],['alpaca-13b', 'vicuna-13b'], 
                ['gpt-3.5-turbo', 'gpt-4'], 
                ['gpt-4', 'claude-v1'], 
                ['vicuna-13b', 'vicuna-7b'], 
                ['vicuna-7b', 'alpaca-13b'], 
                ['gpt-4', 'vicuna-13b']]

            all_token_all , add_token = 0,0
            for model_pair in models:

                model1 = model_pair[0]
                model2 = model_pair[1]
                print(f"Model 1: {model1}")
                print(f"Model 2: {model2}")
                all_token, add_token = query_all(model1=model1, model2=model2,judger=judger,version=version,query_type='pure',temperature=temperature)
                all_token_all += all_token
            # print('average all_token_all is {}, add_token is {}'.format( all_token_all*1.0/(len(models)) , add_token ))


def draw_pic2():
    plt.figure(figsize=(5,2.5))
    res_dict = { 'new': [862.9875, 20],'old':[812.9875,20] ,'likert': [811.9875 , 20]}
    x_list = [i for i in range(10)]
    relation_no = [ 862.9875 for i in range(10)]
    relation_list_min = [ 862.9875 + i*20*2 for i in range(10)]
    relation_list_max = [ (862.9875 + i*20*2)*2 for i in range(10)]
    relation_list_min[0] = 862.9875
    relation_list_max[0] = 862.9875
    plt.plot(x_list, relation_no, marker='*', linestyle='-', label='Rela-ori')
    plt.plot(x_list, relation_list_min, marker='*', linestyle='-', label='Rela-min')
    plt.plot(x_list, relation_list_max, marker='*', linestyle='-', label='Rela-max')
    score_no = [ 812.9875 for i in range(10)]
    score_list_min = [ 812.9875 + i*20*2 for i in range(10)]
    score_list_max = [ (812.9875 + i*20*2)*2 for i in range(10)]
    score_list_min[0] = 812.9875
    score_list_max[0] = 812.9875
    plt.plot(x_list, score_no, marker=',', linestyle='-.', label='Score-ori')
    plt.plot(x_list, score_list_min, marker=',', linestyle='-.', label='Score-min')
    plt.plot(x_list, score_list_max, marker=',', linestyle='-.', label='Score-max')
    likert_no = [ 811.9875 for i in range(10)]
    likert_list_min = [ 811.9875 + i*20*2 for i in range(10)]
    likert_list_max = [ (811.9875 + i*20*2)*2 for i in range(10)]
    likert_list_min[0] = 811.9875
    likert_list_max[0] = 811.9875
    plt.plot(x_list, likert_no, marker='.', linestyle=':', label='Likert-ori')
    plt.plot(x_list, likert_list_min, marker='.', linestyle=':', label='Likert-min')
    plt.plot(x_list, likert_list_max, marker='.', linestyle=':', label='Likert-max')
    plt.xlabel('# K', fontsize=10)
    plt.ylabel('Avg. # input token length', fontsize=10)
    plt.ylim(500,2800)
    plt.legend( prop={'size': 7}, ncol=3,loc='upper left')
    savename = './pic/RQ_IO4K' + 'test1.pdf'
    plt.savefig(savename, bbox_inches='tight')


def draw_pic_splitk():
    fig = plt.figure()
    plt.figure(figsize=(5,2.5))
    res_dict = { 'new': [862.9875, 20],'old':[812.9875,20] ,'likert': [811.9875 , 20]}
    x_max = 7
    x_list = [i for i in range(1,x_max)]
    def count_result(p1,p2,k):
        return math.comb(p1-1,k-1 ) * math.comb(p2-1,k-1)
    base_len_dict = {'charlevel': 1000, 'tokenlevel': 829, 'sentenlevel': 30 }
    sentenlevel = base_len_dict['sentenlevel']
    sentenlevel_curves = []
    sentence_num_list= [10,20,30,40]
    for j in sentence_num_list:
        sentenlevel_curves.append( [ count_result(j,j,i) for i in range(1,x_max)])
    
    epo = 0
    for j in sentence_num_list:
        label = 'Avg-' + str(j)
        plt.plot(x_list, sentenlevel_curves[epo], marker='*', linestyle='-', label=label)
        epo += 1
    plt.yscale('symlog')
    plt.xlabel('# K', fontsize=10)
    plt.ylabel('# Computation', fontsize=10)
    plt.legend( prop={'size': 7}, ncol=2,loc='upper left')
    savename = './pic/RQ_IO4K' + 'test4.pdf'
    plt.savefig(savename, bbox_inches='tight')


parser = argparse.ArgumentParser()
parser.add_argument("--PIC1", help="PIC1", action="store_true")
parser.add_argument("--PIC2", help="PIC2", action="store_true")

args = parser.parse_args()

if args.PIC1:
    draw_pic2()
elif args.PIC2:
    draw_pic_splitk()
else:
    print("PLEASE USE PIC1 OR PIC2")
