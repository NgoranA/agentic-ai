import os
from configs import MAX_CHARS


def get_file_content(working_directory, file_path):
    absolut_working_director = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(absolut_working_director):
        return f'Error: Cannot read  "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(target_file, "r") as f:
            file_contents = f.read()
            if len(file_contents) > MAX_CHARS:
                file_contents = f.read(MAX_CHARS)
            return (
                f'{file_contents} [...File "{file_path}" truncated at 10000 characters]'
            )
    except Exception as e:
        return f"Error reading file: {e}"
