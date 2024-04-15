import os
import openai
import streamlit as st

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

# Function to run assistant within an existing thread or create a new one with file support
def run_assistant(question, file=None, thread_id=None):
    if file is not None:
        # Upload the file to OpenAI
        file_obj = client.beta.files.create(file=file.read(), purpose="user_message")
        file_id = file_obj.id
        file_info = {"id": file_id, "name": file.name}
    else:
        file_info = None

    if thread_id is None:
        # Create a new thread if one does not exist and include file if provided
        messages = [{
            "role": "user",
            "content": question,
            "file_ids": [file_info['id']] if file_info else []
        }]
        thread = client.beta.threads.create(messages=messages)
        thread_id = thread.id
    else:
        # Use the existing thread to maintain conversation context
        # and add a new message with or without a file
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question,
            file_ids=[file_info['id']] if file_info else []
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

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("What is up?")

if user_question:
    uploaded_file = st.file_uploader("Upload a file (optional)")
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
        if uploaded_file is not None:
            st.write("Uploaded file:", uploaded_file.name)
    with st.chat_message("assistant"):
        with st.spinner('Waiting for the assistant to respond...'):
            result, st.session_state['thread_id'] = run_assistant(user_question, uploaded_file, st.session_state['thread_id'])
            if isinstance(result, str):
                st.error(result)
            else:
                for message in result.data:
                    if message.role == "assistant":
                        response = message.content[0].text.value
                        st.markdown(response)
                        # Append only the assistant's response to the messages list
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        break
