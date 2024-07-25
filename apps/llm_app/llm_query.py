import fire
import openai
import time


class ChatGPT:
    def __init__(self, model_name, key, system_message=None):
        self.model_name = model_name
        self.key = key
        self.system_message = system_message

    def get_model_options(
        self,
        temperature=0,
        per_example_max_decode_steps=100,
        per_example_top_p=1,
        n_sample=1,
    ):
        return dict(
            temperature=temperature,
            n=n_sample,
            top_p=per_example_top_p,
            max_tokens=per_example_max_decode_steps,
        )

    def generate_plus_with_score(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {"role": "user", "content": prompt},
        ]
        gpt_responses = None
        retry_num = 0
        retry_limit = 2
        error = None
        while gpt_responses is None and retry_num < retry_limit:
            try:
                gpt_responses = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    stop=end_str,
                    api_key=self.key,
                    **options,
                )
                error = None
            except Exception as e:
                error = e
                time.sleep(5)
                retry_num += 1
        if error:
            raise Exception(error)
        results = []
        for i, res in enumerate(gpt_responses["choices"]):
            text = res["message"]["content"]
            results.append(text)

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        result = self.generate_plus_with_score(prompt, options, end_str)[0]
        return result


DEMO = (
    "Query an LLM model for an answer to a given prompt: "
    "{'app': 'llm', 'action': 'complete_text', 'prompt': [PROMPT]}"
)


def construct_action(
    word_dir, args: dict, py_file_path="/apps/llm_app/llm_query.py"
):
    # return f'python3 {py_file_path} --prompt "{args["prompt"]}" '
    return "python3 {} --prompt '''{}'''".format(py_file_path, args["prompt"])


def query(prompt):
    """
    Query an LLM model for an answer to a given prompt.
    """
    try:
        model_name = "gpt-3.5-turbo-0125"
        key = open("/openai_key.txt").read().strip()
        llm = ChatGPT(model_name, key)
        options = llm.get_model_options(
            temperature=0,
            per_example_max_decode_steps=50,
            per_example_top_p=1,
            n_sample=1,
        )
        response = llm.generate(prompt, options)
        return response
    except Exception as e:
        return f"Error: {e}"


def main(prompt):
    response = query(prompt)
    return response


if __name__ == "__main__":
    fire.Fire(main)
