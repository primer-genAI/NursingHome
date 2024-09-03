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

llm = ChatUpstage(temperature=0, api_key=UPSTAGE_API_KEY)

# Embeddings setup
embeddings = UpstageEmbeddings(
    api_key=UPSTAGE_API_KEY,
    model="solar-embedding-1-large"
)

# Function to create the patient_chain with a specific patient_id
def patient_chain(patient_id, template):

    # Use patient_id to set the persist directory dynamically
    persist_directory = f'../.cache/db/{patient_id}'

    # Load the vector database for the specific patient
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    retriever = vectordb.as_retriever()
    rag_prompt = ChatPromptTemplate.from_template(template)

    # Function to format documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Define the RAG chain
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )