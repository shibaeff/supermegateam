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
        col1, col2 = st.columns([4, 1])
        with col1:
            prompt_val = st.text_input(f"Prompt {i+1}", value=prompt['text'], key=f'prompt_text_{prompt["id"]}')
            st.session_state.prompts[i]['text'] = prompt_val
        with col2:
            if len(st.session_state.prompts) > 1:
                if st.button("❌", key=f'remove_prompt_{prompt["id"]}'):
                    prompt_to_remove = prompt['id']
    if prompt_to_remove:
        st.session_state.prompts = [p for p in st.session_state.prompts if p['id'] != prompt_to_remove]
    if st.button("➕", key="add_prompt"):
        st.session_state.prompts.append({'id': str(uuid.uuid4()), 'text': ''})

with col_right:
    st.subheader("📝 Facts")
    fact_to_remove = None
    for i, fact in enumerate(st.session_state.facts):
        col1, col2 = st.columns([4, 1])
        with col1:
            fact_val = st.text_input(f"Fact {i+1}", value=fact['text'], key=f'fact_text_{fact["id"]}')
            st.session_state.facts[i]['text'] = fact_val
        with col2:
            if len(st.session_state.facts) > 1:
                if st.button("❌", key=f'remove_fact_{fact["id"]}'):
                    fact_to_remove = fact['id']
    if fact_to_remove:
        st.session_state.facts = [f for f in st.session_state.facts if f['id'] != fact_to_remove]
    if st.button("➕", key="add_fact"):
        st.session_state.facts.append({'id': str(uuid.uuid4()), 'text': ''})

st.markdown("---")

# --- Placeholder for Mentioned Rate & Chats Section ---
st.header("Mentioned Rate & Chats")
st.info("This section can be updated to show fact/prompt combinations or evaluation results.")
