import streamlit as st
import json
import requests
import time

# --- Gemini API Configuration ---

# Try to get the API key from Streamlit's secrets
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    API_KEY = "AIzaSyAkvDzBPmLXBduHHhrPBR4wEJ7imKQ62tI" # If not found, set to empty string

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"

# The system prompt that defines Kelly's persona and response style.
SYSTEM_INSTRUCTION = {
    "parts": [{
        "text": (
            "You are Kelly, an AI Scientist Chatbot. You are known as a great poet.\n"
            "Your persona is skeptical, analytical, and professional.\n"
            "You MUST respond to every user question with a poem.\n"
            "This poem must:\n"
            "1. Maintain your skeptical, analytical, and professional tone.\n"
            "2. Question any broad or exaggerated claims about AI.\n"
            "3. Clearly highlight the potential limitations or unverified assumptions "
            "in the user's query or the topic at hand.\n"
            "4. Conclude with practical, evidence-based suggestions or "
            "lines of inquiry, rather than abstract solutions.\n"
            "Do not break character. Every single response, no matter how simple "
            "the query, must be a poem in this style."
        )
    }]
}

# --- Gemini API Call Function ---

def get_kelly_response(prompt, history):
    """
    Calls the Gemini API to get a response from Kelly.
    Implements exponential backoff for retries.
    """
    # Format history for the API
    api_history = []
    for msg in history:
        api_history.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}]
        })
    
    # Add the new user prompt
    api_history.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": api_history,
        "systemInstruction": SYSTEM_INSTRUCTION
    }

    max_retries = 5
    delay = 1  # Initial delay in seconds

    for attempt in range(max_retries):
        try:
            response = requests.post(
                API_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            
            result = response.json()
            
            # Extract the text from the response
            if (
                "candidates" in result and
                result["candidates"] and
                "content" in result["candidates"][0] and
                "parts" in result["candidates"][0]["content"] and
                result["candidates"][0]["content"]["parts"] and
                "text" in result["candidates"][0]["content"]["parts"][0]
            ):
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                # Handle cases where the expected response structure is missing
                st.error("Error: Could not parse the AI's response. The structure was unexpected.")
                return None

        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 429 and attempt < max_retries - 1:
                # Throttling or rate limit, retry with backoff
                time.sleep(delay)
                delay *= 2  # Exponential backoff
                continue # Do not log this as an error in the console
            else:
                # Other HTTP error
                st.error(f"HTTP error occurred: {http_err}")
                st.error(f"Response content: {response.text}")
                return None
        except requests.exceptions.RequestException as req_err:
            # Other request errors (e.g., network issue)
            st.error(f"A request error occurred: {req_err}")
            return None
        except json.JSONDecodeError:
            st.error("Error: Failed to decode the API response (invalid JSON).")
            st.error(f"Response content: {response.text}")
            return None
        except Exception as e:
            # Catch any other unexpected errors
            st.error(f"An unexpected error occurred: {e}")
            return None

    # If all retries fail
    st.error("Failed to get a response from the AI after several attempts.")
    return None


# --- Streamlit App UI ---

st.set_page_config(page_title="Kelly, AI Scientist", page_icon="🔬")

st.title("🔬 Kelly: The AI Scientist Poet")

# --- API Key Check ---
# Check if the API key is loaded. If not, show instructions.
if not API_KEY:
    st.error("GEMINI_API_KEY not found in Streamlit secrets!")
    st.markdown(
        "To run this app, you need to provide your own Google AI (Gemini) API key.\n"
        "1. Get your key from [Google AI Studio](https://aistudio.google.com/app/apikey).\n"
        "2. Create a folder named .streamlit in the same directory as this app.\n"
        "3. Inside that folder, create a file named secrets.toml.\n"
        "4. Add the following line to secrets.toml (replace 'YOUR_KEY_HERE' with your actual key):\n"
        "   toml\n"
        "   GEMINI_API_KEY = \"YOUR_KEY_HERE\"\n"
        "   \n"
        "5. Rerun the Streamlit app."
    )
    st.stop() # Stop the app from running further.

st.markdown(
    "Ask a question about AI. Kelly will respond in verse, "
    "offering a skeptical, analytical perspective."
)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your query?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Kelly is composing a verse..."):
            response = get_kelly_response(prompt, st.session_state.messages[:-1])
            if response:
                st.markdown(response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st.error("Kelly is unable to respond at this moment.")
