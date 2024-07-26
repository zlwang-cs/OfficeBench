# OfficeBench: Benchmarking Language Agents across Multiple Applications for Office Automation

🖋 **Authors:** [Zilong Wang](https://zilongwang.me), Yuedong Cui, [Li Zhong](https://github.com/FloridSleeves), Zimin Zhang, [Da Yin](https://wadeyin9712.github.io/), [Bill Yuchen Lin](https://yuchenlin.xyz/), [Jingbo Shang](https://shangjingbo1226.github.io/)

We introduce **OfficeBench**, one of the first office automation benchmarks for evaluating current LLM agents' capability to address office tasks in realistic office workflows. **OfficeBench** requires LLM agents to perform feasible long-horizon planning, proficiently switch between applications in a timely manner, and accurately ground their actions within a large combined action space, based on the contextual demands of the workflow.

<p align="center">
<img src=assets/officebench.jpg width=900/>
</p>

**OfficeBench is one of the first office automation benchmarks for language agents.** We assess the ability of language agents to perform complex office workflows across multiple applications using customized evaluation methods, such as Exact Matching, Fuzzy Matching, and Execution-based Evaluation.

## 🧩 Architecture

<p align="center">
<img src=assets/architecture.jpg width=900/>
</p>

The LLM agent leverages the operations from multiple applications to construct an operation chain that effectively addresses office tasks. **The framework is formulated as a transition system where the current application serves as the _state_ and the operations serve as the _transitions_.** Specialized operations, such as `read_file` and `send_email`, perform specific tasks.

## 📈 Leaderboard
*`X App(s)` indicates the number of apps the task requires. `(X)` indicates the number of tasks in this category.*

| LLM Agents                                | Single App (93) | Two Apps (95) | Three Apps (112) | Overall (300) |
| ----------------------------------------- | --------------- | ------------- | ---------------- | ------------- |
| **Proprietary Models**                    |                 |               |                  |               |
| Gemni-1.0 Pro (Feb 2024)                  | 24.73           | 13.68         | 0.89             | 12.33         |
| Gemni-1.5 Flash (May 2024)                | 34.41           | 24.21         | 0.89             | 18.67         |
| Gemni-1.5 Pro (May 2024)                  | 41.94           | 32.63         | 7.14             | 26.00         |
| GPT-3.5 Turbo (0125)                      | 8.60            | 7.45          | 0.89             | 5.35          |
| GPT-4 Turbo (2024-04-09)                  | 56.99           | 50.63         | 11.61            | 38.00         |
| GPT-4 Omni (2024-05-13)                   | 64.52           | 60.00         | 21.43            | 47.00         |
| **Open-weights Models**                   |                 |               |                  |               |
| Llama 3 (70B-Instruct)                    | 39.79           | 41.05         | 5.36             | 27.33         |
| Qwen 2 (72B-Instruct)                     | 30.23           | 28.42         | 8.04             | 21.16         |

*(Note: This leaderboard will be continuously updated as new data and model updates become available.)*

## 🛠️ Setup

```
conda create -n officebench python=3.10
pip install -r requirements.txt
```

## 🤖 Run LLM Agent

```shell
# Prepare your OpenAI key in openai_key.txt if you call OpenAI models.
# Prepare your Gemini key in gemini_key.txt if you call Gemini models.
# Launch a vLLM server if you call models from Huggingface.
# Check `generate_command.ipynb` to generate your customized commands easily.

python agent_interact.py \
--docker_name {docker_name} \         # docker image name: e.g. officebench
--container_name {container_name} \   # container name: e.g. officebench-test
--model_name {model_name} \           # now supports Openai/Gemini/vLLM (see below)
--task_dir {task_dir} \               # task directory: e.g. 'tasks/1-20'
--config_file {config_file} \         # config file: e.g. 'tasks/1-20/subtasks/0.json'
--tag {tag} \                         # a unique tag for your current run: e.g. July24-test
--max_iter {max_iter} \               # maximum number of iterations: e.g. 20
--mode {mode}                         # running mode: default/force_new/use_llm_cache (see below)
```

### Supported LLMs

- **OpenAI:** To use the OpenAI API with specific language models, simply specify the [model name](https://platform.openai.com/docs/models), such as `gpt-4-turbo`.
- **Gemini:** Similar to the OpenAI API, you can specify [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini) by name, for example, `gemini-1.5-pro`.
- **vLLM:** To use LLMs from [Huggingface](https://huggingface.co/models) as the backbone, you must launch an [OpenAI Compatible Server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) from vLLM.

### Running Mode

- **default**: Operates without caching or overriding. Raises an error if results already exist.
- **force_new**: Overrides existing results if found.
- **use_llm_cache**: Loads previous LLM chat history and continues task processing. Useful for extending max_iter after initial experiments.

### Task Naming

The annotated tasks can be found in `tasks/{app_num}-{task_id}/subtask/{subtask_id}.json`, which includes the *task decription* and *evaluation methods*.

## ✅ Evaluation

```shell
python evaluation.py \
--model_name {model_name} \           # the LLM you used (`--model_name` used in agent_interact.py)
--tag_name {tag_name} \               # the tag you used (`--tag` used in agent_interact.py)
```

Final results will be written to `results/{model_name}_{tag_name}_result.jsonl`

## ❤️ Acknowledgement

We greatly thank [InterCode](https://github.com/princeton-nlp/intercode) for providing the awesome agent framwork. We also sincerely appreciate the contributors of the vLLM team for providing the [OpenAI Compatible Server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) to easily call open-sourced LLMs.
