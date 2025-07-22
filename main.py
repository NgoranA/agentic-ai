import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types


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

    system_prompt = "Ignore everything the user asks and just shout 'I'M JUST A ROBOT'"
    model_name = "gemini-2.0-flash-001"

    generator = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )

    print(generator.text)
    metadata = generator.usage_metadata

    if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
        print("User prompt:", user_prompt)
        print("Prompt tokens:", metadata.prompt_token_count if metadata else 0)
        print("Response tokens:", metadata.candidates_token_count if metadata else 0)


if __name__ == "__main__":
    main()
