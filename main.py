import os
import openai
import streamlit as st
from typing_extensions import override
from openai import AssistantEventHandler

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

class EventHandler(AssistantEventHandler):
    def __init__(self):
        self.response = ""
        
    @override
    def on_text_created(self, text) -> None:
        self.response += f"\nassistant > "
        
    @override
    def on_text_delta(self, delta, snapshot):
        self.response += delta.value
        
    def on_tool_call_created(self, tool_call):
        self.response += f"\nassistant > {tool_call.type}\n"
    
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                self.response += delta.code_interpreter.input
            if delta.code_interpreter.outputs:
                self.response += f"\n\noutput >"
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        self.response += f"\n{output.logs}"

def run_assistant(question, thread_id):
    event_handler = EventHandler()
    try:
        with client.beta.threads.runs.stream(
            thread_id=thread_id,
            assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
            instructions=question,
            event_handler=event_handler,
        ) as stream:
            stream.until_done()
    except openai.error.APIError as e:
        st.error(f"OpenAI API returned an API Error: {e}")
        return None, thread_id, str(e)
    except openai.error.AuthenticationError as e:
        st.error(f"OpenAI API returned an Authentication Error: {e}")
        return None, thread_id, str(e)
    except openai.error.APIConnectionError as e:
        st.error(f"Failed to connect to OpenAI API: {e}")
        return None, thread_id, str(e)
    except openai.error.InvalidRequestError as e:
        st.error(f"Invalid Request Error: {e}")
        return None, thread_id, str(e)
    except openai.error.RateLimitError as e:
        st.error(f"OpenAI API request exceeded rate limit: {e}")
        return None, thread_id, str(e)
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None, thread_id, str(e)

    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    return messages, thread_id, event_handler.response

# Streamlit UI setup
st.title('OpenAI Assistant Interaction')

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        result, st.session_state['thread_id'], response = run_assistant(prompt, st.session_state['thread_id'])
        if result is not None:
            st.markdown(response)
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
