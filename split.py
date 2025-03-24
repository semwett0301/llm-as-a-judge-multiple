from IBM6 import IBM6

MODEL_NAMES = ['A', 'B']

VERSION_TO_SYSTEM_PROMPT = {
    'old': "We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above.\nPlease rate the helpfulness, relevance, accuracy, level of details of their responses. Each assistant receives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance.\nPlease first output a single line containing only two values indicating the scores for Assistant A and B, respectively. The two scores are separated by a space. In the subsequent line, please provide a comprehensive explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment.\n\n",
    'new': "Please act as an impartial judge and evaluate the quality of the responses provided by two AI assistants to the user question displayed below. You should choose the assistant that follows the user's instructions and answers the user's question better. Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of their responses. Begin your evaluation by comparing the two responses and provide a short explanation. Avoid any positional biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your final verdict by strictly following this format: \"[[A]]\" if assistant A is better, \"[[B]]\" if assistant B is better, and \"[[C]]\" for a tie.",
    'likert': f"We would like to request your feedback on the performance of two AI assistants in response to the user question displayed above.Please compare the helpfulness, relevance, accuracy, level of details of their responses. The rating should be from the set of 1, 2, 3, 4, 5, 6, or 7, where higher numbers indicated that Assistant {MODEL_NAMES[1]} was better than Assistant {MODEL_NAMES[0]}. Please first output a single line containing only one value indicating the preference between Assistant {MODEL_NAMES[0]} and {MODEL_NAMES[1]}. In the subsequent line, please provide a brief explanation of your evaluation, avoiding any potential bias and ensuring that the order in which the responses were presented does not affect your judgment."
}


def _append_parts_to_template(template, ans1_parts, ans2_parts, names):
    for i, (a1, a2) in enumerate(zip(ans1_parts, ans2_parts), start=1):
        template += f"""[The Start of Assistant {names[0]}'s Answer part{i}]
                    {a1}
                    [The End of Assistant {names[0]}'s Answer part{i}]

                    [The Start of Assistant {names[1]}'s Answer part{i}]
                    {a2}
                    [The End of Assistant {names[1]}'s Answer part{i}]

                    """
    return template


def split_ans(first_answer, second_answer, question_content, split_num=3, split_type='equal', version='old'):
    assert split_num > 1, "It's necessary to split on more than 2 parts"

    template_init = f"\n[Question]\n{question_content}\n\n"

    if split_type == 'equal':
        len1, len2 = len(first_answer), len(second_answer)
        ans1_parts = [first_answer[i * len1 // split_num:(i + 1) * len1 // split_num] for i in range(split_num)]
        ans2_parts = [second_answer[i * len2 // split_num:(i + 1) * len2 // split_num] for i in range(split_num)]

        template_init += _append_parts_to_template(template_init, ans1_parts, ans2_parts, MODEL_NAMES)

    elif split_type in ['IBM-pure', 'IBM-BERT']:
        model_name = 'pure' if split_type == 'IBM-pure' else 'bert-base-nli-mean-tokens'
        res, _, best_ans1, best_ans2 = IBM6(
            ans1=first_answer,
            ans2=second_answer,
            split_num=split_num,
            model_name=model_name,
            length_penalty=True
        )

        if res:
            template_init += _append_parts_to_template(template_init, best_ans1, best_ans2, MODEL_NAMES)
        else:
            return split_ans(first_answer, second_answer, question_content, split_num=split_num,
                             split_type='equal', version=version)

    prompt = f"{template_init}[System]\n{VERSION_TO_SYSTEM_PROMPT[version]}".replace('\n\n', '\n')

    return prompt