from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores.faiss import FAISS
from langchain.memory import ConversationBufferMemory
# from langchain.chains import LLMChain
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
# from langchain.llms import OpenAI
# from langchain.runnables import RunnableSequence
# from langchain.runnables.openai_runnable import OpenAIRunnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from dotenv import load_dotenv, find_dotenv
import os, time
import openai
import streamlit as st

from tools import Tools

def chatbot_tab(t: Tools):
    load_dotenv(find_dotenv())
    openai.api_key = os.environ['OPENAI_API_KEY']
    
    st.subheader("Chatbot Tab")
    
    # Set up memory
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    # memory = ConversationBufferMemory(memory_key="history", chat_memory=msgs, input_key="question")
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

    chain = chat_prompt | chat | StrOutputParser()
    # chain = ConversationalRetrievalChain(
    #         llm=chat,
    #         prompt=template
    #     )
    # chain = LLMChain(llm=chat, prompt=chat_prompt, memory=memory)
    
    # Render current messages from StreamlitChatMessageHistory
    for msg in msgs.messages:
        st.chat_message(msg.type).write(msg.content)
      
    # Initialize embedding and FAISS variables in session state
    if 'embedding' not in st.session_state:
        st.session_state['embedding'] = OpenAIEmbeddings()
    if 'faiss_db' not in st.session_state:
        st.session_state['faiss_db'] = FAISS.load_local("vectorstores", st.session_state['embedding'], allow_dangerous_deserialization=True)

    # Function to update FAISS database with new messages
    def update_faiss_db(history_message):
        print("updating faiss db")
        db2 = FAISS.from_texts(history_message, st.session_state['embedding'])
        st.session_state['faiss_db'].merge_from(db2)
        
    # embedding = OpenAIEmbeddings()
    # If user inputs a new prompt, generate and draw a new response
    if query := st.chat_input("Enter a question..."):
        # db = t.model.load_db()
        # db = FAISS.load_local("vectorstores", embedding, allow_dangerous_deserialization=True)
        # history_message = [msg.content for msg in msgs.messages]
        # db2 = FAISS.from_texts(history_message, embedding)
        # db.merge_from(db2)
        history_message = [msg.content for msg in msgs.messages]
        update_faiss_db(history_message)
        db = st.session_state['faiss_db']
        
        docs = db.similarity_search(chat_prompt, k=4)
        docs_page_content = " ".join([doc.page_content for doc in docs])
        msgs.add_user_message(chat_prompt)
        st.chat_message("human").write(chat_prompt)
        config = {"configurable": {"session_id": "any"}}
        response = chain.invoke({
            'question': query,
            'docs': docs_page_content,
            'history': msgs.messages,
            'topic': "academic",
        }, config)
        
        def stream_data():
            for word in response.split(" "):
                yield word + " "
                time.sleep(0.02)
        msgs.add_ai_message(response)
        st.chat_message("ai").write(stream_data)
        # st.write_stream(stream_data)
        
    
    # Draw the messages at the end, so newly generated ones show up immediately
    with view_messages:
        view_messages.json(st.session_state["langchain_messages"])