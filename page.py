import streamlit as st
from model import DocumentProcessor
import os

m = DocumentProcessor()
def process_pdf_file(uploaded_file):
    file_name = uploaded_file.name
    save_directory = "temp"
    os.makedirs(save_directory, exist_ok=True)
    save_path = os.path.join(save_directory, file_name)

    # Save the file locally
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    st.success(f"File '{file_name}' uploaded and saved locally at {save_path}")
    m.create_db_from_document(save_path)
    os.remove(save_path)
    st.success("PDF successfully processed")

def process_data(input_text):
    if input_text.endswith(".pdf"):
        filepath = m.download_pdf(input_text)
        m.create_db_from_document(filepath)
        os.remove(filepath)
        st.success("PDF successfully processed")
    elif "youtube.com" in input_text:
        m.create_db_from_video(input_text)
        st.success("Video successfully processed")
    else:
        st.error("Please enter a valid input")

def input_tab():
    st.subheader("Input Tab")
    input_text = st.text_area("Enter URL (PDF or YouTube URL):", "")
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])

    # Button to process data
    if st.button("Process Data"):
        st.subheader("Status:")
        if input_text.strip():
            process_data(input_text)
        elif uploaded_file:
            process_pdf_file(uploaded_file)
        else:
            st.error("Please enter a valid input")

def chatbot_tab():
    st.subheader("Chatbot Tab")
    
    session_state = st.session_state
    if 'inputs' not in session_state:
        session_state.inputs = []
        session_state.responses = []

    # Input text area
    new_input = st.text_input("Your message:", "")

    # Save input to session state
    if st.button("Send"):
        session_state.inputs.append(new_input)

        # Replace this with your chatbot logic
        db = m.load_db()
        response, _ = m.get_response_from_query(db, new_input)
        session_state.responses.append(response)

    # Clear button to clear inputs and responses
    if st.button("Clear"):
        session_state.inputs = []
        session_state.responses = []

    text_width = 750  # Adjust the value as needed
    for input_text, response_text in zip(session_state.inputs[::-1], session_state.responses[::-1]):
        st.markdown(f"<div style='width:{text_width}px;'>Input: {input_text}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='width:{text_width}px;'>Response: <p>{response_text}<p></div>", unsafe_allow_html=True)
        st.markdown("---")

def main():
    st.title("Academic Chatbot")

    # Sidebar for tab selection
    selected_tab = st.sidebar.selectbox("Select Tab:", ["Input", "Chatbot"])

    # Display the selected tab
    if selected_tab == "Input":
        input_tab()
    elif selected_tab == "Chatbot":
        chatbot_tab()

if __name__ == "__main__":
    main()
