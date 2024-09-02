import bs4
from langchain import hub
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os
from glob import glob

# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv

# API 키 정보 로드
load_dotenv()

from langchain_community.document_loaders import TextLoader

import argparse

# Set up argument parsing to get values from the command line
parser = argparse.ArgumentParser(description="Configure text splitting and document loading.")
parser.add_argument('--patient_id', type=str, required=True, help='Name for specifying the directory (e.g., 남A).')

args = parser.parse_args()

# Use the provided name argument for directory paths
patient_id = args.patient_id


loader = TextLoader(f"./data/{patient_id}/{patient_id}.md")
docs = loader.load()
print(f"문서의 수: {len(docs)}")

from dotenv import load_dotenv
import os
import json
import sys
import time
from tqdm import tqdm
from langchain_community.vectorstores import Chroma
# from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_upstage import UpstageEmbeddings

# Load environment variables
load_dotenv()

# Load API keys from environment variables
UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

start_time = time.time()

# Use the recursive character splitter
recur_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=60,
    separators=["- ", "\n#", "\n\n", "\n", " ", ""]
)

# Perform the splits using the splitter
data_splits = list(tqdm(recur_splitter.split_documents(docs), desc="Splitting documents", unit="chunk"))
print(f"Number of splits: {len(data_splits)}")

# Vector Store 구축
embeddings = UpstageEmbeddings(
    api_key=UPSTAGE_API_KEY,
    model="solar-embedding-1-large"
)

vectordb = Chroma.from_documents(
    documents=data_splits, # 위에서 처리한 데이터 
    embedding=embeddings, # upstage solar embedding 1 large
    persist_directory=f'.cache/db/{patient_id}')

vectordb.persist()
vectordb = None

end_time = time.time()
elapsed_time = end_time - start_time

print(elapsed_time)