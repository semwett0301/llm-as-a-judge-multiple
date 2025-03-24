import json
import os

from constants import TEMPERATURE, JUDGES, VERSIONS, ANSWER_MODEL_PAIRS, SPLIT_TYPE_TO_PATH, QUERY_TYPE_TO_PATH, \
    SPLIT_NUM_TO_PATH
from utils import extract_ans_rulellm


# from chatgpt import chat

# from qwen import qwenchat
# from chatglm import chatglmchat
# from minmax import call_minmax
# from exttool import qualitycheck
# from claude import call_claude
# from gpt4 import callgpt4
# from gpt4new import callgpt4new

# from llama2 import call_llama


def extract_gpt4_eval(question_id, model_1, model_2):
    gpt_4_ans_file = f"./llm_judge_repo_data/vicuna_bench/model_judgment/gpt-4_pair.jsonl"

    with open(gpt_4_ans_file, 'r', encoding='utf-8') as f1:
        gpt_4_ans = [json.loads(ans) for ans in f1.readlines() if json.loads(ans)["question_id"] == question_id]

        for item in gpt_4_ans:
            c_model_1 = item["model_1"]
            c_model_2 = item["model_2"]

            if {c_model_1, c_model_2} != {model_1, model_2}:
                return -1  # Model pair doesn't match

            reverse = c_model_1 == model_2 and c_model_2 == model_1
            g1_winner = gpt_4_ans['g1_winner']
            g2_winner = gpt_4_ans['g2_winner']

            winner_map = {
                'model_1': 2 if reverse else 1,
                'model_2': 1 if reverse else 2,
                'tie': 3
            }

            return winner_map.get(g1_winner, -1) if g1_winner == g2_winner else 0


def after_order_gpt4_both(first_model, second_model, split_type='equal',
                          split_num=3, judger='gpt-3.5-turbo',
                          output_dir=r'./llm_judge_repo_data/vicuna_bench/order_change_judgment',
                          version='old', query_type='pure', temperature=TEMPERATURE):
    # Resolve result directory based on split_type or query_type
    result_dir = output_dir
    result_dir += SPLIT_TYPE_TO_PATH.get(split_type, QUERY_TYPE_TO_PATH.get(query_type, ''))
    result_dir += SPLIT_NUM_TO_PATH.get(split_num, '')

    # Build main output file path
    base_filename = f"{query_type}_temp{temperature}_{first_model}_{second_model}_{version}_{judger}.jsonl"
    output_file = os.path.join(result_dir, base_filename)

    if query_type == 'split':
        output_file = os.path.join(output_dir, 'EqualSplit', base_filename)
        output_file_2 = os.path.join(output_dir, 'IBM6PURE', base_filename)

    # Read file(s)
    with open(output_file, 'r', encoding='utf-8') as f:
        queried_str = f.readlines()
    assert len(queried_str) % 2 == 0

    if query_type == 'split':
        with open(output_file_2, 'r', encoding='utf-8') as f:
            queried_str_2 = f.readlines()
        assert len(queried_str_2) % 2 == 0
    else:
        queried_str_2 = []

    # Prepare answer dict with GPT-4 results
    answer_dict = {
        qid: {'gpt4': extract_gpt4_eval(qid, first_model, second_model)}
        for qid in range(1, 81)
    }

    def process_judgments(lines, key_name):
        for i in range(0, len(lines), 2):
            rec1 = json.loads(lines[i])
            rec2 = json.loads(lines[i + 1])
            qid = rec1['question_id']
            ans1 = extract_ans_rulellm(rec1['judge_answer'], version)
            ans2 = extract_ans_rulellm(rec2['judge_answer'], version)

            if ans1 == -1 or ans2 == -1:
                answer_dict[qid][key_name] = -1
            elif ans1 != ans2 or (ans1 == 3 and ans2 == 3):
                answer_dict[qid][key_name] = ans1
            else:
                answer_dict[qid][key_name] = 0

    process_judgments(queried_str, 'queried_str')
    if queried_str_2:
        process_judgments(queried_str_2, 'queried_str2')

    # Compare judgments with GPT-4
    gpt4_valid_count = 0
    consistent_count = 0
    for qid, vals in answer_dict.items():
        gpt4_ans = vals['gpt4']
        if gpt4_ans in [-1, 0]:
            continue

        gpt4_valid_count += 1
        if vals.get('queried_str') == gpt4_ans or vals.get('queried_str2') == gpt4_ans:
            consistent_count += 1

    print(f'orderCon_gpt4Con_same {consistent_count}, gpt4same {gpt4_valid_count}')
    return consistent_count, gpt4_valid_count


def rq_ablation():
    order_consistent_gpt4_consistent_origin, gpt_same_origin = 0, 0
    order_consistent_gpt4_consistent_fix, gpt_same_fix = 0, 0

    for judge in JUDGES:
        for version in VERSIONS:
            for model_pair in ANSWER_MODEL_PAIRS:
                model_1 = model_pair[0]
                model_2 = model_pair[1]
                print(f"Model 1: {model_1}")
                print(f"Model 2: {model_2}")

                consistency_pure, gpt4_same_pure = after_order_gpt4_both(first_model=model_1, second_model=model_2, judger=judge,
                                                                         version=version, query_type='pure')

                consistency_split, gpt4_same_split = after_order_gpt4_both(first_model=model_1, second_model=model_2, judger=judge,
                                                                           version=version, query_type='split',
                                                                           split_type='IBM-pure')

                order_consistent_gpt4_consistent_origin += consistency_pure
                gpt_same_origin += gpt4_same_pure

                order_consistent_gpt4_consistent_fix += consistency_split
                gpt_same_fix += gpt4_same_split

        print(f'origin AR rate is {round(order_consistent_gpt4_consistent_origin * 100.0 / gpt_same_origin, 4)}')
        print(f'fix AR rate is {round(order_consistent_gpt4_consistent_fix * 100.0 / gpt_same_fix, 4)}')


if __name__ == "__main__":
    rq_ablation()
