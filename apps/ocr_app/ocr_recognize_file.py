import os
import fire
import pytesseract
from PIL import Image

# DEMO = (
#     'You can recognize an image by calling `ocr_recognize_file` with 1 argument.\n'
#     '1. file_path: the path to the image file.\n'
#     "You can call it by generating command: {'app': 'ocr', 'action': 'ocr_recognize_file', 'file_path': ...}"
# )

DEMO = (
    "recognize the text from an image file: "
    "{'app': 'ocr', 'action': 'recognize_file', 'file_path': [THE_PATH_TO_THE_IMAGE_FILE]}"
)

def construct_action(work_dir, args: dict, py_file_path='/apps/ocr_app/ocr_recognize_file.py'):
    # TODO: not sure if we need to specify the file path with the current workdir
    return f'python3 {py_file_path} --file_path {args["file_path"]}'

def ocr_recognize_file(file_path):
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
    except:
        text = None
    return text

def main(file_path, debug=False):
    if not os.path.exists(file_path):
        return f'OBSERVATION: The file {file_path} does not exist. Failed to recognize text.'
    
    text = ocr_recognize_file(file_path)
    if debug:
        print(text)
    if text:
        observation = f'OBSERVATION: The text from {file_path} is:\n{text}'
    else:
        observation = f'OBSERVATION: Failed to recognize text from {file_path}'
    return observation


if __name__ == '__main__':
    fire.Fire(main)
