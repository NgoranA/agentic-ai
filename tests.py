# from functions.get_files_info import get_files_info
# from functions.get_file_contents import get_file_content
# from functions.write_file import write_file
from functions.run_python_file import run_python_file


def test():
    result = run_python_file("calculator", "main.py")
    print(result)
    result = run_python_file("calculator", "main.py", ["3 + 5"])
    print(result)
    result = run_python_file("calculator", "tests.py")
    print(result)
    result = run_python_file("calculator", "../main.py")
    print(result)
    result = run_python_file("calculator", "nonexistent.py")
    print(result)


if __name__ == "__main__":
    test()
