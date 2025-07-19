import os
import subprocess


def run_python_file(working_directory, file_path, args=[]):
    absolut_working_director = os.path.abspath(working_directory)
    target_file = os.path.abspath(os.path.join(working_directory, file_path))
    if not target_file.startswith(absolut_working_director):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(target_file):
        return f'Error: File "{file_path}" not found.'
    if not target_file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        complete_child_process = subprocess.run(
            args,
            executable=target_file,
            capture_output=True,
            timeout=30,
            cwd=absolut_working_director,
        )
        if not complete_child_process:
            return "No output produced"
        return f"STDOUT: {complete_child_process.stdout} STDERR: {complete_child_process.stderr}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
