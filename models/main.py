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

from rag_patient import patient_chain

from operator import itemgetter
from langchain_core.runnables import RunnableLambda

# Define a request model for FastAPI
class QueryRequest(BaseModel):
    question: str
    patient_id: str

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

from TEMPLATES.rag_template import *


@app.post("/n1") # 친절
async def ask_patient(request: QueryRequest):
    try:
        # 요청으로부터 patient_chain 생성
        chain = patient_chain(request.patient_id, prompt_n1)

        # 질문 실행 및 결과 반환
        result = chain.invoke(
            {
                "question": request.question
            }
        )

        # JSON 응답으로 결과 반환
        return JSONResponse(
            content={"response": result.replace(r'[','').replace(r']','')},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        # 에러 처리
        raise HTTPException(status_code=500, detail=str(e))

# FastAPI 엔드포인트 생성
@app.post("/n2") # 간단
async def ask_patient(request: QueryRequest):
    try:
        # 요청으로부터 patient_chain 생성
        chain = patient_chain(request.patient_id, prompt_n2)

        # 질문 실행 및 결과 반환
        result = chain.invoke(
            {
                "question": request.question
            }
        )

        # JSON 응답으로 결과 반환
        return JSONResponse(
            content={"response": result},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        # 에러 처리
        raise HTTPException(status_code=500, detail=str(e))
    

# 요청 모델 정의
class QueryRequest(BaseModel):
    question: str
    session_id: str
    patient_id: str  # patient_id 필드 추가

# 응답 모델 정의
class QueryResponse(BaseModel):
    response: str

from rag_patient_history import create_rag_with_history
# FastAPI 엔드포인트 생성
@app.post("/chat")
async def chat_with_history(request: QueryRequest):
    try:
        rag_with_history = create_rag_with_history(request.patient_id)

        # 질문과 세션 ID를 사용해 체인을 실행
        result = rag_with_history.invoke(
            {
                "question": request.question,
            },
            config={
                "configurable": {
                    "session_id": request.session_id,
                }
            },
        )

        # JSON 응답으로 결과를 반환
        return JSONResponse(
            content={"response": result},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        # 에러 처리
        raise HTTPException(status_code=500, detail=str(e))