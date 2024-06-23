# app.py
import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain.llms import HuggingFaceHub
from langchain.retrievers import BM25Retriever, EnsembleRetriever
import logging

class Logs:
    @staticmethod
    def setup_logging():
        # Set up the logging configuration
        logging.basicConfig(
            level=logging.DEBUG,  # Default logging level
            format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
            datefmt='%Y-%m-%d %H:%M:%S',  # Date format
            handlers=[
                logging.StreamHandler()  # Output to console
            ]
        )

    @staticmethod
    def error(message):
        # Log an error message
        logging.error(message)

    @staticmethod
    def send(message):
        # Log an informational message
        logging.info(message)

# Set up the logging system
Logs.setup_logging()


app = Flask(__name__)

Logs.send("Starting API server...")

# HuggingFace API Token

load_dotenv()
api_token = os.environ.get('HUGGINGFACEHUB_API_TOKEN')
secret_real_tokens = os.environ.get('SECRETTOKENS')

if not api_token:
    raise ValueError('HUGGINGFACEHUB_API_TOKEN is not set in the .env file')

# Paramters

chunkSize = 800
chunkOverlap = 100

temperature = 0.3
maxTokens = 1024


# Load and clean text file
file_path = "data_point65.txt"
loader = TextLoader(file_path)
docs = loader.load()

# Check if documents are loaded correctly
if not docs:
    raise ValueError("No documents found. Please check the file path and content.")

Logs.send("Documents loaded succesfully")

# Split documents into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=chunkSize, chunk_overlap=chunkOverlap)
chunks = splitter.split_documents(docs)

# Check if chunks are created correctly
if not chunks:
    raise ValueError("No chunks created. Please check the splitting logic.")

Logs.send("Chunks created")

# Get Embedding Model from HF via API

embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=api_token, model_name="BAAI/bge-base-en-v1.5")

# Generate embeddings for the chunks
chunk_texts = [chunk.page_content for chunk in chunks]
chunk_embeddings = embeddings.embed_documents(chunk_texts)

# Check if embeddings are generated correctly
if not chunk_embeddings or len(chunk_embeddings) != len(chunk_texts):
    raise ValueError("Embeddings generation failed. Please check the embedding model and input data.")

Logs.send("Embeddings generated successfully")

# Create VectorStore with the selected embedding model
vectorstore = Chroma.from_documents(chunks, embeddings)

# Ensure the VectorStore retriever is working correctly
vectorstore_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
keyword_retriever = BM25Retriever.from_documents(chunks)
keyword_retriever.k = 3

# Create Ensemble Retriever
ensemble_retriever = EnsembleRetriever(retrievers=[vectorstore_retriever, keyword_retriever], weights=[0.5, 0.5])

# Initialize the LLM
llm = HuggingFaceHub(repo_id="HuggingFaceH4/zephyr-7b-beta", model_kwargs={"temperature": temperature, "max_new_tokens": maxTokens}, huggingfacehub_api_token=api_token)

# Define the prompt template
template = """
>
You are a helpful AI Assistant that follows instructions extremely well.
Use the following context to answer user question. No need to say ""I don't know"" if the answer is not in the context.

Think step by step before answering the question. You will get a $100 tip if you provide correct answer.
Also No need to say "According to the context provided" everytime you begin a sentence.

CONTEXT: {context}
</s>

{query}
</s>
"""
prompt = ChatPromptTemplate.from_template(template)
output_parser = StrOutputParser()

# Create the chain
chain = (
    {"context": ensemble_retriever, "query": RunnablePassthrough()}
    | prompt
    | llm
    | output_parser
)

SECRET_TOKEN = secret_real_tokens

def validate_token(request):
    token = request.headers.get('Authorization')
    if token != f"Bearer {SECRET_TOKEN}":
        return False
    return True

@app.route("/api/ask", methods=["POST"])
def ask():
    if not validate_token(request):
        return jsonify({"error": "Forbidden"}), 403
    
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    try:
        response = chain.invoke(question)
        cleaned_response = response.split("</s>")[-1].strip()
        return jsonify({"response": cleaned_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/status", methods=["GET"])
def status():
    if not validate_token(request):
        return jsonify({"error": "Forbidden"}), 403
    
    try:
        return jsonify({"status": "Ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500
if __name__ == "__main__":
    app.run()
