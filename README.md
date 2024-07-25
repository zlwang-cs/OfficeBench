# OfficeBench: Benchmarking Language Agents across Multiple Applications for Office Automation

🖋 **Authors:** [Zilong Wang](https://zilongwang.me), Yuedong Cui, [Li Zhong](https://github.com/FloridSleeves), Zimin Zhang, [Da Yin](https://wadeyin9712.github.io/), [Bill Yuchen Lin](https://yuchenlin.xyz/), [Jingbo Shang](https://shangjingbo1226.github.io/)

We introduce **OfficeBench**, one of the first office automation benchmarks for evaluating current LLM agents' capability to address the office tasks in realistic office workflows. **OfficeBench** requires LLM agents to perform feasible long-horizon planning, proficiently switch between applications in a timely manner, and accurately ground their actions within a large combined action space, based on the contextual demands of the workflow.
 
<p align="center">
<img src=assets/officebench.jpg width=900/>
<p style="text-align: center;"><strong>OfficeBench is one of the first office automation benchmarks for language agents.</strong> We assess the ability of language agents to perform complex office workflows across multiple applications using customized evaluation methods, such as Exact Matching, Fuzzy Matching, and Execution-based Evaluation.</p>
</p>

## 🧩 Architecture
<p align="center">
<img src=assets/architecture.jpg width=850/>
<p style="text-align: center;">The LLM agent leverages the operations from multiple applications to systematically construct an operation chain that addresses the office tasks effectively. The framework is formulated as a transition system where the current application serves as the <em>state</em> and the operations serve as the <em>transitions</em>. Specialized operations, such as <em>read_file</em> and <em>send_email</em>, perform specific tasks. </p>
</p>

## 🛠️ Setup
```
conda create -n officebench python=3.10
pip install -r requirements.txt
```

## 🤖 Run LLM Agent
```shell
# Prepare your OpenAI key in openai_key.txt if you call OpenAI models.
# Prepare your Gemini key in gemini_key.txt if you call Gemini models.
# Launch a vLLM server if you call Llama/Qwen models.
# Check `generate_command.ipynb` to generate your command easily.

python agent_interact.py \
--docker_name {docker_name} \         # docker image name: e.g. officebench
--container_name {container_name} \   # container name: e.g. officebench-test
--model_name {model_name} \           # now supports Openai/Gemini/Llama/Qwen (see below)
--task_dir {task_dir} \               # task directory: e.g. 'tasks/1-20'
--config_file {config_file} \         # config file: e.g. 'tasks/1-20/subtasks/0.json'
--tag {tag} \                         # a unique tag for your current run: e.g. July24-test
--max_iter {max_iter} \               # maximum number of iterations: e.g. 20
--mode {mode}                         # running mode: default/force_new/use_llm_cache (see below)
```

### Supported LLMs
- **OpenAI:** To use the OpenAI API with specific language models, simply specify the [model name](https://platform.openai.com/docs/models), such as `gpt-4-turbo`.
- **Gemini:** Similar to the OpenAI API, you can specify [Gemini models](https://ai.google.dev/gemini-api/docs/models/gemini) by name, for example, `gemini-1.5-pro`.
- **Llama/Qwen:** To use Llama-series or Qwen-series LLMs as a backbone, you must launch an [OpenAI Compatible Server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) from vLLM. Currently, we support only `NousResearch/Meta-Llama-3-70B-Instruct` and `Qwen/Qwen2-72B-Instruct`.

### Running Mode
- **default**: Operates without caching or overriding. Raises an error if results already exist.
- **force_new**: Overrides existing results if found.
- **use_llm_cache**: Loads previous LLM chat history and continues task processing. Useful for extending max_iter after initial experiments.

## ✅ Evaluation

```shell
python evaluation.py \
--model_name {model_name} \           # the LLM you used
--tag_name {tag_name} \               # the tag you used (`--tag` used in agent_interact.py)
```

Final results will be written to `results/{model_name}_{tag_name}_result.jsonl`

## ❤️ Acknowledgement
We greatly thank [InterCode](https://github.com/princeton-nlp/intercode) for providing the awesome agent framwork. We also sincerely appreciate the contributors of the vLLM team for providing the [OpenAI Compatible Server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html) to easily call open-sourced LLMs. 