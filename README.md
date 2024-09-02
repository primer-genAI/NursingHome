# 요양병원 AI

## 1. Preprocessing

### 1) 의무기록지
1. OCR : UpstageLayoutAnalysisLoader (`pdf to json`)
    - 의무기록지의 다양한 문서 형태를 잘 이해할 수 있음
    - 다만 내부의 값들이 html 문서 형식으로 작성되어 있어서 다시 형태 변환이 필요하다 판단
2. 형태 변환 (`json to txt`)
    - 좀 더 이해하기 쉬운 text 형태로 변환
        'results/{환자번호}/{페이지쪽수}.txt' 이런식으로 페이지를 나눠서 txt파일에 저장했다.

+ 추가적으로 2에서 json -> markdown txt로 변환하여 더 좋은 성능을 보였다

### 2) 식단표
- 모델이 이해하기 쉬운 형태로 변형하였다 (`xls to txt`)


### 3) 환자군 별 청구액 및 간병비
1. OCR : UpstageLayoutAnalysisLoader (`pdf to json`)
2. json 안에 있는 html 형식의 값들을 모두 markdown 형식으로 변환


## 2. Chunking
## 3. RAG

### Router 방식 이용
1. 질문이 어떤 내용인지 분류를 수행하는 chain
    - `환자정보`, `메뉴`, 또는 `병원비` 중 어떤 것에 대한 물음인지 확인

2. 대답 생성
    - `환자정보` :  의무기록지를 context로 사용
    - `메뉴` : 식단표를 context로 사용
    - `병원비` : 환자군별청구액및간병비 데이터를 바탕으로 병원비를 계산해줌

## 실행 방법

```bash
# make and activate venv
python3 -m venv .venv
. .venv/bin/activate

# install package
pip install -r requirements.txt

# Move directory and setting credential
cd models
cat > .env
# make .env for set Upstage API (models 폴더 내에 생성 해야 작동)
UPSTAGE_API_KEY='Your issued API key'

# Execute
uvicorn main:app --reload
```
