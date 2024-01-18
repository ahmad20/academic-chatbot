import streamlit as st
from tools import Tools
from input_page import input_tab
from chatbot_page import chatbot_tab

t = Tools()

def main():
    st.set_page_config(page_title="Academic Chatbot", page_icon="📖")
    st.title("Academic Chatbot")

    selected_tab = st.sidebar.selectbox("Select Tab:", ["Input", "Chatbot"])
    if selected_tab == "Input":
        input_tab(t)
    elif selected_tab == "Chatbot":
        chatbot_tab()

if __name__ == "__main__":
    main()
