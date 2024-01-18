from langchain.chains import LLMChain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv, find_dotenv
import os
import streamlit as st
import openai

st.set_page_config(page_title="StreamlitChatMessageHistory", page_icon="📖")
st.title("📖 StreamlitChatMessageHistory")

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

view_messages = st.expander("View the message contents in session state")

if st.button("Clear messages", key="clear_messages"):
    msgs.clear()

load_dotenv(find_dotenv())
openai_api_key = os.environ['OPENAI_API_KEY']

# Set up the LangChain, passing in Message History
template = """
    Anda adalah asisten yang sangat membantu yang dapat menjawab pertanyaan tentang apapun yang ada didalam dokumen berdasarkan transkrip: {docs}
    
    Hanya gunakan informasi faktual dari dokumen, jangan gunakan opini Anda sendiri.
    
    Jika Anda merasa tidak tahu jawabannya, katakan saja "Saya tidak tahu".
    
    Jika pertanyaannya meminta untuk mencari informasi lewat internet, katakan saja "Silakan hubungi admin", dan berikan penjelasan bahwa apa yang anda ketahui hanya berdasarkan dokumen.
    
    Jawaban Anda harus singkat dan jelas.
"""
system_message_prompt = SystemMessagePromptTemplate.from_template(template)

human_template = "Jawablah pertanyaan berikut ini: {question}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

chat = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)
chain = LLMChain(llm=chat, prompt=chat_prompt)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are an AI chatbot having a conversation with a human."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

chain = prompt | ChatOpenAI(api_key=openai_api_key)
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,
    input_messages_key="question",
    history_messages_key="history",
)

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

# If user inputs a new prompt, generate and draw a new response
if prompt := st.chat_input():
    st.chat_message("human").write(prompt)
    # Note: new messages are saved to history automatically by Langchain during run
    config = {"configurable": {"session_id": "any"}}
    response = chain_with_history.invoke({"question": prompt}, config)
    st.chat_message("ai").write(response.content)

# Draw the messages at the end, so newly generated ones show up immediately
with view_messages:
    """
    Message History initialized with:
    ```python
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    ```

    Contents of `st.session_state.langchain_messages`:
    """
    view_messages.json(st.session_state.langchain_messages)