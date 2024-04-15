import openai
import streamlit as st
from openai import AssistantEventHandler

# Initialize the OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Streamlit UI setup
st.title('Chat with OpenAI Assistant')
conversation_history = st.empty()
user_input = st.text_input("Ask a question to the Assistant:")

# Event handler class to handle streaming events
class EventHandler(AssistantEventHandler):
    def __init__(self, placeholder):
        self.placeholder = placeholder
        self.responses = []

    def on_text_delta(self, delta: TextDelta, snapshot: Text):
        # This will append text as it comes in
        self.responses.append(delta.value)
        # Update the placeholder with the current conversation
        self.placeholder.text_area("Conversation", value=''.join(self.responses), height=250, key='text_area')

# Function to handle the conversation
def talk_to_assistant(question, placeholder):
    # Update conversation history with the user's question
    if 'responses' not in st.session_state:
        st.session_state['responses'] = []
        
    st.session_state['responses'].append(f"You: {question}\n")
    placeholder.text_area("Conversation", value=''.join(st.session_state['responses']), height=250, key='text_area')

    # Create the event handler instance
    event_handler = EventHandler(placeholder)

    # Create a new thread and message, and start the streaming response
    thread = openai.Thread.create()
    message = openai.Message.create(
        thread_id=thread.id,
        role="user",
        content=question
    )

    # Start streaming the response using the event handler
    with openai.Streaming.create_run_and_stream(
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": question}],
        event_handler=event_handler
    ) as stream:
        stream.until_done()

# Run the talk_to_assistant function when the 'Send' button is clicked
if st.button('Send') and user_input:
    talk_to_assistant(user_input, conversation_history)
    # Reset the input box after sending the message
    st.session_state['input'] = ''
