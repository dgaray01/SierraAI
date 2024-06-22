# app.py
import os
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

app = Flask(__name__)

# HuggingFace API Token

load_dotenv()
api_token = os.environ.get('HUGGINGFACEHUB_API_TOKEN')

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

print("Documents loaded successfully")

# Split documents into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=chunkSize, chunk_overlap=chunkOverlap)
chunks = splitter.split_documents(docs)

# Check if chunks are created correctly
if not chunks:
    raise ValueError("No chunks created. Please check the splitting logic.")

print("Chunks created successfully")

# Get Embedding Model from HF via API

embeddings = HuggingFaceInferenceAPIEmbeddings(api_key=api_token, model_name="BAAI/bge-base-en-v1.5")

# Generate embeddings for the chunks
chunk_texts = [chunk.page_content for chunk in chunks]
chunk_embeddings = embeddings.embed_documents(chunk_texts)

# Check if embeddings are generated correctly
if not chunk_embeddings or len(chunk_embeddings) != len(chunk_texts):
    raise ValueError("Embeddings generation failed. Please check the embedding model and input data.")

print("Embeddings generated successfully")

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
Also No need to say "According to the context provided" everytime you begin a sentence

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

@app.route("/ask", methods=["POST"])
def ask():
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

if __name__ == "__main__":
    app.run()
