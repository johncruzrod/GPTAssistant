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
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(message["content"])
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(message["content"])

user_question = st.chat_input("What is up?")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})

    with st.spinner('Waiting for the assistant to respond...'):
        result, st.session_state['thread_id'] = run_assistant(user_question, st.session_state['thread_id'])
        if isinstance(result, str):
            st.error(result)
        else:
            for message in result:
                if message.role == "assistant":
                    response = message.content
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    break

    # Display the messages after the response is received
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])
