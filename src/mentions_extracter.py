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
    

# In-memory cache for process_single_context
_context_cache = {}

def process_single_context(ctx: str, facts_json: str, model: str = "gpt-4o") -> List[int]:
    """
    Process a single context and return the list of fact IDs mentioned.
    Uses in-memory cache for repeated queries.
    """
    cache_key = (ctx, facts_json, model)
    if cache_key in _context_cache:
        return _context_cache[cache_key]
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
        _context_cache[cache_key] = parsed_response.ids
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


def get_all_for_prompts_and_facts(prompts: list[str], facts: list[str], max_workers: int = 5):
    """
    Extended version: returns all intermediate data for debugging/analysis.
    Returns:
        {
            'responses': list of LLM responses,
            'prompt_response_pairs': list of context strings,
            'fact_ids_per_context': list of lists of fact IDs per context,
            'percentages': final percentages per fact
        }
    """
    # Get all responses in parallel
    list_responses = query_llm_batch(prompts, max_workers=max_workers)
    prompt_response_pairs = [
        f"Prompt: {prompt}, response: {response}"
        for (prompt, response) in zip(prompts, list_responses)
    ]
    
    facts_json = json.dumps([{"id": k, "fact": facts[k]} for k in range(len(facts))])
    fact_ids_per_context = []
    
    # Process each context and collect fact IDs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_single_context, ctx, facts_json)
            for ctx in prompt_response_pairs
        ]
        for future in as_completed(futures):
            # To preserve order, we need to map futures to their index
            pass  # We'll fix order below
    # Instead, do ordered collection:
    fact_ids_per_context = [process_single_context(ctx, facts_json) for ctx in prompt_response_pairs]
    
    # Calculate percentages as before
    hit = [0] * len(facts)
    for ids in fact_ids_per_context:
        for i in ids:
            if i in range(len(facts)):
                hit[i] += 1
    n = len(prompt_response_pairs)
    percentages = [h / n if n > 0 else 0.0 for h in hit]
    
    return {
        'responses': list_responses,
        'prompt_response_pairs': prompt_response_pairs,
        'fact_ids_per_context': fact_ids_per_context,
        'percentages': percentages
    }

"""
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
"""