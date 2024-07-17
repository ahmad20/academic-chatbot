
from langchain_community.document_loaders import (
    PyPDFLoader,
    YoutubeLoader
)
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import load_dotenv, find_dotenv
from data import Data

import os
import openai
import requests
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser

class DocumentProcessor:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.embedding = OpenAIEmbeddings()
        openai.api_key = os.environ['OPENAI_API_KEY']
        self.data = Data()

    def load_db(self):
        db = FAISS.load_local("vectorstores", self.embedding, allow_dangerous_deserialization=True)
        return db

    @staticmethod
    def is_vectorstores_empty():
        return len(os.listdir("vectorstores")) == 0

    def save_to_db(self, docs):
        if type(docs) == str:
            fun = FAISS.from_texts
            docs = [docs]
        else:
            fun = FAISS.from_documents
        try:
            if self.is_vectorstores_empty():
                db = fun(docs, self.embedding)
            else:
                db = self.load_db()
                new_db = fun(docs, self.embedding)
                db.merge_from(new_db)
            
            db.save_local("vectorstores")
            print("Success")
            return "Success"
        except Exception as e:
            print(f"Error: {e}")
            return "Error: " + str(e)

    def process_and_save(self, docs):
        try:
            if not(type(docs) == str):
                docs = self._split_text_into_documents(docs)
            self.save_to_db(docs)
        except Exception as e:
            raise Exception(f"Error when processing and saving to database: {e}")

    def create_db_from_json(self, document_path):
        with open(document_path, 'r') as file:
            json_data = json.load(file)
        self.data.set_data(document_path)
        for item in json_data:
            q = item["question"]
            a = item["answer"]
            s = item["source"]
            text = f"Q: {q} A: {a} S: {s}"
            self.process_and_save(text)
        
            
    def create_db_from_video(self, video_url):
        loader = YoutubeLoader.from_youtube_url(
            video_url,
            language=["id"],
            translation="id",
        )
        transcript = loader.load()
        self.data.set_data(video_url)
        self.process_and_save(transcript)

    def create_db_from_document(self, document_path):
        loader = PyPDFLoader(document_path)
        text = loader.load()
        self.data.set_data(document_path)
        self.process_and_save(text)

    @staticmethod
    def download_pdf(url, target_path):
        filename = url.split("/")[-1]
        filepath = os.path.join(target_path, filename)

        if not str(url).endswith(".pdf"):
            raise Exception("URL does not point to a PDF file")

        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, 'wb') as pdf_file:
                pdf_file.write(response.content)
            return filepath
        else:
            raise Exception("Could not download PDF")

    def get_response_from_query(self, db, query, k=4):
        docs = db.similarity_search(query, k)
        # sources = [doc.metadata["source"] for doc in docs][0]
        docs_page_content = " ".join([doc.page_content for doc in docs])
        chat = self._initialize_chat_model()
        
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
        chain = chat_prompt | chat | StrOutputParser()
        # response = self._run_chat_chain(chat, query, docs_page_content)
        response = chain.invoke({
            'question': query,
            'docs': docs_page_content,
            'history': [],
            'topic': "academic",
        }, {"configurable": {"session_id": "any"}})
        return response, docs_page_content

    def _load_text_from_document(self, document_path):
        loader = PyPDFLoader(document_path)
        return loader.load()

    def _split_text_into_documents(self, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return text_splitter.split_documents(text)

    def _initialize_chat_model(self):
        return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)
