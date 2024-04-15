import openai
import streamlit as st
from openai import OpenAI
from openai.types.beta.threads import Text, TextDelta

# Initialize the OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI()

# Set up the Streamlit UI
st.title('Chat with OpenAI Assistant')

# Placeholder for the assistant's responses
response_placeholder = st.empty()

# Function to handle the conversation
def talk_to_assistant(question, event_handler):
    # Start a new thread for each conversation
    thread = client.beta.threads.create()
    # Add a message to the thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )
    # Stream the response
    with client.beta.threads.runs.create_and_run_stream(
        thread_id=thread.id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
        model="gpt-4-turbo-preview",
        event_handler=event_handler
    ) as stream:
        for event in stream:
            if event.type == "thread.message.delta" and event.data.delta.content:
                text_content = event.data.delta.content[0].text
                response_placeholder.markdown(f'**AI**: {text_content}', unsafe_allow_html=True)

# Define the EventHandler class for streaming
class EventHandler:
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.responses = []

    def on_text_delta(self, delta: TextDelta, snapshot: Text):
        # Accumulate text deltas and update the Streamlit placeholder
        self.responses.append(delta.value)
        new_text = "".join(self.responses)
        self.placeholder.markdown(f'**AI**: {new_text}', unsafe_allow_html=True)

# User input
user_input = st.text_input("Ask a question to the Assistant:", key='input')

if st.button('Send') and user_input:
    # Clear previous responses
    response_placeholder.markdown('')
    # Display user's question
    st.write(f'**You**: {user_input}')
    # Handle the conversation
    talk_to_assistant(user_input, EventHandler(response_placeholder))
    # Reset the input box after sending the message
    st.session_state['input'] = ''
