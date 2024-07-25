import json
import os
import fire
import shutil
from datetime import datetime
import pytz

from utils.helper import build_docker
from utils.env import OfficeAgentEnv
from utils.policies import LLMPolicy

from intercode.envs.ic_env import ACTION_EXEC

def main(docker_name='officebench',
         container_name='officebench-debug',
         dockerfile_path='./docker/Dockerfile',
         model_name='gpt-4o-2024-05-13',
         task_dir='tasks/1-1',
         config_file='tasks/1-1/subtasks/0.json',
         task=None,
         tag=None,
         max_iter=20,
         mode='default'):
    build_docker(docker_name, dockerfile_path)

    config = json.load(open(config_file))
    task = config.get('task', task)
    subtask_id = config_file.split('/')[-1].split('.')[0]
    if tag is None:
        timezone = pytz.timezone('America/Los_Angeles')
        tag = datetime.now(timezone).strftime('%Y%m%d%H%M%S')
    output_dir = f'{task_dir}/outputs/{subtask_id}/{model_name}_{tag}'
    
    assert mode in ['force_new', 'use_llm_cache', 'default']
    if mode == 'force_new':
        force_new = True
        use_llm_cache = False
    elif mode == 'use_llm_cache':
        force_new = False
        use_llm_cache = True
    else:
        force_new = False
        use_llm_cache = False

    if os.path.exists(output_dir) and use_llm_cache and not force_new:
        assert os.path.exists(f'{output_dir}/llm_history.json'), f"LLM history not found: {output_dir}/llm_history.json"
        llm_cache = {}
        llm_history = json.load(open(f'{output_dir}/llm_history.json'))
        for item in llm_history:
            llm_cache[item[1]] = item[2]
    else:
        llm_cache = None

    if os.path.exists(output_dir) and not force_new and not use_llm_cache:
        print(f"Output directory already exists: {output_dir}")
        return
    
    if os.path.exists(output_dir) and force_new:
        print(f"Force new mode: removing existing output directory: {output_dir}")
        shutil.rmtree(output_dir)

    env = OfficeAgentEnv(image_name=docker_name, 
                         container_name=container_name,
                         task=task,
                         verbose=True)
    env.reset()
    env.prepare_docker_env(
        testbed_dir=f'{task_dir}/testbed/',
        app_dir=f'apps/',
    )
    env.cache_docker_status(local_cache_dir=f'{task_dir}/cache/{subtask_id}/')

    if 'gpt' in model_name:
        api_key = open('openai_key.txt').read().strip()
    elif 'gemini' in model_name:
        api_key = open('gemini_key.txt').read().strip()
    else:
        api_key = ""

    policy = LLMPolicy(
        model_name=model_name,
        key=api_key,
        env=env,
        config=config,
        llm_cache=llm_cache,
        debug_mode=True,
    )
    try:
        obs = env.observation
        done = False
        n_iter = 0
        while not done:
            n_iter += 1
            action = policy.forward(env)
            obs, reward, done, info = env.step(action)
            if n_iter >= max_iter:
                print(f"Max iterations reached: {max_iter}")
                break
    except KeyboardInterrupt:
        print("Exiting InterCode environment...")
    
    os.makedirs(output_dir, exist_ok=True)
    env.cache_docker_status(local_cache_dir=output_dir)
    env.dump_history(output_dir)
    policy.dump_history(output_dir)
    with open(f'{output_dir}/settings.json', 'w') as f:
        json.dump(config | {'model_name': model_name}, f, indent=2)
    
    env.close()

if __name__ == '__main__':
    fire.Fire(main)
