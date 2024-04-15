import os
import openai
import streamlit as st

# Assuming the API key is set in your environment variables or Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Function to interact with the OpenAI Assistant
def ask_assistant(question):
    # Create a new thread for the conversation
    thread = openai.Thread.create()
    
    # Add user's question to the thread
    message = openai.Message.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )
    
    # Run the assistant on the thread
    run = openai.Run.create(
        thread_id=thread.id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in"
    )
    
    # Retrieve the run until it's completed
    while True:
        run_status = openai.Run.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == "completed":
            # Retrieve all messages added by the assistant
            all_messages = openai.Message.list(
                thread_id=thread.id
            )
            return all_messages.data[-1].content
        elif run_status.status in ["queued", "in_progress"]:
            st.warning(f"Processing: {run_status.status}")
            st.experimental_rerun()
        else:
            st.error("Failed to process the request")
            return None

# Streamlit UI components
st.title('Math Tutor Assistant')
user_question = st.text_input("Enter your math question here:", placeholder="E.g., What is the integral of 3x^2?")

if st.button('Ask'):
    if user_question:
        with st.spinner('Fetching the answer...'):
            response = ask_assistant(user_question)
            st.write(f"**Assistant:** {response}")
    else:
        st.error("Please enter a question.")
