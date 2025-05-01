Just Random Chatbot for Academic in Telkom University


# 🎓 Academic Chatbot – Talk with Your PDFs and YouTube Videos

## Overview

Research and learning often involve going through long academic papers or lectures. It can be overwhelming and time-consuming to find specific information buried in pages of PDFs or hours of video.

**Academic Chatbot** makes that easier. Just upload a PDF or share a YouTube video URL, and you can **ask questions directly** as if you're chatting with the content itself.

No need to scroll or scrub through hours of material—just type your question and get an answer in seconds.

---

## 🚀 What It Can Do

- 📄 **Understand academic PDFs** – Ask questions about your research papers, articles, or assignments.
- 🎥 **Analyze YouTube lectures** – Chat with lecture content using just the video link.
- 💬 **Conversational Q&A** – Get clear answers in chat format.
- ⚡ **Quick and easy** – No technical setup required. Just upload and chat.

---

## 💡 How It Works (Simple Explanation)

1. **You upload a PDF** or provide a **YouTube video link**.
2. The system processes the content and prepares it for conversation.
3. You start asking questions like:  
   _“What is the main conclusion of this paper?”_  
   _“What are the key points discussed in the second half of the video?”_
4. The chatbot gives you helpful, relevant answers based on the content you uploaded.

---

## 🔧 Under the Hood (Optional for the Curious)

This project uses a smart process called **RAG** (Retrieval-Augmented Generation), which combines the best of search and AI generation.

- 🧠 **Langchain** is used to manage how your questions are processed and answered.
- 🗃️ It stores the knowledge using **FAISS**, a fast vector database.
- ✨ It understands meaning using **OpenAI embeddings**.
- 🌐 All this is wrapped in a simple, friendly **Streamlit** web app.

## 🧰 What You Need

To run this chatbot on your own:

- Python 3.8+
- A free or paid **OpenAI API key**
- Internet connection

---

## ⚙️ How to Use

1. Clone the repository:

```bash
git clone https://github.com/ahmad20/academic-chatbot.git
cd academic-chatbot
```
2. Install the required libraries:

```bash
pip install -r requirements.txt
```
3. Set your OpenAI API key in .env or environment variables.

4. Start the app:

```bash
streamlit run app.py
```
5. Open your browser and go to:

```bash
http://localhost:8501
```

6. Upload a PDF or paste a YouTube link, then start chatting!

## 📝 Example Use Case
You're studying for an exam and have a 30-page academic article. Instead of reading every line, you upload the PDF and ask:

“What methods were used in this study?”
“What are the main findings in section 4?”

Or you want to learn from a 1-hour recorded lecture on YouTube. Just paste the link and ask:
```
“What topics are covered in this lecture?”
“Summarize the part where the speaker talks about deep learning.”
```
## 🙌 Contributions
Have ideas to improve the chatbot? Want to add features like file history, summaries, or multi-language support?
Pull requests and suggestions are always welcome!

Made with ❤️ for researchers, students, and lifelong learners.
