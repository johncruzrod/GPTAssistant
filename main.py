import openai
import streamlit as st

# Assuming 'openai' is already configured with the correct API key using Streamlit secrets
client = openai.OpenAI()

# Define the EventHandler to handle the stream
class EventHandler(openai.AssistantEventHandler):
    def __init__(self, placeholder):
        self.placeholder = placeholder
        super().__init__()

    def on_text_delta(self, delta: openai.TextDelta, snapshot: openai.Text):
        # Append new text from the delta event to the placeholder
        new_text = delta.value
        self.placeholder.markdown(f'**AI**: {new_text}', unsafe_allow_html=True)

# Streamlit UI setup
st.title('Chat with OpenAI Assistant')
response_placeholder = st.empty()
user_input = st.text_input("Ask a question to the Assistant:")

# Function to start streaming conversation
def start_streaming_conversation(question, event_handler):
    # Create a new thread and stream the response
    with client.beta.threads.create_and_run_stream(
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": question}],
        event_handler=event_handler
    ) as stream:
        stream.until_done()

# Handle the conversation when the 'Send' button is clicked
if st.button('Send') and user_input:
    response_placeholder.markdown(f'**You**: {user_input}')
    event_handler = EventHandler(response_placeholder)
    start_streaming_conversation(user_input, event_handler)
