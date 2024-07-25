import os
import fire
from PIL import Image


# DEMO = (
#     'You can convert an image file into pdf file by calling `image_convert_to_pdf` with 2 arguments.\n'
#     '1. The path to the image file: image_file_path: str\n'
#     '2. The path to save the pdf file: pdf_file_path: str\n'
#     "You can call it by: {'app': 'pdf', 'action': 'image_convert_to_pdf', 'image_file_path': ..., 'pdf_file_path': ...}"
# )

DEMO = (
    "convert an image file to a pdf file: "
    "{'app': 'pdf', 'action': 'image_convert_to_pdf', 'image_file_path': [THE_PATH_TO_THE_IMAGE_FILE], 'pdf_file_path': [THE_PATH_TO_THE_PDF_FILE]}"
)


def construct_action(work_dir, args: dict, py_file_path='/apps/pdf_app/image_convert_to_pdf.py'):
    # TODO: not sure if we need to specify the file path with the current workdir
    return f'python3 {py_file_path} --image_file_path {args["image_file_path"]} --pdf_file_path {args["pdf_file_path"]}'


def image_convert_to_pdf(image_file_path, pdf_file_path):
    try:
        # Open the image file
        with Image.open(image_file_path) as img:
            # Convert the image to RGB if it's not already in this mode
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Save the image as a PDF
            img.save(pdf_file_path, 'PDF', resolution=100.0)

        status = "Success"
    except Exception as e:
        # If there's an error, capture the error message in the status
        status = f"Failed: {str(e)}"

    return status

def main(image_file_path, pdf_file_path):
    if not os.path.exists(image_file_path):
        return f'OBSERVATION: The file {image_file_path} does not exist. Failed to convert image to pdf.'

    status = image_convert_to_pdf(image_file_path, pdf_file_path)
    
    return 'OBSERVATION: ' + status

if __name__ == '__main__':
    fire.Fire(main)