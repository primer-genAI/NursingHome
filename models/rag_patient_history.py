import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from langchain_upstage import ChatUpstage, UpstageEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.vectorstores import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from operator import itemgetter

# FastAPI 앱 초기화
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드를 허용
    allow_headers=["*"],  # 모든 헤더를 허용
)

# Embeddings 설정
embeddings = UpstageEmbeddings(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    model="solar-embedding-1-large"
)

# 세션 기록을 저장할 딕셔너리
store = {}

# 세션 ID를 기반으로 세션 기록을 가져오는 함수
def get_session_history(session_ids):
    print(f"[대화 세션ID]: {session_ids}")
    if session_ids not in store:  # 세션 ID가 store에 없는 경우
        # 새로운 ChatMessageHistory 객체를 생성하여 store에 저장
        store[session_ids] = ChatMessageHistory()
    return store[session_ids]  # 해당 세션 ID에 대한 세션 기록 반환

# 프롬프트 템플릿 정의
template = """You are a compassionate, articulate physician.
Your goal is to explain medical information in a way that is easy for your patients to understand, avoiding complex medical jargon as much as possible.
Given a medical document, it's your job to explain the key information that the patient or their family asks about in a patient-friendly format. 
When specific details are provided, such as diagnosis codes or medical history, simplify these terms and explain them in a way that is easy to understand.

If you don't know the answer, just say that you don't know.

Don't say what is in the history.

Answer in Korean.

#Previous Chat History:
{chat_history}

#Question: 
{question} 

#Document:
{context}

#Answer:"""

prompt = PromptTemplate.from_template(template)

# 언어 모델(LLM) 생성
llm = ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"))

# RAG 체인 생성
def create_chain(patient_id):
    # 환자별로 Chroma 데이터베이스 생성
    vectordb = Chroma(
        persist_directory=f'.cache/db/{patient_id}',
        embedding_function=embeddings
    )

    retriever = vectordb.as_retriever()

    chain = (
        {
            "context": itemgetter("question") | retriever,
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

# 대화를 기록하는 RAG 체인 생성
def create_rag_with_history(patient_id):
    chain = create_chain(patient_id)
    return RunnableWithMessageHistory(
        chain,
        get_session_history,  # 세션 기록을 가져오는 함수
        input_messages_key="question",  # 사용자의 질문이 템플릿 변수에 들어갈 key
        history_messages_key="chat_history",  # 기록 메시지의 키
    )