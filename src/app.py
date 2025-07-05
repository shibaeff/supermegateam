import streamlit as st
import uuid

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

with col_facts:
    st.subheader("📝 Facts")
    fact_to_remove = None
    for i, fact in enumerate(st.session_state.facts):
        cols = st.columns([8, 1])
        with cols[0]:
            st.text_input(f"Fact {i+1}", value=fact['text'], key=f'fact_text_{fact["id"]}')
        with cols[1]:
            if len(st.session_state.facts) > 1:
                if st.button("", key=f'remove_fact_{fact["id"]}'):
                    fact_to_remove = fact['id']
                st.markdown("""
                <style>
                div[data-testid=\"stButton\"] button {padding: 0.1rem 0.4rem; font-size: 1.1rem; color: #d00;}
                </style>
                <span style='color:#d00;font-size:1.3rem;'>❌</span>
                """, unsafe_allow_html=True)
    if fact_to_remove:
        st.session_state.facts = [f for f in st.session_state.facts if f['id'] != fact_to_remove]
    if st.button("➕", key="add_fact"):
        st.session_state.facts.append({'id': str(uuid.uuid4()), 'text': ''})
    st.markdown("""
    <style>
    div[data-testid=\"stButton\"] button {padding: 0.1rem 0.4rem; font-size: 1.1rem;}
    </style>
    """, unsafe_allow_html=True)

with col_prompts:
    st.subheader("💬 Prompts")
    prompt_to_remove = None
    for i, prompt in enumerate(st.session_state.prompts):
        cols = st.columns([8, 1])
        with cols[0]:
            st.text_input(f"Prompt {i+1}", value=prompt['text'], key=f'prompt_text_{prompt["id"]}')
        with cols[1]:
            if len(st.session_state.prompts) > 1:
                if st.button("", key=f'remove_prompt_{prompt["id"]}'):
                    prompt_to_remove = prompt['id']
                st.markdown("""
                <style>
                div[data-testid=\"stButton\"] button {padding: 0.1rem 0.4rem; font-size: 1.1rem; color: #d00;}
                </style>
                <span style='color:#d00;font-size:1.3rem;'>❌</span>
                """, unsafe_allow_html=True)
    if prompt_to_remove:
        st.session_state.prompts = [p for p in st.session_state.prompts if p['id'] != prompt_to_remove]
    if st.button("➕", key="add_prompt"):
        st.session_state.prompts.append({'id': str(uuid.uuid4()), 'text': ''})
    st.markdown("""
    <style>
    div[data-testid=\"stButton\"] button {padding: 0.1rem 0.4rem; font-size: 1.1rem;}
    </style>
    """, unsafe_allow_html=True)

# --- Single Submit All button for both prompts and facts ---
with st.form(key='submit_all_form', clear_on_submit=False):
    submitted = st.form_submit_button("Submit All")
    if submitted:
        for idx, prompt in enumerate(st.session_state.prompts):
            st.session_state.prompts[idx]['text'] = st.session_state[f'prompt_text_{prompt["id"]}']
        for idx, fact in enumerate(st.session_state.facts):
            st.session_state.facts[idx]['text'] = st.session_state[f'fact_text_{fact["id"]}']
        # Add several chat run placeholders, each considering all prompts and all facts
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

st.markdown("---")

# --- Placeholder for Mentioned Rate & Chats Section ---
st.header("Mentioned Rate & Chats")
st.info("This section can be updated to show fact/prompt combinations or evaluation results.")
