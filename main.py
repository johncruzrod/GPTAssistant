import openai
import streamlit as st

# Initialize OpenAI client with API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to run assistant within an existing thread or create a new one
def run_assistant(question, thread_id=None):
    if thread_id is None:
        # Create a new thread if one does not exist
        thread = openai.beta.threads.create()
        thread_id = thread.id
    
    # Add user's question to the thread
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )

    # Create and poll a run
    run = openai.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_UEVqifz1E5lF4nddLXVbpbza"
    )

    # Retrieve messages only if the run is completed
    if run.status == 'completed':
        messages = openai.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages, thread_id
    else:
        return f"Run status: {run.status}", thread_id

# Streamlit UI setup
st.title('Chat with GPT-4')

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.text_input("Hello! How can I assist you today?")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message
