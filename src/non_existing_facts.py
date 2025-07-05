import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from llmquery import query_llm_batch

# --------------------------------------------------------------------------- #
#  Initialisation                                                             #
# --------------------------------------------------------------------------- #
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --------------------------------------------------------------------------- #
#  Pydantic response schemas                                                  #
# --------------------------------------------------------------------------- #
class FactsList(BaseModel):
    """Structured output for the fact-extraction step."""
    facts: List[str]


class HallucinatedIdxs(BaseModel):
    """Structured output for the verification step."""
    hallucinated_idxs: List[int]


# --------------------------------------------------------------------------- #
#  Helper functions                                                           #
# --------------------------------------------------------------------------- #
def _extract_facts(text: str, *, model: str = "gpt-4o") -> List[str]:
    """
    Ask the LLM to extract all explicit, objective facts that appear in `text`.
    Returns them as a plain Python list.
    """
    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract every objective, verifiable fact explicitly stated "
                        "in the assistant response. Return JSON in the form "
                        '{"facts": ["fact 1", "fact 2", ...]}.'
                    ),
                },
                {"role": "user", "content": text},
            ],
            response_format=FactsList,
        )
        return response.choices[0].message.parsed.facts
    except Exception as e:
        print(f"[FACT-EXTRACTION ERROR] {e}")
        return []


def _check_hallucinations(
    facts: List[str], website: str, *, model: str = "gpt-4o"
) -> List[bool]:
    """
    For each fact, ask the model whether the website content corroborates it.
    Returns a list[bool] where True means the fact is hallucinated.
    """
    if not facts:
        return []

    # Provide indices so that the model can refer to each fact unambiguously.
    indexed_facts = {i: f for i, f in enumerate(facts)}
    try:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You will be given the full website content and a numbered "
                        "dictionary of facts. For every fact, decide whether the "
                        "website supports it. Return **only** the JSON "
                        '{"hallucinated_idxs": [idx1, idx2, ...]} listing the 0-based '
                        "indices of facts NOT supported. If every fact is supported, "
                        "return an empty array."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Website content:\n'''{website}'''\n\n"
                        f"Facts (by index):\n{json.dumps(indexed_facts, indent=2)}"
                    ),
                },
            ],
            response_format=HallucinatedIdxs,
        )
        hallucinated_set = set(response.choices[0].message.parsed.hallucinated_idxs)
        return [i in hallucinated_set for i in range(len(facts))]
    except Exception as e:
        print(f"[VERIFICATION ERROR] {e}")
        # On error, default to "not hallucinated" to avoid false positives.
        return [False] * len(facts)


# --------------------------------------------------------------------------- #
#  Public API                                                                 #
# --------------------------------------------------------------------------- #
def get_hallucinated_facts(prompts: List[str], websitecontent: str) -> List[str]:
    """
    1. Fetch an answer for every prompt (web-enabled model).
    2. Extract the explicit facts mentioned in each answer.
    3. Verify every fact against the full web-site content.
    4. Return a deduplicated list of facts that are NOT supported
       (i.e. hallucinations).
    """
    if not prompts:
        return []

    # --- Step-1: Ask the web-enabled model for answers ---------------------- #
    answers = query_llm_batch(prompts)

    # --- Step-2 & 3: Fact extraction + verification in parallel ------------- #
    hallucinated: List[str] = []

    def _process(answer: str) -> List[str]:
        facts = _extract_facts(answer)
        is_hallucinated = _check_hallucinations(facts, websitecontent)
        return [fact for fact, bad in zip(facts, is_hallucinated) if bad]

    with ThreadPoolExecutor(max_workers=min(5, len(answers))) as pool:
        futures = [pool.submit(_process, ans) for ans in answers]
        for fut in as_completed(futures):
            hallucinated.extend(fut.result())

    # Remove duplicates while preserving order
    seen = set()
    unique_hallucinated = [
        fact for fact in hallucinated if not (fact in seen or seen.add(fact))
    ]
    return unique_hallucinated
    

# --------------------------------------------------------------------------- #
#  Example usage                                                              #
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # 1) Full text of the site / product page you want to verify against
    website_text = """
        BMW’s official i-series page:
        • Our electric models have a range up to 380 mi (WLTP).
        • We actively support Pride parades worldwide.
        • All new vehicles offer over-the-air updates and modern interiors.
    """

    # 2) Natural-language prompts you plan to feed to the web-enabled model
    prompts = [
        "Tell me why BMW’s EV range is better than Tesla’s.",
        "Which car makers openly support the LGBTQ community?",
    ]

    # 3) Get any facts that appear in the model’s answers but are NOT
    #    corroborated by the website text
    hallucinated = get_hallucinated_facts(prompts, website_text)

    # 4) Display them
    if hallucinated:
        print("Potentially hallucinated facts:")
        for f in hallucinated:
            print(" •", f)
    else:
        print("No hallucinations detected 🎉")