import openai
import streamlit as st

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

# Function to run assistant within an existing thread or create a new one
def run_assistant(question, thread_id=None):
    if thread_id is None:
        # Create a new thread if one does not exist
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Add user's question to the thread
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=question
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
        return messages.data, thread_id
    else:
        return None, thread_id

# Streamlit UI setup
st.title('OpenAI Assistant Interaction')

# Initialize chat history if not already initialized
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state['thread_id'] = None

# Display chat messages from history
for message in reversed(st.session_state.messages):
    author = "user" if message.role == "user" else "assistant"
    st.chat_message(message.content, author)

# Accept user input
user_question = st.chat_input("Enter your question:")
if user_question:
    # Append user question to conversation history
    st.session_state.messages.append(openai.openai_object.OpenAIObject(role="user", content=user_question))
    
    # Run the assistant and get the response
    with st.spinner('Waiting for the assistant to respond...'):
        result, thread_id = run_assistant(user_question, st.session_state.get('thread_id'))
        st.session_state['thread_id'] = thread_id
        if result is None:
            st.error(f"No response from the assistant, try again.")
        else:
            # Process assistant messages and display
            assistant_response = None
            for message in result:
                if message.role == "assistant":
                    assistant_response = message.content
                    break
            
            if assistant_response:
                # Append assistant response to conversation history
                st.session_state.messages.append(openai.openai_object.OpenAIObject(role="assistant", content=assistant_response))
                st.chat_message(assistant_response, "assistant")
