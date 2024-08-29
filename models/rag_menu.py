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

# Load API keys from environment variables
UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

llm = ChatUpstage(api_key=UPSTAGE_API_KEY)

# Vector Store 구축
embeddings = UpstageEmbeddings(
    api_key=UPSTAGE_API_KEY,
    model="solar-embedding-1-large"
)

persist_directory = '../.cache/db/menu'

vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

retriever = vectordb.as_retriever()


from TEMPLATES.rag_template import menu_prompt

rag_prompt = ChatPromptTemplate.from_template(menu_prompt)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Define the RAG chain
menu_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)