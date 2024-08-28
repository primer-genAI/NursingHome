from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_teddynote import logging
import os
from langchain_upstage import ChatUpstage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Load API keys from the .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Define the logging with the project name
logging.langsmith("NursingHome")

# Define the Prompt Template
prompt = PromptTemplate.from_template(
    """주어진 사용자 질문을 `환자정보`, `메뉴`, 또는 `병원비` 중 하나로 분류하세요. 한 단어 이상으로 응답하지 마세요.

<question>
{question}
</question>

Classification:"""
)

# Initialize the LLM with the API key
llm = ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"))

# Create the initial chain
chain = (
    prompt
    | llm
    | StrOutputParser()
)

# Import other templates and chains
from TEMPLATES.rag_template import prompt, menu_prompt
from rag_menu import menu_chain
from rag_patient import patient_chain
from rag_bill import bill_chain
from operator import itemgetter
from langchain_core.runnables import RunnableLambda

# Function to route the topic to the correct chain
def route(info):
    if "병원비" in info["topic"].lower():
        return bill_chain
    elif "메뉴" in info["topic"].lower():
        return menu_chain
    else:
        return patient_chain

# Full chain including routing logic
full_chain = (
    {"topic": chain, "question": itemgetter("question")}
    | RunnableLambda(route)
    | StrOutputParser()
)

# Define a request model for FastAPI
class QueryRequest(BaseModel):
    question: str

# Define the response model for FastAPI
class QueryResponse(BaseModel):
    response: str

# Create the main endpoint
@app.post("/process-query")
async def process_query(request: QueryRequest):
    try:
        # Process the question using the chain
        result = full_chain.invoke({"question": request.question})
        # Return the response
        return {'responce':result}
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))