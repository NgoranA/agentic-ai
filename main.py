import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions import get_files_info, get_file_content, run_python_file, write_file

from functions.get_files_info import (
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
)
from configs import WORKING_DIR, MAX_ITERATIONS


def call_function(function_call_part, verbose=False):
    if verbose is True:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_names_dict = {
        "get_files_info": get_files_info.get_files_info,
        "write_file": write_file.write_file,
        "get_file_content": get_file_content.get_file_content,
        "run_python_file": run_python_file.run_python_file,
    }
    function_name = function_call_part.name
    if function_name not in function_names_dict:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )

    args = dict(function_call_part.args)
    args["working_directory"] = WORKING_DIR
    result = function_names_dict[function_name](**args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": result},
            )
        ],
    )


def main():
    # Load env variables
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    verbose = "--verbose" in sys.argv

    print(sys.argv)

    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

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

    iteration = 0
    while True:
        iteration += 1
        if iteration > MAX_ITERATIONS:
            print(f"Maximum iterations ({MAX_ITERATIONS}) reached.")
            sys.exit(1)
        try:
            #
            # generation starts here #
            #

            generator = client.models.generate_content(
                model=model_name,
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )

            metadata = generator.usage_metadata

            if verbose:
                print("Prompt tokens:", metadata.prompt_token_count if metadata else 0)
                print(
                    "Response tokens:",
                    metadata.candidates_token_count if metadata else 0,
                )

            # if not generator.function_calls:
            #     return generator.text

            responses = []
            if generator.function_calls:
                for function_call in generator.function_calls:
                    result = call_function(function_call_part=function_call)

                    if not result.parts or not result.parts[0].function_response:
                        raise Exception("empty function call result")
                    if verbose:
                        print(f"-> {result.parts[0].function_response.response}")
                    # keep the result for future use by the LLM
                    responses.append(result.parts[0])

            if generator.text:
                print("Final response:")
                print(generator.text)

            # Using the walrus operator to assign generator.candidates to candidates only if it exists and is truthy
            if candidates := getattr(generator, "candidates", None):
                for candidate in candidates:
                    # adding the candidate content to the messages list
                    messages.append(candidate.content)

            if not responses:
                raise Exception("no function responses generated, exiting.")

            messages.append(types.Content(role="tool", parts=responses))
        except Exception as e:
            return f"Error: {e} "


if __name__ == "__main__":
    main()
