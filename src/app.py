import streamlit as st

# --- Initialize session state for paired fact/prompt entries ---
if 'fact_prompt_pairs' not in st.session_state:
    st.session_state.fact_prompt_pairs = [{'fact': '', 'prompt': ''}]

st.title('LLM Factual Consistency Evaluation')
st.subheader("🔎 Fact-Prompt Evaluation Pairs")

# --- Fact + Prompt Input Pair Section ---
pairs_to_remove = []
for i, pair in enumerate(st.session_state.fact_prompt_pairs):
    st.markdown(f"#### Pair {i+1}")
    col1, col2 = st.columns([1, 2])
    with col1:
        fact_val = st.text_input(f"Fact {i+1}", value=pair['fact'], key=f'fact_{i}')
        st.session_state.fact_prompt_pairs[i]['fact'] = fact_val
    with col2:
        prompt_val = st.text_input(f"Prompt {i+1}", value=pair['prompt'], key=f'prompt_{i}')
        st.session_state.fact_prompt_pairs[i]['prompt'] = prompt_val
    if len(st.session_state.fact_prompt_pairs) > 1:
        if st.button(f"➖ Remove Pair {i+1}", key=f'remove_{i}'):
            pairs_to_remove.append(i)

for idx in sorted(pairs_to_remove, reverse=True):
    st.session_state.fact_prompt_pairs.pop(idx)

if st.button("➕ Add Another Fact-Prompt Pair"):
    st.session_state.fact_prompt_pairs.append({'fact': '', 'prompt': ''})

# --- Mentioned Rate & Chat Links Section ---
st.markdown("---")
st.header("Mentioned Rate & Chats")

# Make sure rates list matches the number of pairs, cycling if needed
def get_rates(n):
    base_rates = [80, 60, 40, 50, 30, 90]
    if n <= len(base_rates):
        return base_rates[:n]
    else:
        # Repeat/cycle rates if more pairs than base rates
        return [base_rates[i % len(base_rates)] for i in range(n)]

placeholder_mentioned_rates = get_rates(len(st.session_state.fact_prompt_pairs))
placeholder_chats = [
    [f'Chat {i+1}-1', f'Chat {i+1}-2', f'Chat {i+1}-3'] for i in range(len(st.session_state.fact_prompt_pairs))
]

for i, pair in enumerate(st.session_state.fact_prompt_pairs):
    st.subheader(f'Fact {i+1}: {pair["fact"]}')
    st.write(f'Mentioned Rate: {placeholder_mentioned_rates[i]}%')
    st.write('Chats:')
    for chat in placeholder_chats[i]:
        st.markdown(f'- [View {chat}](#)', unsafe_allow_html=True)
