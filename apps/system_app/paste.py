import fire

DEMO = (
    'You can paste text that previous get copied to the clipboard by calling `paste` with 0 argument.\n'
    "You can call it by generating command: {'app': 'system', 'action': 'paste'}"
)

def construct_action(work_dir, args: dict, py_file_path='/apps/system_app/paste.py'):
    # TODO: not sure if we need to specify the file path with the current workdir
    return f'python3 {py_file_path} --text {args["text"]}'

def paste():
    # Store the text into a temporary file as clipboard
    try:
        f = open('/tmp/.clipboard', 'r') # TODO: decide which dir to put clipboard
        text = f.read()
        f.close()
    except Exception as e:
        return None
    return text

def main(text, debug=False):
    text = paste()
    if debug:
        print(text)
    if text is None:
        observation = "Failed to paste."
    else:
        observation =  text
    return observation

if __name__ == '__main__':
    fire.Fire(main)
