import streamlit as st
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override

# Use Streamlit's secret management to safely store and access your API key
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

assistant_id = "asst_s0ZnaVjEm8CnagISufIAQ1in"

class EventHandler(AssistantEventHandler):
    def __init__(self):
        self.report = []
        
    @override
    def on_text_created(self, text) -> None:
        self.report.append(f"\n\nAssistant: ")
        
    @override
    def on_text_delta(self, delta, snapshot):
        self.report[-1] += delta.value

    def on_tool_call_created(self, tool_call):
        self.report.append(f"\n\nAssistant used tool: {tool_call.type}\n")

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                self.report[-1] += delta.code_interpreter.input
            if delta.code_interpreter.outputs:
                self.report[-1] += "\nOutput:\n"
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        self.report[-1] += f"\n{output.logs}"

st.title("OpenAI Assistant Conversation")

if 'thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state['thread_id'] = thread.id

user_input = st.text_input("Enter your message:", key="input")

if st.button("Send"):
    client.beta.threads.messages.create(thread_id=st.session_state['thread_id'], role="user", content=user_input)
    
    event_handler = EventHandler()
    
    response_placeholder = st.empty()
    
    with client.beta.threads.runs.stream(
        thread_id=st.session_state['thread_id'],
        assistant_id=assistant_id,
        event_handler=event_handler,
    ) as stream:
        while True:
            try:
                stream.block_for_event()
                response_placeholder.markdown(''.join(event_handler.report))
            except TimeoutError:
                break

    st.session_state["input"] = ""  # Clear the input field
