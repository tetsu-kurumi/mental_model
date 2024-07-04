from dotenv import load_dotenv
import os

load_dotenv()

def get_gpt_apikey():
    gpt_api_key = os.environ.get("OPENAI_API_KEY")
    if gpt_api_key is None:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return gpt_api_key