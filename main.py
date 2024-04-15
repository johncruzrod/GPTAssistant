import os
import openai
import streamlit as st

# Initialize OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI()

def run_assistant(question):
    # Step 2: Create a Thread
    thread = client.beta.threads.create()

    # Step 3: Add a Message to the Thread
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )

    # Step 4: Create a Run
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id="asst_s0ZnaVjEm8CnagISufIAQ1in",
        instructions="The user works for a life insurance company. You will be fed a file with some information on a client, and need to identify if there is any extraordinary risk that the underwriter should take note of. The files will most likely be PDFs. You should keep communication to a minimum, as you will only be fed a file, and no message, and should only reply with the risk assessment. Always reply in markdown. "
    )

    # Check if the run is completed and retrieve messages
    if run.status == 'completed': 
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        return messages
    else:
        return f"Run status: {run.status}"

# Streamlit UI setup
st.title('OpenAI Assistant Interaction')
user_question = st.text_input("Enter your question here:", placeholder="Type your math question...")

if st.button('Submit Question'):
    if user_question:
        with st.spinner('Waiting for the assistant to respond...'):
            result = run_assistant(user_question)
            if isinstance(result, str):
                st.error(result)
            else:
                responses = [message.content for message in result.data if message.role == "assistant"]
                for response in responses:
                    st.write(f"Assistant: {response}")
    else:
        st.error("Please enter a question to submit.")
