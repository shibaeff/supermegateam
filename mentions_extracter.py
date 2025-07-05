import json,os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def eval_facts(facts:dict,prs:list,model="gpt-4o-mini"):
    ids=list(facts)
    facts_json=json.dumps([{"id":k,"fact":facts[k]}for k in ids])
    sys=f'Given a dialog and facts {facts_json}, return a JSON array of ids of facts explicitly mentioned and justified.'
    hit=[0]*len(ids)
    for ctx in prs:
        out=client.chat.completions.create(model=model,messages=[{"role":"system","content":sys},{"role":"user","content":ctx}],temperature=0).choices[0].message.content
        try: lst=json.loads(out)
        except: lst=[s.strip().strip('"') for s in out.strip("[]").split(",")]
        for i in lst:
            if i in facts: hit[ids.index(i)]+=1
    n=len(prs)
    return [h/n for h in hit]

# Example test data
facts = {
    "F1": "The capital of France is Paris",
    "F2": "Water boils at 100°C at sea level",
    "F3": "Python is a programming language",
    "F4": "The Earth orbits the Sun",
    "F5": "Shakespeare wrote Romeo and Juliet"
}

promptresponses = [
    "Q: What's the capital of France? A: Paris is the capital of France, a beautiful city known for its culture.",
    "Q: At what temperature does water boil? A: Water boils at 100 degrees Celsius under standard atmospheric pressure.",
    "Q: Tell me about programming languages? A: Python is a popular programming language used for data science and web development.",
    "Q: Describe our solar system. A: The Earth revolves around the Sun along with other planets in our solar system.",
    "Q: Who wrote famous plays? A: William Shakespeare authored many classics including Romeo and Juliet.",
    "Q: What's 2+2? A: The answer is 4, which is basic arithmetic."
]

# Test the function
result = eval_facts(facts, promptresponses)
print(result)  # Should show [1.0, 1.0, 1.0, 1.0, 1.0] since each fact appears once in 5 relevant responses

