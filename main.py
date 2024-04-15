import streamlit as st
from openai import OpenAI
from typing_extensions import override
from openai import AssistantEventHandler

# Initialize Streamlit app
st.title('OpenAI Assistant Chat')

# Use Streamlit's secret management for the API key
api_key = st.secrets["OPENAI_API_KEY"]

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# Streamlit widgets to collect user input
user_input = st.text_input("You:", "")

# Placeholder for the chat history
chat_history_placeholder = st.empty()

# Store the conversation history
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

if 'stream_active' not in st.session_state:
    st.session_state['stream_active'] = False

# EventHandler class to handle streaming events
class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        # This handles the creation of new text by the Assistant
        st.session_state['conversation'].append("Assistant: " + text.text)
    
    @override
    def on_text_delta(self, delta, snapshot):
        # This handles incremental text updates
        st.session_state['conversation'][-1] += delta.value

# Function to start the conversation with OpenAI Assistant
def chat_with_assistant(prompt):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )
    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
        instructions="Please be concise and to the point.",
        event_handler=EventHandler(),
    ) as stream:
        for _ in stream:  # Simply iterating through the stream to capture events
            pass

# If the user has entered input and the stream is not active, call the Assistant
if user_input and not st.session_state['stream_active']:
    st.session_state['stream_active'] = True
    chat_with_assistant(user_input)
    st.session_state['stream_active'] = False

# Display the conversation history
chat_history_placeholder.text_area("Chat History:", value="\n".join(st.session_state['conversation']), height=300)
