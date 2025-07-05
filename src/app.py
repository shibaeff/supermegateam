import streamlit as st
import uuid
from typing import List
import random

# --- Initialize session state for separate facts and prompts lists with unique IDs ---
def init_list(key):
    if key not in st.session_state:
        st.session_state[key] = [{'id': str(uuid.uuid4()), 'text': ''}]

init_list('facts')
init_list('prompts')

st.title('LLM Factual Consistency Evaluation')

# --- Two-column layout: Facts (far left), Prompts (far right) ---
layout_cols = st.columns([0.1, 6, 0.1, 6, 0.1])
col_facts = layout_cols[1]
col_prompts = layout_cols[3]

# Custom CSS for card-like row grouping
st.markdown('''
<style>
.card-row {
    border: 1px solid #eee;
    border-radius: 6px;
    background: #fafbfc;
    margin-bottom: 0.5rem;
    padding: 0.3rem 0.5rem;
    display: flex;
    align-items: center;
}
.card-row .stTextInput, .card-row .stButton {margin-bottom: 0 !important;}
.card-row .stButton button {padding: 0.05rem 0.2rem; font-size: 0.7rem; color: #d00;}
</style>
''', unsafe_allow_html=True)

with col_facts:
    st.subheader("📝 Facts")
    fact_to_remove = None
    for i, fact in enumerate(st.session_state.facts):
        with st.container():
            row = st.columns([8, 1])
            with row[0]:
                st.markdown('<div class="card-row">', unsafe_allow_html=True)
                st.text_input(f"Fact {i+1}", value=fact['text'], key=f'fact_text_{fact["id"]}')
            with row[1]:
                if len(st.session_state.facts) > 1:
                    if st.button("❌", key=f'remove_fact_{fact["id"]}', help="Remove this fact"):
                        fact_to_remove = fact['id']
            st.markdown('</div>', unsafe_allow_html=True)
    if fact_to_remove:
        st.session_state.facts = [f for f in st.session_state.facts if f['id'] != fact_to_remove]
    if st.button("➕", key="add_fact"):
        st.session_state.facts.append({'id': str(uuid.uuid4()), 'text': ''})

with col_prompts:
    st.subheader("💬 Prompts")
    prompt_to_remove = None
    for i, prompt in enumerate(st.session_state.prompts):
        with st.container():
            row = st.columns([8, 1])
            with row[0]:
                st.markdown('<div class="card-row">', unsafe_allow_html=True)
                st.text_input(f"Prompt {i+1}", value=prompt['text'], key=f'prompt_text_{prompt["id"]}')
            with row[1]:
                if len(st.session_state.prompts) > 1:
                    if st.button("❌", key=f'remove_prompt_{prompt["id"]}', help="Remove this prompt"):
                        prompt_to_remove = prompt['id']
            st.markdown('</div>', unsafe_allow_html=True)
    if prompt_to_remove:
        st.session_state.prompts = [p for p in st.session_state.prompts if p['id'] != prompt_to_remove]
    if st.button("➕", key="add_prompt"):
        st.session_state.prompts.append({'id': str(uuid.uuid4()), 'text': ''})

def gen_perc_for_facts_and_prompts(facts: List[str], prompts: List[str]) -> List[float]:
    # Mock: return a random percentage for each fact
    return [round(random.uniform(0, 1), 2) for _ in facts]

# --- Single Submit All button for both prompts and facts ---
with st.form(key='submit_all_form', clear_on_submit=False):
    submitted = st.form_submit_button("Submit All")
    mentioned_rates = None
    if submitted:
        for idx, prompt in enumerate(st.session_state.prompts):
            st.session_state.prompts[idx]['text'] = st.session_state[f'prompt_text_{prompt["id"]}']
        for idx, fact in enumerate(st.session_state.facts):
            st.session_state.facts[idx]['text'] = st.session_state[f'fact_text_{fact["id"]}']
        # Call the mock function
        facts_list = [f['text'] for f in st.session_state.facts]
        prompts_list = [p['text'] for p in st.session_state.prompts]
        mentioned_rates = gen_perc_for_facts_and_prompts(facts_list, prompts_list)
        # Mentioned Rate section above chat runs
        st.markdown("---")
        st.header("Mentioned Rate & Chats")
        if mentioned_rates:
            for i, rate in enumerate(mentioned_rates):
                st.write(f"Fact {i+1}: {int(rate*100)}% mentioned")
        else:
            st.info("This section can be updated to show fact/prompt combinations or evaluation results.")
        # Chat run placeholders
        st.markdown("---")
        st.header("Chat Runs (Placeholders)")
        for run_num in range(1, 4):
            with st.expander(f"Chat Run {run_num}"):
                st.markdown("**Prompts:**")
                for i, prompt in enumerate(st.session_state.prompts):
                    st.markdown(f"- {prompt['text']}")
                st.markdown("**Facts:**")
                for j, fact in enumerate(st.session_state.facts):
                    st.markdown(f"- {fact['text']}")
                st.markdown(f"**Simulated Chat Output {run_num}:**\n> This is a placeholder for the chat result using all prompts and facts.")
