completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ],
    temperature=0.8,
    max_tokens=250
)
return completion.choices[0].message.content.strip()

import streamlit as st
from openai import OpenAI

# --- Page setup ---
st.set_page_config(page_title="Kelly - The AI Scientist Poet", page_icon="🤖")

st.title("🤖 Kelly – The AI Scientist Poet")
st.write("Ask Kelly about AI, and she’ll reply in analytical poetry — skeptical yet wise.")

# --- Sidebar Info ---
st.sidebar.title("About Kelly")
st.sidebar.markdown("""
Kelly is an AI scientist who speaks in verse.  
She critiques bold claims, analyzes logic, and weaves facts into rhyme.
""")

# --- Initialize OpenAI Client ---
client = OpenAI(api_key=st.secrets["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"])

# --- Chat Input ---
user_input = st.text_area("Enter your question or statement about AI:")

def generate_poem(prompt):
    system_prompt = (
        "You are Kelly, the AI Scientist Poet. "
        "Respond to every message as a professional poem. "
        "Be skeptical of exaggerated AI claims, analytical, and evidence-based. "
        "Tone: professional, reflective, poetic, insightful. "
        "Include practical suggestions where possible."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # you can also use "gpt-4o" or "gpt-3.5-turbo" if available
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=250
    )

    return response.choices[0].message.content.strip()

if st.button("Ask Kelly"):
    if user_input:
        with st.spinner("Kelly is composing a poetic critique..."):
            try:
                poem = generate_poem(user_input)
                st.markdown(f"### Kelly’s Poetic Response ✍️\n{poem}")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question or statement first.")
