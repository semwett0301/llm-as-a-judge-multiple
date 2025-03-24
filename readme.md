

This repository contains the code for evaluating the ICLR2024 submission. The supported language models (LLMs) and judges are listed below:

Supported judges: 'gpt-3.5-turbo', 'chatglm', 'qwen', 'minimax', 'claude2', 'llama2-70b', 'llama2-7b', 'llama2-13b', 'gpt4'

Supported LLM answer pairs:

models = [['gpt-3.5-turbo', 'claude-v1'], ['llama-13b', 'vicuna-13b'], ['alpaca-13b', 'vicuna-13b'], 
          ['gpt-3.5-turbo', 'gpt-4'], ['gpt-4', 'claude-v1'], ['vicuna-13b', 'vicuna-7b'], 
          ['vicuna-7b', 'alpaca-13b'], ['gpt-4', 'vicuna-13b']]



## Preparation

- Install [chatglm2](https://github.com/THUDM/ChatGLM2-6B) for answer extractor, making sure that you have at least one NVIDIA GPU on your server.

- Download the question and answers from different LLMs from the [Vicuna](https://github.com/lm-sys/FastChat/tree/main/fastchat/llm_judge/data) repository. If you encounter network issues, we provide a backup. 
**./llm_judge_repo_data/quesitons/question.jsonl**

- Download the answer results we provided from different LLM judges (evaluators). Note that the original file exceeds the maximum file size of Supplementary Material and the Anonymous Github repo file size. 
You can unzip **./llm_judge_repo_data/vicuna_bench/order_change_judgment.7z**, password is ``iclr2024''
If you do not wish to download or unzip, you can use the excel file we provided for evaluation.

- conda env install, please refer to **./iclr2024.yaml**, note that we delete the username and env name to satisfy the requirement of anonymous submisson.

## Execution

Run the GetExcel.py file to convert the answer results into an excel file (optional, as we have already provided the excel file).

```sh
CUDA_VISIBLE_DEVICES=0 python GetExcel.py
```

Note that if you do not have a GPU, you can use the excel file we provided for evaluation.

For the main result table, run the following command:

```sh
CUDA_VISIBLE_DEVICES=0 python RQ_gen_table.py --RQ1
```

For the ablation study, run the following command:

```sh
CUDA_VISIBLE_DEVICES=0 python RQ_gen_table.py --RQ2
```

For figure 2 (a) and (b), run the following commands:

```sh
CUDA_VISIBLE_DEVICES=0 python RQ_IO4K.py --PIC1
CUDA_VISIBLE_DEVICES=0 python RQ_IO4K.py --PIC2
```


The human study results are located in split_and_merge_sub/human_result/Final.txt


## Other Information

We have only tested our code on a GPU server with an Intel Xeon Platinum 8276 CPU, 256GB of RAM, and 4 NVIDIA A100 GPUs.



## Responsible Usage


Throughout our experiment, we have been diligent in ensuring that we adhere to the highest ethical standards and legal regulations of scientific research. We have taken great care to ensure that our research does not infringe upon the rights of any individuals or exacerbate any potential biases in LLMs.

To this end, all of the data we have used in our research come from open-source datasets that have undergone rigorous scrutiny and authorization. We have made sure that the data we use are reliable and accurate, and we have taken steps to ensure that they do not cause any harm to society.

We believe that it is important to encourage the reasonable use of our dataset and to oppose any form of misuse. We understand that the data we have collected may be of great value to researchers and scholars in various fields, and we are committed to making this data available to them in a responsible and ethical manner.

In conclusion, we take our responsibility as researchers very seriously and are committed to upholding the highest standards of ethical conduct in all aspects of our work. We believe that our research can make a positive contribution to society, and we are dedicated to ensuring that it is used in a responsible and beneficial way.


## Disclaimer

Our experiment aims to improve the consistency of LLM evaluators to more accurately assess the quality of AI-generated answers. We believe that mitigating positional biases in LLM evaluators is an initial step towards addressing higher-level biases in AI systems, including gender and racial biases. More consistent LLM evaluators can provide human-like evaluations at a lower cost, supplying feedback to reduce biases during training. **However, we recognize that malicious actors could exploit these methods to intentionally train models that go against human values.** Open-source LLM evaluators could be leveraged as consistent evaluators to guide the training of harmful models such as Worm-GPT. While our work targets constructive applications, we caution that, like any technology, consistent LLM evaluators could potentially be misused. Researchers should consider ethical implications and preventative measures. Overall, we believe the benefits of more fair and accurate AI outweigh the risks, but responsibility is required in deployment.

We guarantee that our results are reproducible, and all experimental details, including hyperparameters. We encourage other researchers to make reasonable use of our dataset, but please note that ethical standards and legal regulations must be followed. We are not responsible for the use of our dataset by other researchers and **do not assume any legal liability**.