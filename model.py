import os
import openai
import requests
from langchain.document_loaders import (
    PyPDFLoader,
    YoutubeLoader
)
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from dotenv import load_dotenv, find_dotenv
from data import Data

class DocumentProcessor:
    def __init__(self):
        load_dotenv(find_dotenv())
        self.embedding = OpenAIEmbeddings()
        openai.api_key = os.environ['OPENAI_API_KEY']
        self.data = Data()

    def create_db_from_document(self, document_path):
        text = self._load_text_from_document(document_path)
        docs = self._split_text_into_documents(text)
        db = FAISS.from_documents(docs, self.embedding)
        return db

    def load_db(self):
        db = FAISS.load_local("vectorstores", self.embedding)
        return db

    @staticmethod
    def is_vectorstores_empty():
        return len(os.listdir("vectorstores")) == 0

    def save_to_db(self, docs):
        try:
            if self.is_vectorstores_empty():
                print("Creating new vectorstore")
                db = FAISS.from_documents(docs, self.embedding)
            else:
                print("Appending to existing vectorstore")
                db = FAISS.load_local("vectorstores", self.embedding)
                new_db = FAISS.from_documents(docs, self.embedding)
                db.merge_from(new_db)
            
            db.save_local("vectorstores")
            return "Success"
        except Exception as e:
            return "Error: " + str(e)

    def process_and_save(self, docs):
        try:
            docs = self._split_text_into_documents(docs)
            self.save_to_db(docs)
        except Exception as e:
            raise Exception(f"Error when processing and saving to database: {e}")

    def create_db_from_video(self, video_url):
        loader = YoutubeLoader.from_youtube_url(
            video_url,
            language=["id"],
            translation="id",
        )
        transcript = loader.load()
        self.process_and_save(transcript)
        self.data.set_data(video_url)

    def create_db_from_document(self, document_path):
        loader = PyPDFLoader(document_path)
        text = loader.load()
        self.process_and_save(text)
        self.data.set_data(document_path)

    @staticmethod
    def download_pdf(url):
        filename = url.split("/")[-1]
        filepath = f"temp/{filename}"

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
        sources = [doc.metadata["source"] for doc in docs][0]
        docs_page_content = " ".join([doc.page_content for doc in docs])
        chat = self._initialize_chat_model()

        response = self._run_chat_chain(chat, query, docs_page_content)
        return response, sources

    def _load_text_from_document(self, document_path):
        loader = PyPDFLoader(document_path)
        return loader.load()

    def _split_text_into_documents(self, text):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        return text_splitter.split_documents(text)

    def _initialize_chat_model(self):
        return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

    def _run_chat_chain(self, chat, query, docs_page_content):
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

        chain = LLMChain(llm=chat, prompt=chat_prompt)

        return chain.run(question=query, docs=docs_page_content)
