import fire

DEMO = (
    'You can copy text by calling `copy` with 1 argument.\n'
    '1. text: the text you want to copy.\n'
    "You can call it by generating command: {'app': 'system', 'action': 'copy', 'text': ...}"
)

def construct_action(work_dir, args: dict, py_file_path='/apps/system_app/copy.py'):
    # TODO: not sure if we need to specify the file path with the current workdir
    return f'python3 {py_file_path} --text {args["text"]}'

def copy(text):
    # Store the text into a temporary file as clipboard
    try:
        f = open('/tmp/.clipboard', 'w') # TODO: decide which dir to put clipboard
        f.write(text)
        f.close()
    except Exception as e:
        return False
    return True

def main(text, debug=False):
    success = copy(text)
    if debug:
        print(text)
    if not success:
        observation = "Failed to copy the text."
    else:
        observation =  "Text copied successfully."
    return observation

if __name__ == '__main__':
    fire.Fire(main)
