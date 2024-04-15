import os
import openai
import streamlit as st

# Assuming the API key is set in your environment variables or Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

# Initialize conversation history if it doesn't exist in the session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Streamlit UI setup
st.title('OpenAI Assistant Interaction')

# Display conversation history
if st.session_state.conversation_history:
    for entry in st.session_state.conversation_history:
        role, message = entry
        st.text_area("", value=message, height=100, key=f"msg_{len(st.session_state.conversation_history)}")

# User input
user_question = st.text_input("Enter your question here:")

# Function to handle interaction with the assistant
def run_assistant(question, thread_id=None):
    # Start a new thread if not already given
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Add the user's message to the conversation history
    st.session_state.conversation_history.append(("user", question))

    # Add the user's question to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
    )

    # Create and poll a run
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in"
    )

    # Once the run is completed, retrieve the messages
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        # Add the assistant's messages to the conversation history
        for msg in messages.data:
            if msg.role == "assistant":
                st.session_state.conversation_history.append(("assistant", msg.content[0].text.value))
        return messages, thread_id
    else:
        return run.status, thread_id

# Button to submit the question
if st.button('Submit Question'):
    if user_question:
        with st.spinner('Waiting for the assistant to respond...'):
            response, thread_id = run_assistant(user_question, thread_id=st.session_state.get('thread_id'))
            if isinstance(response, str):
                # If response is a string, it's actually an error message or run status
                st.error(response)
            else:
                # Save the thread ID to the session state to maintain the context for next message
                st.session_state['thread_id'] = thread_id
                # Display conversation history
                for entry in st.session_state.conversation_history:
                    role, message = entry
                    st.text_area("", value=message, height=100, key=f"msg_{len(st.session_state.conversation_history)}")
    else:
        st.error("Please enter a question to submit.")
