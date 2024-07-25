import openai
import time
import numpy as np
import google.generativeai as genai

class ChatGPT:
    def __init__(self, model_name, key, system_message=None):
        self.model_name = model_name
        self.key = key
        self.system_message = system_message

    def get_model_options(
        self,
        temperature=0,
        per_example_max_decode_steps=1024,
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
                "content": "I will give you some examples, you need to follow the examples and complete the text, and no other content." if self.system_message is None else self.system_message,
            },
            {"role": "user", "content": prompt},
        ]
        gpt_responses = None
        retry_num = 0
        retry_limit = 2
        error = None
        while gpt_responses is None:
            try:
                gpt_responses = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    stop=end_str,
                    api_key=self.key,
                    **options
                )
                error = None
            except Exception as e:
                print(str(e), flush=True)
                error = str(e)
                if "This model's maximum context length is" in str(e):
                    print(e, flush=True)
                    gpt_responses = {
                        "choices": [{"message": {"content": "PLACEHOLDER"}}]
                    }
                elif retry_num > retry_limit:
                    error = "too many retry times"
                    gpt_responses = {
                        "choices": [{"message": {"content": "PLACEHOLDER"}}]
                    }
                else:
                    time.sleep(60)
                retry_num += 1
        if error:
            raise Exception(error)
        results = []
        for i, res in enumerate(gpt_responses["choices"]):
            text = res["message"]["content"]
            fake_conf = (len(gpt_responses["choices"]) - i) / len(
                gpt_responses["choices"]
            )
            results.append((text, np.log(fake_conf)))

        return results

    def generate(self, prompt, options=None, end_str=None):
        if options is None:
            options = self.get_model_options()
        options["n"] = 1
        result = self.generate_plus_with_score(prompt, options, end_str)[0][0]
        return result
    


class Gemini:
    # gemini-1.0-pro
    # gemini-1.5-pro
    def __init__(self, model_name, key, system_message=None):
        self.model_name = model_name
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel(model_name)
        self.system_message = system_message
    
    def generate(self, prompt):
        combined_prompt = f"{self.system_message}\n\n{prompt}" if self.system_message else prompt
        response = self.model.generate_content(
            combined_prompt,
            generation_config=genai.types.GenerationConfig(
                # Only one candidate for now.
                candidate_count=1,
                max_output_tokens=1024,
                temperature=1.0)
        )
        return response.text
    

class LLAMA:
    def __init__(self, model_name, system_message=None):
        self.model_name = model_name
        self.model = openai.OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="token-abc123",
        )
        self.system_message = system_message
    
    def generate(self, prompt):
        try:
            completion = self.model.chat.completions.create(
                model="NousResearch/Meta-Llama-3-70B-Instruct",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print('Generation Error:', e)
            return 'None'
    

class Qwen:
    def __init__(self, model_name, system_message=None):
        self.model_name = model_name
        self.model = openai.OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="token-abc123",
        )
        self.system_message = system_message
    
    def generate(self, prompt):
        completion = self.model.chat.completions.create(
            model="Qwen/Qwen2-72B-Instruct",
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    

class Mixtral:
    def __init__(self, model_name, system_message=None):
        self.model_name = model_name
        self.model = openai.OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="token-abc123",
        )
        self.system_message = system_message
    
    def generate(self, prompt):
        try:
            completion = self.model.chat.completions.create(
                model="mistralai/Mixtral-8x22B-v0.1",
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print('Generation Error:', e)
            return 'None'