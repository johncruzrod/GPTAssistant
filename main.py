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

# Streamlit UI setup
st.title('OpenAI Assistant Interaction')

# Initialize chat history if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in reversed(st.session_state.messages):
    if message["role"] == "user":
        st.chat_message(message["content"], avatar_style="big-smile", key=f"user_{message['content']}")
    else:
        st.chat_message(message["content"], avatar_style="bottts", key=f"assistant_{message['content']}")

# Accept user input
user_question = st.chat_input("Enter your question:")

if user_question:
    # Append user question to conversation history
    st.session_state.messages.append({"role": "user", "content": user_question})
    
    # Display user message in chat
    st.chat_message(user_question, avatar_style="big-smile", key=f"user_{user_question}")
    
    # Clear the input field
    st.session_state.user_question = ""
    
    # Run the assistant and get the response
    with st.spinner('Waiting for the assistant to respond...'):
        result, st.session_state['thread_id'] = run_assistant(user_question, st.session_state.get('thread_id'))
        
        if isinstance(result, str):
            st.error(result)
        else:
            assistant_response = None
            for message in result.data:
                if message.role == "assistant":
                    assistant_response = message.content[0].text.value
                    break
            
            if assistant_response:
                # Append assistant response to conversation history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
                # Display assistant response in chat
                st.chat_message(assistant_response, avatar_style="bottts", key=f"assistant_{assistant_response}")
