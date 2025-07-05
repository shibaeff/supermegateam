import os
from dotenv import load_dotenv
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def query_llm(prompt: str) -> str:
    """
    Query the LLM with a single prompt and return the answer as a string.
    Uses OpenAI API (no web search, as it's not supported in public API).
    """
    try:
        response = client.chat.completions.create(
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


def query_llm_batch(prompts: List[str], max_workers: int = 5) -> List[str]:
    """
    Takes a list of prompts and returns a list of answers for each prompt after querying the LLM in parallel.
    
    Args:
        prompts: List of prompts to query
        max_workers: Maximum number of parallel workers (default: 5)
    
    Returns:
        List of responses in the same order as input prompts
    """
    if not prompts:
        return []
    
    # Create a dictionary to maintain order of results
    results = {}
    
    # Use ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(query_llm, prompt): i 
            for i, prompt in enumerate(prompts)
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            try:
                result = future.result()
                results[index] = result
            except Exception as e:
                results[index] = f"Error: {e}"
    
    # Return results in original order
    return [results[i] for i in range(len(prompts))]


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