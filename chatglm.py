from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True).half().cuda()
model = model.eval()

def chatglmchat(question, temperature = 0.7, max_length = 4000):


    if temperature!= 0 :
        response, history = model.chat(tokenizer, question, history=[], temperature=temperature, max_length = max_length)
    else:
        response, history = model.chat(tokenizer, question, history=[], max_length = max_length)

    return response