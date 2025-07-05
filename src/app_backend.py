from flask import Flask, request, jsonify
from mentions_extracter import get_perc_for_prompts_and_facts, get_all_for_prompts_and_facts

app = Flask(__name__)

@app.route('/api/eval-facts', methods=['POST'])
def eval_facts_endpoint():
    data = request.get_json()
    prompts = data.get('prompts', [])
    facts = data.get('facts', [])
    if not isinstance(prompts, list) or not isinstance(facts, list):
        return jsonify({'error': 'prompts and facts must be lists'}), 400
    try:
        percentages = get_perc_for_prompts_and_facts(prompts, facts)
        return jsonify({'percentages': percentages[0], 'prompts_to_facts': percentages[1]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/eval-all', methods=['POST'])
def eval_all_endpoint():
    data = request.get_json()
    prompts = data.get('prompts', [])
    facts = data.get('facts', [])
    if not isinstance(prompts, list) or not isinstance(facts, list):
        return jsonify({'error': 'prompts and facts must be lists'}), 400
    try:
        result = get_all_for_prompts_and_facts(prompts, facts)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000)
