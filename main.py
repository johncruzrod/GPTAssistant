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

# Function to display conversation history
def display_conversation_history():
    # Use reversed order to show the most recent messages at the top
    for i in reversed(range(len(st.session_state['conversation']))):
        speaker, message = st.session_state['conversation'][i]
        st.markdown(f"**{speaker}**: {message}")

# Streamlit UI setup
st.title('OpenAI Assistant Interaction')

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

user_question = st.text_input("Enter your question here:", key="user_question", placeholder="Type your question...")

if st.button('Submit Question'):
    if user_question:
        # Append user question to conversation history
        st.session_state['conversation'].append(("User", user_question))
        
        # No need to call display_conversation_history here
        
        with st.spinner('Waiting for the assistant to respond...'):
            result, st.session_state['thread_id'] = run_assistant(user_question, st.session_state['thread_id'])
            
            if isinstance(result, str):
                st.error(result)
            else:
                assistant_response = None
                for message in result.data:
                    if message.role == "assistant":
                        assistant_response = message.content
                        break
                        
                if assistant_response:
                    # Append assistant response to conversation history
                    st.session_state['conversation'].append(("Assistant", assistant_response))

        # Display updated conversation history
        display_conversation_history()
    else:
        st.error("Please enter a question to submit.")

# Always display conversation history, even if no question has been asked yet
if st.session_state['conversation']:
    display_conversation_history()
