import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Loads .env file

# Configure Google Generative AI
import google.generativeai as genai
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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

def get_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=20000, chunk_overlap=10000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    try:
        # Create embeddings using a Google Generative AI model
        logger.info("Creating embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        
        # Create a vector store using FAISS from the provided text chunks and embeddings
        logger.info("Creating FAISS vector store...")
        vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        
        # Save the vector store locally with the name "faiss_index"
        index_dir = "faiss_index"
        os.makedirs(index_dir, exist_ok=True)
        logger.info(f"Saving FAISS index to {index_dir}...")
        vector_store.save_local(index_dir)
        
        # Verify the existence of the file
        index_file_path = os.path.join(index_dir, "index.faiss")
        if os.path.exists(index_file_path):
            logger.info(f"FAISS index saved successfully at {index_file_path}")
        else:
            logger.error(f"FAISS index file not found at {index_file_path}")
    except Exception as e:
        logger.error(f"Error creating or saving FAISS index: {e}")

def main():
    raw_text = get_txt_text(folder_path)
    logger.info("Text loaded")
    text_chunks = get_chunks(raw_text)
    logger.info(f"Text split into {len(text_chunks)} chunks")
    get_vector_store(text_chunks)

if __name__ == "__main__":
    main()
