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
                    "content": f"Given a dialog and facts {facts_json}, return a JSON array of ids of facts explicitly mentioned and justified separated by commas."
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


def eval_facts(facts: list, prs: list, model="gpt-4o", max_workers: int = 5):
    """
    Evaluate facts against contexts in parallel.
    
    Args:
        facts: List of facts to check
        prs: List of contexts to analyze
        model: OpenAI model to use
        max_workers: Maximum number of parallel workers
    """
    facts_json = json.dumps([{"id": k, "fact": facts[k]} for k in range(len(facts))])
    hit = [0] * len(facts)
    
    if not prs:
        return [0.0] * len(facts)
    
    # Process contexts in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_context = {
            executor.submit(process_single_context, ctx, facts_json, model): ctx
            for ctx in prs
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_context):
            try:
                ids = future.result()
                for i in ids:
                    if i in range(len(facts)):
                        hit[i] += 1
            except Exception as e:
                print(f"Error processing context: {e}")
    
    n = len(prs)
    return [h / n for h in hit]


def get_perc_for_prompts_and_facts(prompts: list[str], facts: list[str], max_workers: int = 5) -> list[float]:
    """
    Get percentages for prompts and facts with parallel processing.
    
    Args:
        prompts: List of prompts to query
        facts: List of facts to check
        max_workers: Maximum number of parallel workers
    """
    # First, get all responses in parallel
    list_responses = query_llm_batch(prompts, max_workers=max_workers)
    pprint(list_responses)
    
    # Then evaluate facts in parallel
    percentages = eval_facts(
        facts,
        [
            f"Prompt: {prompt}, response: {response}"
            for (prompt, response) in zip(prompts, list_responses)
        ],
        max_workers=max_workers
    )
    return percentages

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

print(get_perc_for_prompts_and_facts(prompts, facts))