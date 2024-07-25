import json
import math
import os
import subprocess

from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, List, Tuple

from intercode.envs.ic_env import (
    IntercodeEnv,
    AGENT_OBS, EVAL_OBS, CORRUPT_GOLD, ACTION_EXEC, REWARD
)
from intercode.utils import get_container, timeout

import logging

# In the future, all of these functions should be imported from a single file
import apps


GIT_RESET_SCRIPT = "git reset --hard; git clean -fd;"
GIT_STATUS_SCRIPT = "git status --short;"

class OfficeAgentEnv(IntercodeEnv):
    """Gym environment for bash shell"""
    name = "officeagent_bash"

    def __init__(self, image_name: str, container_name: str, **kwargs):
        super(OfficeAgentEnv, self).__init__(image_name, container_name, **kwargs)
        # OfficeAgent states
        self.task = kwargs.get("task", '<undefined>')
        self.current_app = None
        self.available_apps = apps.AVAILABLE_APPS
        self.history = []

        self.logger = logging.getLogger(__name__)

    def prepare_docker_env(self, testbed_dir, app_dir):
        self._prepare_docker_testbed(testbed_dir)
        self._prepare_docker_apps(app_dir)

    def _prepare_docker_testbed(self, testbed_dir):
        os.makedirs(testbed_dir, exist_ok=True)
        os.makedirs(f"{testbed_dir}/data", exist_ok=True)
        os.makedirs(f"{testbed_dir}/emails", exist_ok=True)
        os.makedirs(f"{testbed_dir}/calendar", exist_ok=True)
        command = [
            'docker', 'cp', f'{testbed_dir}', f'{self.container_name}:/'
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, f"Prepare Testbed: Failed to copy testbed to container: {result.stderr}" 
    
    def _prepare_docker_apps(self, app_dir):
        command = [
            'docker', 'cp', f'{app_dir}', f'{self.container_name}:/'
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, f"Prepare Apps: Failed to copy apps to container: {result.stderr}"

    def cache_docker_status(self, local_cache_dir, remote_cache_dir="/testbed"):
        os.makedirs(local_cache_dir, exist_ok=True)
        command = [
            'docker', 'cp', f'{self.container_name}:{remote_cache_dir}', f'{local_cache_dir}/'
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, f"Cache Status: Failed to copy cache from container: {result.stderr}"

    def dump_history(self, output_dir):
        with open(f"{output_dir}/env_history.json", "w") as f:
            json.dump(self.history, f, indent=2)
    
    def _write_answer_to_docker(self, answer: str, file_path: str):
        answer = str(answer)
        answer = answer.replace('"', '').replace("'", '')
        command = [
            'docker', 'exec', self.container_name, 'bash', '-c', "echo '{}' > {}".format(answer, file_path)
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        # print('WRITE ANSWER COMMAND:', result)
        assert result.returncode == 0, f"Write Answer: Failed to write answer to container: {result.stderr}"


    def get_available_actions(self) -> List:
        current_app = self.current_app
        available_actions = list(apps.AVAILABLE_ACTIONS[current_app].keys())
        return available_actions

    def reset_container(self) -> None:
        self.workdir = "/"
        exit_code, output = self.container.exec_run(self.clean_cmd(GIT_RESET_SCRIPT))
        if exit_code != 0:
            raise RuntimeError(f"Failed to reset `{self.ctr_name_eval}` container successfully: {output}")

    def check_valid_action(self, action: dict) -> bool:
        """Checks if action is valid"""
        try:
            assert 'app' in action and 'action' in action
            return True
        except AssertionError:
            return False
    
    def _minor_action_fix(self, action):
        proc_action = {}
        for k, v in action.items():
            if isinstance(v, list) and len(v) == 1:
                proc_action[k] = v[0]
            else:
                proc_action[k] = v
        return proc_action

    def exec_action(self, action_string: str) -> None:
        self.observation = None
        try:
            action = eval(action_string)
            action = self._minor_action_fix(action)
            assert self.check_valid_action(action)

            # special case for switch app
            if action['action'] == 'switch_app':
                action['app'] = 'system'

            is_cd_flag = False
            if action["app"] == "shell":
                command = action["command"]
                if isinstance(command, list):
                    command = ' '.join(command)
                is_cd_flag = command.startswith("cd")
                if is_cd_flag:
                    # TODO: What if multiple commands on one line w/ `cd` as first one?
                    cd_arg = command[command.index("cd ")+3:].strip()
                    new_path = self.simplify_path(self.workdir, cd_arg)
                    command = f"cd {new_path}"
            elif action["app"] == "system":
                if action["action"] == "switch_app":
                    self.current_app = action["target_app"]
                    self.observation = f"Successfully switched to app: {self.current_app}"
                elif action["action"] == "finish_task":
                    answer = action.get("answer", 'None')
                    self._write_answer_to_docker(answer, "/testbed/data/answer.txt")
                    self.observation = "Task finished"
                elif action["action"] == 'got_stuck':
                    answer = 'None'
                    self.observation = "Task failed"
                command = None
            else:
                action_module = apps.AVAILABLE_ACTIONS[action["app"]][action["action"]]
                command = action_module.construct_action(self.workdir, args=action)

            if command is not None:
                with timeout():
                    cleaned_cmd = self.clean_cmd(command)
                    self.logger.info(f"Executing command: [{cleaned_cmd}]")
                    exit_code, output = self.container.exec_run(
                        cleaned_cmd,
                        workdir=self.workdir
                    )
                    self.observation = output.decode("utf-8").split('OBSERVATION:')[-1].strip()
                    self.info[ACTION_EXEC] = exit_code == 0

                if is_cd_flag and self.info[ACTION_EXEC]:
                    self.workdir = new_path
                
                if self.observation == "" and action["app"] == "shell":
                    self.observation = f"Successfully executed command: {command}. The output was [{output.decode('utf-8')}]."

            self.history.append((action, self.observation))
        except Exception as e:
            print('!!!!!!!!')
            print(e)
            print('!!!!!!!!')
            self.observation = "Malformed action! You must follow the given action format! Try a different action."
            self.info[ACTION_EXEC] = False
            self.history.append((action_string, self.observation))
        return
            
    def get_reward(self) -> Tuple[float, Dict]:
        """
        The reward currently is calculated as a weighted sum of the following:
        - 0.33: (File System Diff) Difference in file system states between agent, gold command
        - 0.33: (File Content) Verify each file was correctly changed by agent using hashing
        - 0.33: (Observation) Verify that correct output was generated
        """
        # Reset evaluation container state
        exit_code, output = self.container_eval.exec_run(self.clean_cmd(GIT_RESET_SCRIPT))
        if exit_code != 0:
            raise RuntimeError(f"Failed to reset `{self.ctr_name_eval}` container successfully: {output}")
        
        # Run gold command(s) in evaluation container
        self.observation_eval = None
        try:
            if isinstance(self.gold, str):
                self.observation_eval = self.container_eval.exec_run(
                    self.clean_cmd(self.gold)).output.decode("utf-8")
            elif isinstance(self.gold, List):
                self.observation_eval = self.container_eval.exec_run(
                self.clean_cmd(";".join(self.gold))).output.decode("utf-8")
            self.info[CORRUPT_GOLD] = False
        except Exception as e:
            self.info[CORRUPT_GOLD] = True

        # Calculate Rewards
        reward, info = 0.01, {}
        info[REWARD] = {}

        # PART 1: Compare file system states
        diff_agent = self.parse_status(self.container.exec_run(self.clean_cmd(GIT_STATUS_SCRIPT)).output.decode("utf-8"))
        diff_eval = self.parse_status(self.container_eval.exec_run(self.clean_cmd(GIT_STATUS_SCRIPT)).output.decode("utf-8"))
        info["diff_miss"] = list(set(diff_eval) - set(diff_agent))
        info["diff_extra"] = list(set(diff_agent) - set(diff_eval))
        p1_score = round(0.33 * (1 - math.erf(len(info["diff_miss"]) + len(info["diff_extra"]))), 2)
        info[REWARD]["file_diff"] = p1_score
        reward += p1_score

        # PART 2: Check if files changed by both agent, gold commands were modified correctly
        p2_score = 0.33
        # Only check corrects of common changes that were added or modified
        filter_changes = lambda x: (x[1] in ["A", "??", "C"])
        diff_same = [x for x in list(set(diff_agent) & set(diff_eval)) if filter_changes(x)]
        
        if len(diff_same) > 0:
            same_changes = 0
            # Compute hashes for files and folders differently using md5 checksums
            get_hash_cmd = lambda x: f"md5sum {x}" if "." in x else f"md5deep -r {x}"

            for path in diff_same:
                hash_cmd = get_hash_cmd(path[0])
                agent_hash = self.container.exec_run(hash_cmd).output.decode("utf-8")
                gold_hash = self.container_eval.exec_run(hash_cmd).output.decode("utf-8")
                same_changes += 1 if agent_hash == gold_hash else 0
            
            info["diff_same"] = {"files": diff_same, "correct": same_changes, "total": len(diff_same)}
            p2_score = round(0.33 * (same_changes / len(diff_same)), 2)
        info[REWARD]["file_changes"] = p2_score
        reward += p2_score
        
        # PART 3: Compare agent, query answers
        info[AGENT_OBS] = self.observation
        info[EVAL_OBS] = self.observation_eval
        try:
            vect = TfidfVectorizer()
            tfidf = vect.fit_transform([info[AGENT_OBS], info[EVAL_OBS]])
            answer_similarity = tfidf * tfidf.T
            info["answer_similarity"] = answer_similarity.toarray()[0][1]
        except:
            info["answer_similarity"] = 1 if info[AGENT_OBS] == info[EVAL_OBS] else 0
        p3_score = round(0.33 * info["answer_similarity"], 2)
        info[REWARD]["answer_similarity"] = p3_score
        reward += p3_score

        self.reward = reward 
        self.info.update(info)

        self.logger.info(f"Info: {self.info}")
        self.logger.info(f"Reward: {self.reward}")
        return reward, info

    def close(self):
        self.logger.info("Beginning environment shutdown...")
        self.container.stop()
        self.logger.info("Agent, evaluation containers stopped")
    
    ############################
    ### MARK: Helper methods ###
    ############################

    def clean_cmd(self, action: str) -> str:
        """Cleans action string"""
        entrypoint = "/bin/bash" # IMAGE_TO_SETTINGS[self.image_name]
        # TODO: Fix the bracket problems
        # return f"{entrypoint} -c """{action.strip()}""""
        command = '{} -c """ {} """'.format(entrypoint, action.strip())
        print('COMMAND:', command)
        return command

    def parse_status(self, status: str) -> List:
        """Parses git status output into list of changes"""
        status_lst = status.split()
        changes = []
        for i in range(0, len(status_lst), 2):
            changes.append((status_lst[i+1], status_lst[i]))
        return changes

    def simplify_path(self, current: str, changed: str) -> str:
        """Resolves path from current working directory path and the argument of the `cd` command"""
        if not changed:
            return current
        if changed[0] == "/":
            current = ""

        path = []
        
        for segment in (current + "/" + changed).split("/"):
            if segment == "..":
                if path:
                    path.pop()
            elif segment and segment != ".":
                path.append(segment)

        return "/" + "/".join(path)
