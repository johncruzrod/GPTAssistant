import openai
import streamlit as st

# Assuming OpenAI key is correctly set in Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to run assistant within an existing thread or create a new one
def run_assistant(question, thread_id=None):
    if thread_id is None:
        # Create a new thread if one does not exist
        # Adjusted to use the correct API call as per your assistant API logic framework
        thread = openai.ChatCompletion.create(model="your_model_here", messages=[{"role": "system", "content": "Your system message"}])
        thread_id = thread['id']

    # Add user's question to the thread and retrieve the response directly, adapted to your API logic
    response = openai.ChatCompletion.create(
        model="your_model_here",  # Model should be replaced with your specific assistant model
        messages=[
            {"role": "user", "content": question}
        ],
        # Assuming thread_id is managed externally or within the parameters you wish to include
    )

    # Assuming 'response' follows a certain structure containing a message list similar to your API logic
    messages = response.get('messages', [])
    return messages, thread_id

st.title('OpenAI Assistant Interaction')

# Ensure the initialization of session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.thread_id = None

# Handling message display
for message in reversed(st.session_state.messages):
    author = "You" if message["role"] == "user" else "Assistant"  # Adjusted for consistency
    st.chat_message(message["content"], author)

# User interaction
user_question = st.text_input("Enter your question:", key="user_input")

# When user submits a question
if user_question and st.button('Send'):  # Using a button to trigger sending and processing
    # Append user question to conversation history
    st.session_state.messages.append({"role": "user", "content": user_question})

    # Run the assistant and get responses
    with st.spinner('Waiting for the assistant to respond...'):
        responses, thread_id = run_assistant(user_question, st.session_state.thread_id)
        st.session_state.thread_id = thread_id

        if responses:
            # Assuming the first assistant response is what we want to display
            for response in responses:
                if response['role'] == 'assistant':
                    st.session_state.messages.append({"role": "assistant", "content": response['content']})
                    break  # Assuming we only want the first assistant message after the user's query

# Clear input field after submission to prevent resending
st.session_state.user_input = ""
