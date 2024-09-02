from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Solve CORS prob(called by Dart, Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 헤더를 허용
)

# Define the logging with the project name
logging.langsmith("NursingHome")

# Define the Prompt Template
prompt = PromptTemplate.from_template(
    """주어진 사용자 질문을 `환자정보`, `메뉴`, 또는 `병원비` 중 하나로 분류하세요. 한 단어 이상으로 응답하지 마세요. 한글로 답변하세요.

<question>
{question}
</question>

Classification:"""
)

# Initialize the LLM with the API key
llm = ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"))

# Create the initial chain
chain = prompt | llm | StrOutputParser()

# Import other templates and chains
#from TEMPLATES.rag_template import prompt, menu_prompt
from rag_menu import menu_chain
from rag_patient import patient_chain  # Updated import
# from no_rag_patient import chain as patient_chain
from rag_patient_n1 import patient_chain as patient_chain_n1
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
        # Pass patient_id along to the patient_chain
        return patient_chain(info.get("patient_id", ""))
    
# def route(info):
#     if "병원비" in info["topic"].lower():
#         return bill_chain
#     elif "메뉴" in info["topic"].lower():
#         return menu_chain
#     else:
#         # Pass patient_id along to the patient_chain
#         return patient_chain

def route1(info):
    if "병원비" in info["topic"].lower():
        return bill_chain
    elif "메뉴" in info["topic"].lower():
        return menu_chain
    else:
        # Pass patient_id along to the patient_chain
        return patient_chain_n1(info.get("patient_id", ""))

# Full chain including routing logic
full_chain = (
    {"topic": chain, "question": itemgetter("question")}
    | RunnableLambda(route)
    | StrOutputParser()
)

full_chain1 = (
    {"topic": chain, "question": itemgetter("question")}
    | RunnableLambda(route1)
    | StrOutputParser()
)

# Define a request model for FastAPI
class QueryRequest(BaseModel):
    question: str
    patient_id: str  # Add patient_id to the request model


# Define the response model for FastAPI
class QueryResponse(BaseModel):
    response: str


import logging

logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 콘솔에도 로그 출력
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)


# Create the main endpoint
@app.post("/n2")
async def process_query(request: QueryRequest):
    try:
        # Pass the patient_id and question to the full_chain
        result = full_chain.invoke(
            {"question": request.question, "patient_id": request.patient_id}
        )
        logging.info(f"결과:{result}")

        # Return the response
        content = {"response": result}
        return JSONResponse(
            content=content, media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))


# Create the main endpoint
@app.post("/n1")
async def process_query(request: QueryRequest):
    try:
        # Pass the patient_id and question to the full_chain
        result = full_chain1.invoke(
            {"question": request.question, "patient_id": request.patient_id}
        )
        logging.info(f"결과:{result}")

        # Return the response
        content = {"response": result}
        return JSONResponse(
            content=content, media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))