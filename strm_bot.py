import streamlit as st
from openai import OpenAI, AssistantEventHandler
import time

assistant_id = st.secrets["assistant_id"]
api_key = st.secrets["api_key"]

client = OpenAI(api_key=api_key)

# Session state initialization
if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "openai_model" not in st.session_state:
    st.session_state.openai_model = "gpt-3.5-turbo"
if "messages" not in st.session_state:
    st.session_state.messages = []

# Streamlit app
#st.set_page_config(page_title="HR BOT", page_icon=":speech_balloon:")

st.title("Employee Assistant Chatbot")
st.write("Ask any questions you have related to HR documents. If the assistant can't find the answer, it will let you know.")

# Create columns for buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Start Chat"):
        st.session_state.start_chat = True
        thread = client.beta.threads.create()
        st.session_state.thread_id = thread.id

with col3:
    if st.button("Clear chat when done"):
        st.session_state.messages = []
        st.session_state.start_chat = False
        st.session_state.thread_id = None

if st.session_state.start_chat:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Give it a try"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
            instructions="Please answer as a helpful HR assistant, but if you can't find the answer to their question in the document, just say 'I don't know'.",
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )

        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == 'assistant'
        ]

        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.markdown(message.content[0].text.value)

else:
    st.write("Click 'Start Chat' to begin.")