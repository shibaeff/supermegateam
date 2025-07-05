import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


def query_llm(prompt: str) -> str:
    """
    Query the LLM with a single prompt and return the answer as a string.
    Uses OpenAI API (no web search, as it's not supported in public API).
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides accurate, up-to-date information."
                },
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {e}"


def query_llm_batch(prompts: list[str]) -> list[str]:
    """
    Takes a list of prompts and returns a list of answers for each prompt after querying the LLM.
    """
    return [query_llm(prompt) for prompt in prompts]



def test_query_llm_batch():
    prompts = ["what is the weather in Berlin?"]
    answers = query_llm_batch(prompts)
    print("Prompt:", prompts[0])
    print("Answer:", answers[0])
    assert isinstance(answers, list)
    assert len(answers) == 1
    assert isinstance(answers[0], str)

# Uncomment to run the test manually
# if __name__ == "__main__":
#     test_query_llm_batch()