import os
import openai
import streamlit as st

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

# Function to run assistant within an existing thread or create a new one
def run_assistant(question, thread_id=None):
    if thread_id is None:
        # Create a new thread if one does not exist
        thread = client.beta.threads.create()
        thread_id = thread.id
    else:
        # Use the existing thread to maintain conversation context
        thread_id = thread_id
    # Add user's question to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )
    # Create and poll a run
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in"
    )
    # Retrieve messages only if the run is completed
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages, thread_id
    else:
        return f"Run status: {run.status}", thread_id

# Streamlit UI setup
st.title('OpenAI Assistant Interaction')

with st.expander("ℹ️ Disclaimer"):
    st.caption(
        """We appreciate your engagement! Please note, this demo is designed to
        process a maximum of 10 interactions and may be unavailable if too many
        people use the service concurrently. Thank you for your understanding.
        """
    )

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "max_messages" not in st.session_state:
    # Counting both user and assistant messages, so 10 rounds of conversation
    st.session_state.max_messages = 20

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if len(st.session_state.messages) >= st.session_state.max_messages:
    st.info(
        """Notice: The maximum message limit for this demo version has been reached. We value your interest!
        We encourage you to experience further interactions by building your own application with instructions
        from Streamlit's [Build a basic LLM chat app](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)
        tutorial. Thank you for your understanding."""
    )
else:
    user_question = st.chat_input("What is up?")
    if user_question:
        # Append user's query to session messages
        st.session_state.messages.append({"role": "user", "content": user_question})
    
        with st.chat_message("user"):
            st.markdown(user_question)
    
        with st.chat_message("assistant"):
            with st.spinner('Waiting for the assistant to respond...'):
                # Obtain the response and thread id from the assistant
                result, st.session_state['thread_id'] = run_assistant(user_question, st.session_state['thread_id'])
    
                if isinstance(result, str):
                    st.error(result)
                else:
                    for message in result[0].data:  # Assuming result returns messages and thread_id in a tuple
                        if message['role'] == "assistant":
                            response = message["content"]
                            st.markdown(response)
    
                            # Append only the assistant's response to the messages list
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            break

# Force a state refresh after updating messages
st.experimental_rerun()
