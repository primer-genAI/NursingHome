from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from langchain_core.runnables import RunnablePassthrough

from langchain.vectorstores import Chroma
from langchain_upstage import ChatUpstage, UpstageEmbeddings


import os
import dotenv

dotenv.load_dotenv()

UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')

llm = ChatUpstage(api_key=UPSTAGE_API_KEY)

# Embeddings setup
embeddings = UpstageEmbeddings(
  api_key=UPSTAGE_API_KEY,
  model="solar-embedding-1-large"
)

persist_directory = '.cache/db/남A_의무기록지'

vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

retriever = vectordb.as_retriever()

from TEMPLATES.rag_template import prompt

rag_prompt = ChatPromptTemplate.from_template(prompt)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Define the RAG chain
patient_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)