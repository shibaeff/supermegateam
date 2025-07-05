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
        st.text_input(f"Prompt {i+1}", value=prompt['text'], key=f'prompt_text_{prompt["id"]}')
    # Remove buttons outside the form
    for i, prompt in enumerate(st.session_state.prompts):
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
        st.text_input(f"Fact {i+1}", value=fact['text'], key=f'fact_text_{fact["id"]}')
    # Remove buttons outside the form
    for i, fact in enumerate(st.session_state.facts):
        if len(st.session_state.facts) > 1:
            if st.button("❌", key=f'remove_fact_{fact["id"]}'):
                fact_to_remove = fact['id']
    if fact_to_remove:
        st.session_state.facts = [f for f in st.session_state.facts if f['id'] != fact_to_remove]
    if st.button("➕", key="add_fact"):
        st.session_state.facts.append({'id': str(uuid.uuid4()), 'text': ''})

# --- Single Submit All button for both prompts and facts ---
with st.form(key='submit_all_form', clear_on_submit=False):
    submitted = st.form_submit_button("Submit All")
    if submitted:
        for idx, prompt in enumerate(st.session_state.prompts):
            st.session_state.prompts[idx]['text'] = st.session_state[f'prompt_text_{prompt["id"]}']
        for idx, fact in enumerate(st.session_state.facts):
            st.session_state.facts[idx]['text'] = st.session_state[f'fact_text_{fact["id"]}']
        # Add chat run placeholders for each prompt/fact combination
        st.markdown("---")
        st.header("Chat Runs (Placeholders)")
        for i, prompt in enumerate(st.session_state.prompts):
            for j, fact in enumerate(st.session_state.facts):
                st.info(f"Chat Run Placeholder: Prompt {i+1} & Fact {j+1}")

st.markdown("---")

# --- Placeholder for Mentioned Rate & Chats Section ---
st.header("Mentioned Rate & Chats")
st.info("This section can be updated to show fact/prompt combinations or evaluation results.")
