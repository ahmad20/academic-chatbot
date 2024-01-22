from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from dotenv import load_dotenv, find_dotenv
import os
import openai
import streamlit as st

def chatbot_tab():
    load_dotenv(find_dotenv())
    openai.api_key = os.environ['OPENAI_API_KEY']
    
    st.subheader("Chatbot Tab")
    
    # Set up memory
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    memory = ConversationBufferMemory(memory_key="history", chat_memory=msgs, input_key="question")
    if len(msgs.messages) == 0:
        msgs.add_ai_message("How can I help you?")

    view_messages = st.expander("View the message contents in session state")

    # Clear button to clear inputs and responses
    if st.button("Clear", key="clear"):
        msgs.clear()

    # Set up the LangChain, passing in Message History
    template = """
        
        Anda adalah asisten yang sangat membantu yang dapat menjawab pertanyaan tentang apapun yang ada didalam dokumen berdasarkan transkrip: {docs}
        
        Ini adalah riwayat percakapan sebelumnya dan dapat anda gunakan jika terdapat pertanyaan yang merujuk ke riwayat tersebut {history}
        
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
    chain = LLMChain(llm=chat, prompt=chat_prompt, memory=memory)
    
    # Render current messages from StreamlitChatMessageHistory
    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)
      
    
    # If user inputs a new prompt, generate and draw a new response
    if chat_prompt := st.chat_input():
        embedding = OpenAIEmbeddings()
        db = FAISS.load_local("vectorstores", embedding)
        history_message = [msg.content for msg in msgs.messages]
        db2 = FAISS.from_texts(history_message, embedding)
        db.merge_from(db2)
        
        docs = db.similarity_search(chat_prompt, k=4)
        docs_page_content = " ".join([doc.page_content for doc in docs])
        st.chat_message("human").write(chat_prompt)
        config = {"configurable": {"session_id": "any"}}
        response = chain.invoke({
            'question': chat_prompt,
            'docs': docs_page_content,
            'history': msgs.messages,
        }, config)
        st.chat_message("ai").write(response.get('text', 'Error'))
        
    
    # Draw the messages at the end, so newly generated ones show up immediately
    with view_messages:
        view_messages.json(st.session_state.langchain_messages)