import streamlit as st
from tools import Tools

def input_tab(t: Tools):
    st.subheader("Input Tab")
    input_text = st.text_area("Enter URL (PDF or YouTube URL):", "")

    # Button to process data
    if st.button("Process Data", key="text_input"):
        try:
            if input_text.strip():
                t.process_data(input_text)
            else:
                st.error("Please enter a valid input")
        except Exception as e:
            st.error(f"Error: {e}")
    
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])
    if st.button("Process Data", key="file_input"):
        try:
            if uploaded_file:
                t.process_pdf_file(uploaded_file)
            else:
                st.error("Please enter a valid input")
        except Exception as e:
            st.error(f"Error: {e}")
    