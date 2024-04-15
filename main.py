import os
import openai
import streamlit as st
from typing_extensions import override
from openai import AssistantEventHandler

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

class EventHandler(AssistantEventHandler):    
    @override
    def on_text_created(self, text) -> None:
        st.write(f"\nassistant > ", end="", flush=True)
        
    @override
    def on_text_delta(self, delta, snapshot):
        st.write(delta.value, end="", flush=True)
        
    def on_tool_call_created(self, tool_call):
        st.write(f"\nassistant > {tool_call.type}\n", flush=True)
    
    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                st.write(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                st.write(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        st.write(f"\n{output.logs}", flush=True)

def run_assistant(question, thread_id):
    with client.beta.threads.runs.stream(
        thread_id=thread_id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
        instructions=question,
        event_handler=EventHandler(),
    ) as stream:
        stream.until_done()
    
    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    return messages, thread_id

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
        try:
            result, st.session_state['thread_id'] = run_assistant(prompt, st.session_state['thread_id'])
            response = result.data[-1].content[0].text.value
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )
        except:
            rate_limit_message = """
            Oops! Sorry, I can't talk now. Too many people have used
            this service recently.
            """
            st.session_state.messages.append(
                {"role": "assistant", "content": rate_limit_message}
            )
            st.rerun()
