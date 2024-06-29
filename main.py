# app.py
from flask import Flask, request, jsonify, render_template, redirect, url_for
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import logging
import warnings
import prompts

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


prompt_selection = prompts.prompt_2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore")

load_dotenv()  # Loads .env file

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Loads API key
secret_real_tokens = os.environ.get('SECRETTOKENS')

if not secret_real_tokens:
    raise ValueError('SECRETTOKENS is not set in the .env file')


app = Flask(__name__)
Logs.send("Starting API server...")

##### Text #####
folder_path = "txt_docs"
def get_txt_text(folder_path):
    text = ""
    # List all files in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            # Create a full file path
            file_path = os.path.join(folder_path, filename)
            # Open and read the text file
            with open(file_path, 'r', encoding='utf-8') as file:
                text += file.read() + "\n"  # Append the content of the text file to the 'text' string
    return text

##### CHUNKS ######
def get_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=20000, chunk_overlap=10000)
    chunks = text_splitter.split_text(text)
    return chunks

##### VECTOR STORE ######
def get_vector_store(text_chunks):
    try:
        # Create embeddings using a Google Generative AI model
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

        # Create a vector store using FAISS from the provided text chunks and embeddings
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)

        # Save the vector store locally with the name "faiss_index"
        index_dir = "faiss_index"
        os.makedirs(index_dir, exist_ok=True)
        vector_store.save_local(index_dir)
        logger.info(f"FAISS index saved to {index_dir}")
    except Exception as e:
        logger.error(f"Error creating or saving FAISS index: {e}")
SECRET_TOKEN = secret_real_tokens

def validate_token(request):
    token = request.headers.get('Authorization')
    if token != f"Bearer {SECRET_TOKEN}":
        return False
    return True


##### CHAINS ######
def get_conversational_chain():
    prompt_template = prompt_selection
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, max_tokens=1024)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    if not validate_token(request):
        return jsonify({"error": "Forbidden"}), 403
    user_question = request.json.get('question', '')

    # Create embeddings for the user question using a Google Generative AI model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    try:
        # Load a FAISS vector database from a local file
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        logger.info("FAISS index loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load FAISS index: {e}")
        return jsonify({"error": "Failed to load FAISS index"}), 500

    # Perform similarity search in the vector database based on the user question
    docs = new_db.similarity_search(user_question, k=5)  # Retrieve top 5 most similar chunks

    # Obtain a conversational question-answering chain
    chain = get_conversational_chain()

    # Use the conversational chain to get a response based on the user question and retrieved documents
    response = chain(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True
    )

    return jsonify({"response": response["output_text"]})

@app.route('/process', methods=['POST'])
def process():
    raw_text = get_txt_text(folder_path)
    text_chunks = get_chunks(raw_text)
    get_vector_store(text_chunks)
    return jsonify({"message": "Processing Done!"})

@app.route("/api/status", methods=["GET"])
def status():
    if not validate_token(request):
        return jsonify({"error": "Forbidden"}), 403

    try:
        return jsonify({"status": "Ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False)