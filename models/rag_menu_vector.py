from langchain_community.document_loaders import TextLoader

from dotenv import load_dotenv
import os
import json
import sys
import time
from tqdm import tqdm

from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_upstage import UpstageEmbeddings

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import RunnablePassthrough

from langchain.vectorstores import Chroma
from langchain_upstage import ChatUpstage, UpstageEmbeddings

# Load environment variables
load_dotenv()

loader = TextLoader('menus.txt')
data = loader.load()

# Load API keys from environment variables
UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

llm = ChatUpstage(api_key=UPSTAGE_API_KEY)

# Use the recursive character splitter
recur_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=60,
    separators=["\n"]
)

# Perform the splits using the splitter
data_splits = list(tqdm(recur_splitter.split_documents(data), desc="Splitting documents", unit="chunk"))
#print(f"Number of splits: {len(data_splits)}")

# Vector Store 구축
embeddings = UpstageEmbeddings(
    api_key=UPSTAGE_API_KEY,
    model="solar-embedding-1-large"
)

persist_directory = '../.cache/db/menu'

vectordb = Chroma.from_documents(
    documents=data_splits, # 위에서 처리한 데이터 
    embedding=embeddings, # upstage solar embedding 1 large
    persist_directory=persist_directory)