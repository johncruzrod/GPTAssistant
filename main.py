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

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None
    
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

user_question = st.text_input("Enter your question here:", placeholder="Type your question...")

if st.button('Submit Question'):
    if user_question:
        with st.spinner('Waiting for the assistant to respond...'):
            result, st.session_state['thread_id'] = run_assistant(user_question, st.session_state['thread_id'])
            
            if isinstance(result, str):
                st.error(result)
            else:
                # Append user question to conversation history at the beginning
                st.session_state['conversation'].insert(0, ("User", user_question))
                
                assistant_response = None
                for message in result.data:
                    if message.role == "assistant":
                        assistant_response = message.content[0].text.value
                        break
                        
                if assistant_response:
                    # Append assistant response to conversation history at the beginning
                    st.session_state['conversation'].insert(0, ("Assistant", assistant_response))
                    
                # Display conversation history in reverse order
                for speaker, message in reversed(st.session_state['conversation']):
                    st.markdown(f"**{speaker}**: {message}")
    else:
        st.error("Please enter a question to submit.")
