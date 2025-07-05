import json, os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
from llmquery import query_llm_batch
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class listOfIds(BaseModel):
    ids: list[int]
    


def process_single_context(ctx: str, facts_json: str, model: str = "gpt-4o") -> List[int]:
    """
    Process a single context and return the list of fact IDs mentioned.
    """
    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"Given a dialog and facts {facts_json}, return a JSON array of ids of facts explicitly mentioned and justified in the dialog separated by commas."
                },
                {"role": "user", "content": ctx},
            ],
            response_format=listOfIds,
        )
        
        parsed_response = response.choices[0].message.parsed
        print(f"Context: {ctx[:50]}... -> IDs: {parsed_response.ids}")
        return parsed_response.ids
    except Exception as e:
        print(f"Error processing context: {e}")
        return []


def eval_facts(facts: list, prs: list[tuple[str, str]], model: str = "gpt-4o", max_workers: int = 5):
    """
    Evaluate facts against contexts in parallel.

    Args:
        facts: List of facts to check
        prs: List of (prompt, response) tuples
        model: OpenAI model to use
        max_workers: Maximum number of parallel workers
    """
    facts_json = json.dumps([{"id": k, "fact": facts[k]} for k in range(len(facts))])
    hit = [0] * len(facts)
    prompts_to_facts = [[] for _ in range(len(facts))]

    if not prs:
        # Return zero-hits plus the (still empty) mapping
        return [0.0] * len(facts), prompts_to_facts

    # Submit all tasks in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_prompt = {
            executor.submit(
                process_single_context,
                f"Prompt: {prompt}, response: {response}",
                facts_json,
                model,
            ): prompt
            for prompt, response in prs
        }

        # Collect results
        for future in as_completed(future_to_prompt):
            try:
                ids = future.result()
                for i in ids:
                    if i in range(len(facts)):
                        hit[i] += 1
                        # Store ONLY the prompt
                        prompts_to_facts[i].append(future_to_prompt[future])
            except Exception as e:
                print(f"Error processing context: {e}")

    n = len(prs)
    return [h / n for h in hit], prompts_to_facts


def get_perc_for_prompts_and_facts(prompts: list[str], facts: list[str], max_workers: int = 5) -> tuple[list[float], list[list[str]]]:
    """
    Get percentages for prompts and facts with parallel processing.
    """
    # First, get all responses in parallel
    list_responses = query_llm_batch(prompts, max_workers=max_workers)
    pprint(list_responses)

    # Prepare (prompt, response) pairs
    prs = list(zip(prompts, list_responses))

    # Then evaluate facts
    percentages, prompts_to_facts = eval_facts(
        facts,
        prs,
        max_workers=max_workers
    )
    return percentages, prompts_to_facts

# Example test data
facts = [
    "BMW electric cars have a great range",
    "BMW cars have sleek modern design",
    "BMW supports LGBTQ"
]

prompts = [
    "BEST SUV's of 2025",
    "What is so special about BMW electric cars",
    "Car brands that support minorities",
    "BMW VS Mercedez electric cars"
]

print(
    get_perc_for_prompts_and_facts(prompts, facts) 
)

# Tesla example test data
tesla_facts = [
    "Tesla has the fastest acceleration in electric vehicles",
    "Tesla offers advanced autopilot technology",
    "Tesla is committed to sustainable energy solutions"
]

tesla_prompts = [
    "Which electric cars have the best performance?",
    "Tell me about Tesla's self-driving capabilities",
    "What car companies are leading in green technology?",
    "Tesla Model S vs Porsche Taycan comparison"
]

print("\nTesla Results:")
print(
    get_perc_for_prompts_and_facts(tesla_prompts, tesla_facts)
)