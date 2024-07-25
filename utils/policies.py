import json
import apps

from utils.llm import ChatGPT, Gemini, LLAMA, Qwen, Mixtral

import logging


class BasePolicy:
    def __init__(self):
        pass

    def forward(self, *args, **kwargs):
        raise NotImplementedError
    
class HumanPolicy(BasePolicy):
    def __init__(self):
        super().__init__()
    
    def forward(self, query, observation, available_actions):
        action = input('> ')
        return action


PROMPT_DICT = {
    'prompt_undecided_app': (
        '##Task: {task}\n'
        '##Available apps: {available_apps}\n'
        '##Instruction:\n'
        " - choose an app from the avaiblable apps: {{'app': 'system', 'action': 'switch_app', 'target_app': [THE_APP_YOU_CHOOSE]}}\n"
        '##Command:'
    ),
    'prompt_undecided_app_w_history': (
        '##Task: {task}\n'
        '##History:\n'
        '{history}'
        '##Available apps: {available_apps}\n'
        '##Instruction:\n'
        " - choose an app from the avaiblable apps: {{'app': 'system', 'action': 'switch_app', 'target_app': [THE_APP_YOU_CHOOSE]}}\n"
        '##Command:'
    ),
    'prompt_decided_app': (
        '##Task: {task}\n'
        '##History:\n'
        '{history}'
        '##Current apps: {current_app}\n'
        '##Instruction: Choose one action from the list as the next step.\n'
        '{detailed_instruction}'
        " - switch to another app among {available_apps}: {{'app': 'system', 'action': 'switch_app', 'target_app': [THE_APP_YOU_CHOOSE]}}\n"
        " - finish the task with your answer as None if the task is not a question: {{'app': 'system', 'action': 'finish_task', 'answer': 'None'}}\n"
        " - finish the task with your answer if the task is a question: {{'app': 'system', 'action': 'finish_task', 'answer': [ANSWER]}}\n"
        '##Command:'
    )
}

class LLMPolicy(BasePolicy):
    def __init__(self, model_name, key, env, config, llm_cache=None, debug_mode=False):
        super().__init__()

        self.system_message = self.construct_system_message(config, env.available_apps)
        if 'gpt' in model_name:
            self.llm = ChatGPT(model_name, key, self.system_message)
        elif 'gemini' in model_name:
            self.llm = Gemini(model_name, key, self.system_message)
        elif 'Llama-3' in model_name:
            self.llm = LLAMA(model_name, self.system_message)
        elif 'Qwen' in model_name:
            self.llm = Qwen(model_name, self.system_message)
        elif 'Mixtral' in model_name:
            self.llm = Mixtral(model_name, self.system_message)
        else:
            raise NotImplementedError
        self.llm_history = []

        self.action_window = []
        self.action_window_size = 5

        self.llm_cache = llm_cache

        self.logger = logging.getLogger(__name__)

        self.debug_mode = debug_mode

    def dump_history(self, output_dir):
        with open(f'{output_dir}/llm_history.json', 'w') as f:
            json.dump(self.llm_history, f, indent=2)

    def construct_system_message(self, config, available_apps):
        app_introduction = ''
        for app in available_apps:
            app_introduction += f' - {apps.AVAILABLE_APPS[app].INTRO}\n'
        username = config['username']
        date = config['date']
        weekday = config['weekday']
        time = config['time']        
        system_message = (
            f"Today is {date} ({weekday}). The current time is {time}. You are an AI assistant for user {username}.\n"
            "You can help solve the task step by step.\n"
            "You can interact with an operation system and use apps to solve the task.\n"
            "You must follow the instructions and use the given json format to call APIs.\n"
            "You can only generate one action at a time.\n"
            "You can find files for your task in `/testbed/data`. If you don't know the filenames, please switch to shell app and call commands to list the directory.\n"
            "You have following apps installed in the system:\n"
            f"{app_introduction}"
        ).strip()
        return system_message

    def proc_action(self, action):
        if '{' not in action or '}' not in action:
            return action
        left = action.find('{')
        right = action.rfind('}') + 1
        action = action[left:right]
        return action

    def forward(self, env):
        prompt = self.build_prompt(env)
        if self.llm_cache:
            if prompt in self.llm_cache:
                print('!!!')
                print('LLM Cache Hit!')
                print('!!!')
                response = self.llm_cache[prompt]
            else:
                response = self.llm.generate(prompt)
        else:
            response = self.llm.generate(prompt)

        self.llm_history.append((self.system_message, prompt, response))

        if self.debug_mode:
            print('\n\n' + '>'*20)
            print(f'System: {self.system_message}')
            print(f'Prompt: {prompt}')
            print(f'Response: {response}')
            print('<'*20 + '\n\n')

        action = self.proc_action(response)
        if action == '':
            action = response

        self.action_window.append(action)
        self.action_window = self.action_window[-self.action_window_size:]
        if len(self.action_window) >= self.action_window_size and all([action == self.action_window[0] for action in self.action_window]):
            self.logger.warning(f"LLM Policy: Action stuck in the action window: {action}")
            action = repr({'app': 'system', 'action': 'got_stuck'})   

        return action
    
    def build_prompt(self, env):
        if env.current_app is None:
            if len(env.history) == 0:
                prompt = PROMPT_DICT['prompt_undecided_app'].format_map({
                    'task': env.task,
                    'available_apps': list(env.available_apps.keys()),
                })
            else:
                # construct history
                history = ''
                for i, (action, observation) in enumerate(env.history):
                    if observation:
                        observation = observation.replace('\n', '\\n')
                        history += f' - Step {i}: {action} -> [{observation}]\n'
                    else:
                        history += f' - Step {i}: {action}\n'
                prompt = PROMPT_DICT['prompt_undecided_app_w_history'].format_map({
                    'task': env.task,
                    'history': history,
                    'available_apps': list(env.available_apps.keys()),
                })
        else:
            # construct history
            history = ''
            for i, (action, observation) in enumerate(env.history):
                if observation:
                    observation = observation.replace('\n', '\\n')
                    history += f' - Step {i}: {action} -> [{observation}]\n'
                else:
                    history += f' - Step {i}: {action}\n'
            # construct detailed instruction
            detailed_instruction = ''
            for action in env.get_available_actions():
                action_module = apps.AVAILABLE_ACTIONS[env.current_app][action]
                detailed_instruction += f" - {action_module.DEMO}\n"
            avaiblable_apps = [app for app in env.available_apps.keys() if app != env.current_app]
            prompt = PROMPT_DICT['prompt_decided_app'].format_map({
                'task': env.task,
                'history': history,
                'current_app': env.current_app,
                'detailed_instruction': detailed_instruction,
                'available_apps': avaiblable_apps,
            })

        return prompt


