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

# Solve CORS problem (called by Dart, Flutter)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from all domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

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
chain = prompt | llm | StrOutputParser()

# Import other templates and chains
from TEMPLATES.rag_template import prompt, menu_prompt
from rag_menu import menu_chain
from rag_patient import patient_chain  # Updated import
from rag_bill import bill_chain
from operator import itemgetter
from langchain_core.runnables import RunnableLambda

# Global dictionary to store chat history
chat_history = {}

# Function to route the topic to the correct chain
def route(info):
    if "병원비" in info["topic"].lower():
        return bill_chain
    elif "메뉴" in info["topic"].lower():
        return menu_chain
    else:
        # Pass patient_id along to the patient_chain
        return patient_chain(info.get("patient_id", ""))

# Full chain including routing logic
full_chain = (
    {"topic": chain, "question": itemgetter("question")}
    | RunnableLambda(route)
    | StrOutputParser()
)

# Define a request model for FastAPI
class QueryRequest(BaseModel):
    question: str
    patient_id: str  # Add patient_id to the request model

# Define the response model for FastAPI
class QueryResponse(BaseModel):
    response: str
    chat_history: list  # Add chat history to the response model

import logging

logging.basicConfig(
    filename="debug.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Console logging setup
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

# Create the main endpoint
@app.post("/process-query")
async def process_query(request: QueryRequest):
    try:
        # Pass the patient_id and question to the full_chain
        result = full_chain.invoke(
            {"question": request.question, "patient_id": request.patient_id}
        )
        logging.info(f"결과: {result}")

        # Save chat history
        if request.patient_id not in chat_history:
            chat_history[request.patient_id] = []

        # Append the new question and response to the chat history
        chat_history[request.patient_id].append({
            "question": request.question,
            "response": result
        })

        # Prepare the full chat history response
        content = {
            "response": result,
            "chat_history": chat_history[request.patient_id]
        }

        # Return the response including the current chat history
        return JSONResponse(
            content=content, media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        # Handle errors
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to retrieve chat history for a specific patient
@app.get("/chat-history/{patient_id}")
async def get_chat_history(patient_id: str):
    if patient_id in chat_history:
        return JSONResponse(content=chat_history[patient_id])
    else:
        raise HTTPException(status_code=404, detail="Chat history not found.")
    