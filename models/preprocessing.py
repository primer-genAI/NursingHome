import re
import json
import os
from glob import glob
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# .env 파일에서 API 키를 로드합니다.
load_dotenv()

# UPSTAGE_API_KEY = os.getenv('UPSTAGE_API_KEY')
# print(UPSTAGE_API_KEY)
UPSTAGE_API_KEY='up_fc6POq5G3jf4Jl7l3TjWhJJlR4oy1'

client = OpenAI(
    api_key=UPSTAGE_API_KEY,
    base_url="https://api.upstage.ai/v1/solar"
)

from temp.prompts_ocr import system_prompt

# 함수 정의: 위에서 주어진 extract_info를 가져옵니다
def extract_info(data):
    response = client.chat.completions.create(
        model="solar-1-mini-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": data},
        ],
        stream=False,
    )
    result = response.choices[0].message.content
    return result

# 폴더 내 모든 JSON 파일 처리 및 결과를 각각의 페이지별 텍스트 파일에 저장하기
def process_files_in_folder(folder_path, result_folder):
    # 결과 저장 폴더가 없으면 생성합니다.
    os.makedirs(result_folder, exist_ok=True)

    # 폴더 내 모든 파일 확인
    json_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".json")])
    
    for filename in tqdm(json_files, desc="Processing Files", unit="file"):
        json_file_path = os.path.join(folder_path, filename)
        
        # JSON 파일 열기
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        # JSON 파일 이름과 같은 이름의 폴더 생성
        json_base_name = os.path.splitext(filename)[0]
        result_subfolder = os.path.join(result_folder, json_base_name)
        os.makedirs(result_subfolder, exist_ok=True)
        
        # 페이지별 텍스트 변환 및 저장
        for idx, item in enumerate(tqdm(data, desc=f"Processing {filename}", unit="page", leave=False), start=1):
            try:
                text = item.get('text', '')
                if text:
                    transformed_text = extract_info(text)
                    # 페이지별로 텍스트 파일 저장
                    result_file_path = os.path.join(result_subfolder, f"{idx}.txt")
                    with open(result_file_path, 'w', encoding='utf-8') as result_file:
                        result_file.write(transformed_text)
                else:
                    print(f"No 'text' field in item: {item}")
            except Exception as e:
                print(f"Error processing item {idx} in {filename}: {e}")

# 사용 예시: 폴더 경로를 지정하여 실행
folder_path = './ocr'
result_folder = './results'
process_files_in_folder(folder_path, result_folder)
