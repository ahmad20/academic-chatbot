from model import DocumentProcessor
import streamlit as st
import os

class Tools:
    def __init__(self):
        self.model = DocumentProcessor()
        temp_path = "temp"
        os.makedirs(temp_path, exist_ok=True)
        self.temp_path = temp_path
    
    def process_pdf_file(self, uploaded_file):
        file_name = uploaded_file.name
        save_path = os.path.join(self.temp_path, file_name)

        # Save the file locally
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        self.model.create_db_from_document(save_path)
        os.remove(save_path)
        st.success("PDF successfully processed")

    def process_data(self, input_text: str):
        if input_text.endswith(".pdf"):
            filepath = self.model.download_pdf(input_text, target_path=self.temp_path)
            self.model.create_db_from_document(filepath)
            os.remove(filepath)
            st.success("PDF successfully processed")
        elif "youtube.com" in input_text:
            self.model.create_db_from_video(input_text)
            st.success("Video successfully processed")
        else:
            st.error("Please enter a valid input")