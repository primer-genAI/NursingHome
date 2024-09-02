import bs4
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv

# API 키 정보 로드
load_dotenv()

from langchain.prompts.prompt import PromptTemplate

import json
with open("../data/qa.json", "r", encoding='utf-8') as f:
    data = json.load(f)

example_prompt = PromptTemplate(
    input_variables=["question", "answer",],
    template="\nQuestion: {question}\nAnswer: {answer}",
)


from langchain_community.document_loaders import DirectoryLoader

loader = DirectoryLoader("./results/남A_의무기록지/", glob="*.txt", show_progress=True)
docs = loader.load()

print(f"문서의 수: {len(docs)}")

from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 500,
    chunk_overlap  = 100,
    length_function = len,
)

texts = text_splitter.split_text(docs[0].page_content)

from langchain.text_splitter import RecursiveCharacterTextSplitter

