import streamlit as st
import uuid

# --- Initialize session state for separate facts and prompts lists with unique IDs ---
def init_list(key):
    if key not in st.session_state:
        st.session_state[key] = [{'id': str(uuid.uuid4()), 'text': ''}]

init_list('facts')
init_list('prompts')

st.title('LLM Factual Consistency Evaluation')

# --- Two-column layout: Prompts (left), Facts (right) ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💬 Prompts")
    prompt_to_remove = None
    for i, prompt in enumerate(st.session_state.prompts):
        with st.form(key=f'prompt_form_{prompt["id"]}', clear_on_submit=False):
            col1, col2 = st.columns([4, 1])
            with col1:
                prompt_val = st.text_input(f"Prompt {i+1}", value=prompt['text'], key=f'prompt_text_{prompt["id"]}')
            with col2:
                remove = st.form_submit_button("❌") if len(st.session_state.prompts) > 1 else False
            if remove or st.session_state.prompts[i]['text'] != prompt_val:
                st.session_state.prompts[i]['text'] = prompt_val
            if remove:
                prompt_to_remove = prompt['id']
    if prompt_to_remove:
        st.session_state.prompts = [p for p in st.session_state.prompts if p['id'] != prompt_to_remove]
    if st.button("➕", key="add_prompt"):
        st.session_state.prompts.append({'id': str(uuid.uuid4()), 'text': ''})

with col_right:
    st.subheader("📝 Facts")
    fact_to_remove = None
    for i, fact in enumerate(st.session_state.facts):
        with st.form(key=f'fact_form_{fact["id"]}', clear_on_submit=False):
            col1, col2 = st.columns([4, 1])
            with col1:
                fact_val = st.text_input(f"Fact {i+1}", value=fact['text'], key=f'fact_text_{fact["id"]}')
            with col2:
                remove = st.form_submit_button("❌") if len(st.session_state.facts) > 1 else False
            if remove or st.session_state.facts[i]['text'] != fact_val:
                st.session_state.facts[i]['text'] = fact_val
            if remove:
                fact_to_remove = fact['id']
    if fact_to_remove:
        st.session_state.facts = [f for f in st.session_state.facts if f['id'] != fact_to_remove]
    if st.button("➕", key="add_fact"):
        st.session_state.facts.append({'id': str(uuid.uuid4()), 'text': ''})

st.markdown("---")

# --- Placeholder for Mentioned Rate & Chats Section ---
st.header("Mentioned Rate & Chats")
st.info("This section can be updated to show fact/prompt combinations or evaluation results.")
