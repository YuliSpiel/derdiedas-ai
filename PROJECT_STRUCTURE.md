# DerDieDas.ai 프로젝트 구조

## 디렉토리 구조

```
derdiedas-ai.ai/
│
├── src/                          # 소스 코드
│   ├── __init__.py
│   │
│   ├── level_test/              # 레벨 테스트 모듈
│   │   ├── __init__.py
│   │   ├── CEFR_Eval.py        # 평가 엔진 (코사인 유사도 + AI 피드백)
│   │   └── level_test_app.py   # Streamlit 웹 UI
│   │
│   └── utils/                   # 유틸리티 모듈
│       ├── __init__.py
│       ├── parse_pipeline.py   # 파싱 유틸리티
│       └── utils_io_and_stats.py  # I/O 및 통계 유틸리티
│
├── notebooks/                   # Jupyter 노트북
│   └── lang_eval.ipynb         # 언어 평가 실험
│
├── docs/                        # 문서
│   └── README_LEVEL_TEST.md    # 레벨 테스트 상세 문서
│
├── config/                      # 설정 파일
│   └── .env                     # 환경 변수 (API 키 등, gitignored)
│
├── models_cache/                # 모델 캐시 (gitignored)
│   ├── hub/                     # Hugging Face 모델 캐시
│   └── datasets/                # 데이터셋 캐시
│
├── outputs/                     # 출력 파일 (gitignored)
│
├── dddvenv/                     # Python 가상환경 (gitignored)
│
├── run_level_test.py           # 레벨 테스트 실행 스크립트
├── requirements.txt            # Python 의존성
├── README.md                   # 프로젝트 메인 README
├── PROJECT_STRUCTURE.md        # 이 파일
├── .gitignore                  # Git 제외 파일
└── .gitattributes              # Git 속성

```

## 주요 파일 설명

### 소스 코드 (`src/`)

#### `src/level_test/`
독일어 레벨 테스트 시스템의 핵심 모듈

**CEFR_Eval.py** (1,000+ 줄)
- `CEFRLevel`, `SubLevel`: 레벨 정의 enum
- `Question`: 질문 데이터 클래스
- `UserResponse`: 사용자 답변 데이터 클래스
- `DetailedFeedback`: AI 피드백 데이터 클래스
- `CEFRCorpusLoader`: MERLIN 독일어 코퍼스 로더
- `LevelEstimator`: 코사인 유사도 기반 레벨 추정
- `AdaptiveQuestionSelector`: 적응형 질문 선택 알고리즘
- `AIFeedbackGenerator`: GPT-4o mini 기반 AI 피드백 생성
- `FinalLevelAssessor`: 최종 레벨 판정
- `LevelTestSession`: 전체 세션 관리

**level_test_app.py** (~450 줄)
- Streamlit 기반 웹 UI
- `show_welcome_screen()`: 시작 화면
- `show_test_screen()`: 테스트 진행 화면
- `show_result_screen()`: 결과 화면
- `show_ai_feedback()`: AI 피드백 표시
- `get_recommendations()`: 레벨별 학습 추천

#### `src/utils/`
범용 유틸리티 함수

**parse_pipeline.py**
- 텍스트 파싱 및 처리 유틸리티

**utils_io_and_stats.py**
- 파일 I/O 및 통계 계산 유틸리티

### 실행 스크립트

**run_level_test.py**
- 프로젝트 루트에서 레벨 테스트를 실행하는 래퍼 스크립트
- Python path 설정 및 Streamlit 실행

### 설정 파일

**requirements.txt**
- Python 패키지 의존성 목록
- streamlit, sentence-transformers, openai 등

**config/.env**
- 환경 변수 (API 키 등)
- Git에서 제외됨

**.gitignore**
- 가상환경, 캐시, 환경 변수 파일 등 Git 제외

## 데이터 흐름

```
사용자
  ↓
level_test_app.py (Streamlit UI)
  ↓
LevelTestSession
  ↓
├─→ CEFRCorpusLoader → MERLIN 코퍼스 로드
│
├─→ LevelEstimator → 코사인 유사도 계산
│
├─→ AdaptiveQuestionSelector → 다음 질문 선택
│
└─→ AIFeedbackGenerator → GPT-4o mini 피드백
      ↓
최종 결과 (레벨 + AI 피드백)
```

## 모듈 임포트 구조

```python
# level_test_app.py에서
from CEFR_Eval import LevelTestSession, CEFRLevel

# 외부에서 임포트 시
from src.level_test import LevelTestSession, CEFRLevel
```

## 캐시 구조

### models_cache/
Hugging Face에서 다운로드한 모델 및 데이터셋 캐시

```
models_cache/
├── hub/
│   ├── models--sentence-transformers--paraphrase-multilingual-mpnet-base-v2/
│   └── datasets--UniversalCEFR--merlin_de/
└── datasets/
    └── UniversalCEFR___merlin_de/
```

## 개발 환경 설정

### 1. 가상환경 생성
```bash
python -m venv dddvenv
source dddvenv/bin/activate  # Windows: dddvenv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정
```bash
echo "OPENAI_API_KEY=your-key" > config/.env
```

### 4. 실행
```bash
streamlit run run_level_test.py
```

## 추가 예정 모듈

```
src/
├── chatbot/           # 회화 연습 챗봇
├── grammar/           # 문법 학습 모듈
├── notebook/          # 학습 노트북 관리
└── tracking/          # 진도 추적
```
