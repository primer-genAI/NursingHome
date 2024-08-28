# 요양병원 AI


## 1. Preprocessing

### 1) 의무기록지
1. OCR : UpstageLayoutAnalysisLoader (`pdf to json`)
    - 의무기록지의 다양한 문서 형태를 잘 이해할 수 있음
    - 다만 내부의 값들이 html 문서 형식으로 작성되어 있어서 다시 형태 변환이 필요하다 판단
2. 형태 변환 (`json to txt`)
    - 좀 더 이해하기 쉬운 text 형태로 변환
        'results/{환자번호}/{페이지쪽수}.txt' 이런식으로 페이지를 나눠서 txt파일에 저장했다.

### 2) 식단표
- 모델이 이해하기 쉬운 형태로 변형하였다 (`xls to txt`)


### 3) 환자군 별 청구액 및 간병비
1. OCR : UpstageLayoutAnalysisLoader (`pdf to json`)
2. json 안에 있는 html 형식의 값들을 모두 markdown 형식으로 변환


## 2. Chunking
## 3. RAG

## 실행 방법

```bash
uvicorn main:app --reload
```