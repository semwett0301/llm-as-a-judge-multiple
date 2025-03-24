def extract_ans(answer, version='old'):
    if answer is None:
        return -1
    if version == 'old':
        try:
            score1 = float(answer.split('\n')[0].split(' ')[0])
            score2 = float(answer.split('\n')[0].split(' ')[1])
            if score1 > score2:
                return 1
            elif score1 < score2:
                return 2
            else:
                return 3
        except:
            return -1
    elif version == 'new':
        if '[[A]]' in answer:
            return 1
        elif '[[B]]' in answer:
            return 2
        elif '[[C]]' in answer:
            return 3
        else:
            return -1
    elif version == 'likert':
        try:
            score = int(answer.split('\n')[0].strip())
            if score < 4:
                return 1
            elif score > 4:
                return 2
            elif score == 4:
                return 3
        except:
            return -1


def extract_ans_rulellm(answer, version='old'):
    """
    :param answer:
    :param version:

    :return: -1 if ans doesn't exist,
    """
    if answer is None:
        return -1
    res = extract_ans(answer, version=version)
    if res != -1:
        return res
    prompt = 'You are given a paragraph of judgement. You are asked to tell me which AI assistant is better according to the judgement. '
    prompt += '[Judgement] '
    prompt += answer
    prompt += '\n return \"[[A]]\" if assistant A is better, return \"[[B]]\" if assistant B is better, and return \"[[C]]\" for a tie. Only return one string.'
    prompt += 'Only return one string in one line, do not explain, do not return two strings.'
    # llmanswer = chatglmchat(question = prompt, temperature = 0)
    # res = extract_ans(llmanswer, version='new')
    return res
