import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import (
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
)


def main():
    # Load env variables
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    print(sys.argv)
    if len(sys.argv) == 1:
        print("You need to provide a command for me")
        exit(1)

    # user prompt
    user_prompt = sys.argv[1]

    # Create a new list of types.Content, and set the user's prompt as the only message (for now):
    # We will use it later to keep track of the converstion between the user and the LLM

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    # Create an instance of the Gemini Client
    client = genai.Client(api_key=api_key)

    # We now need to use a model's method to get response from the gemini-2.0-flash-001 model
    # We need teo name parameters: model and contents

    system_prompt = """
    You are a helpful AI coding agent.

    When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

    - List files and directories
    - Read file contents
    - Execute Python files with optional arguments
    - Write or overwrite files

    All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
    """

    model_name = "gemini-2.0-flash-001"

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_run_python_file,
            schema_get_file_content,
            schema_write_file,
        ]
    )

    generator = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    print(generator.text)
    print("")

    if generator.function_calls is not None:
        for function_call_part in generator.function_calls:
            print(
                f"Calling function: {function_call_part.name} ({function_call_part.args})"
            )

    metadata = generator.usage_metadata

    if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
        print("User prompt:", user_prompt)
        print("Prompt tokens:", metadata.prompt_token_count if metadata else 0)
        print("Response tokens:", metadata.candidates_token_count if metadata else 0)


if __name__ == "__main__":
    main()
