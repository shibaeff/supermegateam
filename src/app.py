import streamlit as st

# --- Initialize session state for separate facts and prompts lists ---
if 'facts' not in st.session_state:
    st.session_state.facts = ['']
if 'prompts' not in st.session_state:
    st.session_state.prompts = ['']

st.title('LLM Factual Consistency Evaluation')

# --- Two-column layout: Prompts (left), Facts (right) ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("💬 Prompts")
    prompts_to_remove = []
    for i, prompt in enumerate(st.session_state.prompts):
        col1, col2 = st.columns([4, 1])
        with col1:
            prompt_val = st.text_input(f"Prompt {i+1}", value=prompt, key=f'prompt_{i}')
            st.session_state.prompts[i] = prompt_val
        with col2:
            if len(st.session_state.prompts) > 1:
                if st.button(f"Remove Prompt {i+1}", key=f'remove_prompt_{i}'):
                    prompts_to_remove.append(i)
    for idx in sorted(prompts_to_remove, reverse=True):
        st.session_state.prompts.pop(idx)
    if st.button("Add Another Prompt"):
        st.session_state.prompts.append('')

with col_right:
    st.subheader("📝 Facts")
    facts_to_remove = []
    for i, fact in enumerate(st.session_state.facts):
        col1, col2 = st.columns([4, 1])
        with col1:
            fact_val = st.text_input(f"Fact {i+1}", value=fact, key=f'fact_{i}')
            st.session_state.facts[i] = fact_val
        with col2:
            if len(st.session_state.facts) > 1:
                if st.button(f"Remove Fact {i+1}", key=f'remove_fact_{i}'):
                    facts_to_remove.append(i)
    for idx in sorted(facts_to_remove, reverse=True):
        st.session_state.facts.pop(idx)
    if st.button("Add Another Fact"):
        st.session_state.facts.append('')

st.markdown("---")

# --- Placeholder for Mentioned Rate & Chats Section ---
st.header("Mentioned Rate & Chats")
st.info("This section can be updated to show fact/prompt combinations or evaluation results.")
