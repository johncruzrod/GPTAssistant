import openai
import streamlit as st
from openai.assistant import AssistantEventHandler

# Streamlit UI setup
st.title('Chat with OpenAI Assistant')
conversation_history = st.empty()
user_input = st.text_input("Ask a question to the Assistant:")

# Event handler class to handle streaming events
class EventHandler(AssistantEventHandler):
    def __init__(self):
        self.responses = []

    def on_text_delta(self, delta, snapshot):
        # This will append text as it comes in
        self.responses.append(delta.value)
        conversation_history.text_area("Conversation", value=''.join(self.responses), height=250, key='text_area')

# Function to handle the conversation
def talk_to_assistant(question):
    # Create an empty placeholder to accumulate messages
    if 'responses' not in st.session_state:
        st.session_state['responses'] = []
        
    st.session_state['responses'].append(f"You: {question}\n")
    
    # Update the conversation history
    conversation_history.text_area("Conversation", value=''.join(st.session_state['responses']), height=250, key='text_area')

    event_handler = EventHandler()

    # Using the create_and_run_stream method to initiate the conversation
    with openai.Streaming(client).create_and_run_stream(
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": question}],
        event_handler=event_handler
    ) as stream:
        stream.until_done()

# Run the talk_to_assistant function when the 'Send' button is clicked
if st.button('Send') and user_input:
    talk_to_assistant(user_input)
    # Reset the input box after sending the message
    st.session_state['input'] = ''
