import os
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv

# API 키 정보 로드
load_dotenv()

from langchain.prompts.prompt import PromptTemplate

import json
with open("../data/qa.json", "r", encoding='utf-8') as f:
    examples = json.load(f)

# This is a prompt template used to format each individual example.
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{question}"),
        ("ai", "{answer}"),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

prompt = '''
### 시스템 설명 :
당신은 병원 AI 지원 시스템입니다. 
보호자 또는 환자가 의료 상태와 관련된 질문을 하면, 환자의 최신 의료 기록을 기반으로 적절한 답변을 제공해야 합니다. 
답변은 보호자 또는 환자가 이해할 수 있도록 전문용어를 최대한 피하고 쉽게 설명해야 합니다.
환자 혹은 보호자의 질문에 친절하게 답변해주세요

아래에 환자의 의료 기록이 제공됩니다.


### 지시 사항 :
환자의 상태, 식사, 약물 복용, 거동 상태 등을 포함하여 질문에 대한 정확한 답변을 생성하십시오.
참고한 데이터의 메타데이터를 알려주세요

### 중요 사항 :
한글로 답변하세요

### 응답 :
'''

final_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt),
        few_shot_prompt,
        ("human", "{question}"),
    ]
)

from langchain_upstage import ChatUpstage

llm = ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"))

from langchain_core.output_parsers import StrOutputParser

chain = final_prompt | llm | StrOutputParser()