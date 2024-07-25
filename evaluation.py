import glob
import fire
import json
import os
from utils.evaluate import (
    evaluate_contain, 
    evaluate_not_contain,
    evaluate_file_exist, 
    evaluate_file_not_exist, 
    evaluate_diff_contain_text, 
    evaluate_excel_cell_value, 
    evaluate_excel_cell_comparator,
    evaluate_exact_match,
    evaluate_calendar_no_overlap
)

def evaluate_output(task_id, subtask_id, output_dir):
    print(f"Evaluating {task_id} {subtask_id} {output_dir}...")
    config_path = f"./tasks/{task_id}/subtasks/{subtask_id}.json"
    config = json.load(open(config_path))
    eval_config = config['evaluation']
    for eval_item in eval_config:
        function = eval_item['function']
        args = eval_item['args']
        if not eval(f"{function}(output_dir, args)"):
            print(f"Failed: {function} {args}")
            return False
    return True

def main(model_name='gpt-4o-2024-05-13', tag_name='test', result_dir='./results', output_subdir='outputs'):
    results_dict = {
        "1": [],
        "2": [],
        "3": []
    }
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    all_tasks_info = []
    unfound_result_cases = []
    result_path = f'{result_dir}/{model_name}_{tag_name}_result.jsonl'
    
    f_result = open(result_path, 'w')

    all_config_filepaths = glob.glob(f"./tasks/*/subtasks/*.json")
    for config_filepath in all_config_filepaths:
        # ./tasks/1-1/subtasks/0.json
        task_id = config_filepath.split('/')[2]
        subtask_id = config_filepath.split('/')[4].split('.')[0]
        all_tasks_info.append((task_id, subtask_id))
    
    all_tasks_info = sorted(all_tasks_info, key=lambda x: tuple(map(int, x[0].split('-'))) + (int(x[1]),))
    
    for task_id, subtask_id in all_tasks_info:
        num_app_tag = task_id[0]
        # ./tasks/3-42/outputs/0/gemini-1.5-pro_jun11-gemini/testbed/
        result_testbed_dir = f"./tasks/{task_id}/{output_subdir}/{subtask_id}/{model_name}_{tag_name}/testbed"
        if os.path.exists(result_testbed_dir):
            print(f"Found {result_testbed_dir}")
            try:
                is_pass = evaluate_output(task_id, subtask_id, result_testbed_dir)
            except Exception as e:
                is_pass = False
                print(f"!!! Error: {e}")
        else:
            print(f"Not Found {result_testbed_dir}")
            unfound_result_cases.append((task_id, subtask_id))
            is_pass = False
        print(f"task_id: {task_id}, subtask_id: {subtask_id}, is_pass: {is_pass}")
        f_result.write(json.dumps({"task_id": task_id, "subtask_id": subtask_id, "is_pass": is_pass}) + '\n')
        results_dict[num_app_tag].append(1 if is_pass else 0)
        print("====================================")

    f_result.close()

    # print results
    print(model_name, tag_name)
    for num_app_tag in results_dict:
        results = results_dict[num_app_tag]
        print(f"Num_App_Tag {num_app_tag}: {sum(results)}/{len(results)}={sum(results)/len(results)*100:.3f}%")
    overall_results = results_dict['1'] + results_dict['2'] + results_dict['3']
    print(f"Overall: {sum(overall_results)}/{len(overall_results)}={sum(overall_results)/len(overall_results)*100:.3f}%")
    print("====================================")
    print(f"Unfound result cases:")
    for task_id, subtask_id in sorted(unfound_result_cases, key=lambda x: tuple(map(int, x[0].split('-'))) + (int(subtask_id),)):
        print(f"{task_id} {subtask_id}")
    print('Total unfound result cases:', len(unfound_result_cases))

if __name__ == '__main__':
    fire.Fire(main)
