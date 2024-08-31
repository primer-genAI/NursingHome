import os
import sys
import time
import json
from dotenv import load_dotenv
from tqdm import tqdm
import argparse

from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_upstage import UpstageEmbeddings

# Load environment variables
load_dotenv()

# Load API keys from environment variables
UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

# Set up argument parsing to get values from the command line
parser = argparse.ArgumentParser(description="Configure text splitting and document loading.")
parser.add_argument('--chunk_size', type=int, default=1000, help='Chunk size for splitting the documents.')
parser.add_argument('--chunk_overlap', type=int, default=200, help='Chunk overlap for splitting the documents.')
parser.add_argument('--patient_id', type=str, required=True, help='Name for specifying the directory (e.g., 남A).')

args = parser.parse_args()

start_time = time.time()

# Use the provided name argument for directory paths
patient_id = args.patient_id
chunk_size = args.chunk_size
chunk_overlap = args.chunk_overlap

from langchain.document_loaders import JSONLoader

# Load documents from the specified directory
# loader = DirectoryLoader(f"../json/{patient_id}/", glob="*.json", show_progress=True)
loader = JSONLoader(
    file_path=f"../json/{patient_id}/{patient_id}.json",
    jq_schema='.[] | .text',
    text_content=False
)
docs = loader.load()

print(f"문서의 수: {len(docs)}")

# Use the recursive character splitter with command line arguments
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=chunk_size,
    chunk_overlap=chunk_overlap,
    separators=["\n\n", "\n", "-", "*", " ", ""]
)

# Perform the splits using the splitter
data_splits = list(tqdm(text_splitter.split_documents(docs), desc="Splitting documents", unit="chunk"))
print(f"Number of splits: {len(data_splits)}")

# Set up embeddings using the API key
embeddings = UpstageEmbeddings(
    api_key=UPSTAGE_API_KEY,
    model="solar-embedding-1-large"
)

# Define the persist directory using the provided name
persist_directory = f'../.cache/db/{patient_id}'

# Build the vector store
vectordb = Chroma.from_documents(
    documents=data_splits,
    embedding=embeddings,
    persist_directory=persist_directory
)

print(persist_directory)
vectordb.persist()
vectordb = None

# Display elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print(f'소요 시간 : {elapsed_time}')