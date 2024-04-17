import openai
import streamlit as st

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to run assistant within an existing thread or create a new one
def run_assistant(question, thread_id=None):
    if thread_id is None:
        # Create a new thread if one does not exist
        thread = openai.Thread.create(
            messages=[
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        thread_id = thread.id
    else:
        # Use the existing thread to maintain conversation context
        openai.Message.create(
            thread_id=thread_id,
            role="user",
            content=question
        )

    # Create and poll a run
    run = openai.Run.create_and_poll(
        thread_id=thread_id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in"
    )

    # Retrieve messages only if the run is completed
    if run.status == 'completed':
        messages = openai.Message.list(
            thread_id=thread_id
        )
        return messages, thread_id
    else:
        return f"Run status: {run.status}", thread_id

# Streamlit UI setup
st.title('Chat with GPT-4')

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = None

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_question = st.chat_input("What is up?")

if user_question:
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        with st.spinner('Waiting for the assistant to respond...'):
            result, st.session_state['thread_id'] = run_assistant(user_question, st.session_state['thread_id'])
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
