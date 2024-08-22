Just Random Chatbot for Academic in Telkom University

pip install pypdf
pip install youtube-transcript-api
pip install faiss-cpu
pip install tiktoken


docker build -t academic-chatbot:0.0.1 .

docker run -p 8501:8501 -d --name academic academic-chatbot:0.0.1