# DerDieDas.ai

AI-powered German Learning Assistant Chatbot

An interactive German learning assistant designed to help users improve their German language skills through natural conversation, personalized feedback, and adaptive level testing.

## 프로젝트 구조

```
derdiedas-ai.ai/
├── app.py                       # 메인 진입점 (자동 리다이렉트)
├── pages/                       # Streamlit 멀티페이지
│   ├── dashboard.py             # 대시보드 (메인 홈)
│   └── level_test.py            # 레벨 테스트 페이지
├── src/                         # 소스 코드
│   ├── level_test/              # 레벨 테스트 모듈
│   │   ├── CEFR_Eval.py        # 평가 로직
│   │   └── __init__.py
│   ├── models/                  # 데이터 모델
│   │   ├── user_profile.py     # 사용자 프로필 및 노트북
│   │   └── __init__.py
│   ├── dashboard/               # 대시보드 (원본 소스)
│   └── utils/                   # 유틸리티
├── notebooks/                   # Jupyter 노트북
├── docs/                        # 문서
├── config/                      # 설정 파일
│   └── .env                     # 환경 변수 (API 키 등)
├── data/                        # 사용자 데이터 (gitignore)
├── models_cache/                # 모델 캐시 (gitignore)
├── outputs/                     # 출력 파일 (gitignore)
├── requirements.txt             # Python 의존성
└── README.md                    # 이 파일

```

## 주요 기능

### 1. 대시보드 (Dashboard)
- **사용자 프로필**: 레벨, 스탬프, 연속 학습 일수, 관심사 관리
- **추천 노트북**: AI 기반 맞춤 학습 콘텐츠 추천
- **노트북 관리**: 문법, 표현, 어휘 등 카테고리별 학습 노트북
- **학습 진도 추적**: 총 학습 횟수 및 최근 학습 날짜 표시

### 2. 독일어 레벨 테스트 (CEFR 기반)
- **작문 기반 평가**: 5개의 적응형 작문 과제
- **이중 평가 시스템**:
  - 코사인 유사도 (MERLIN 독일어 코퍼스)
  - GPT-4o mini AI 피드백 (5가지 평가 기준)
- **세부 레벨 판정**: A2~C1 + 초반/중반/후반
- **프로필 연동**: 테스트 결과가 자동으로 프로필에 저장

자세한 내용은 [레벨 테스트 문서](docs/README_LEVEL_TEST.md)를 참고하세요.

## 설치 및 실행

### 1. 가상환경 생성 (권장)

```bash
python -m venv dddvenv
source dddvenv/bin/activate  # Windows: dddvenv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정 (선택사항)

AI 피드백을 사용하려면 OpenAI API 키를 설정하세요:

```bash
# config/.env 파일 생성
echo "OPENAI_API_KEY=your-api-key-here" > config/.env
```

또는 환경 변수로 설정:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 4. 앱 실행

**앱 실행:**
```bash
streamlit run app.py
```

- 최초 접속 시: 자동으로 대시보드로 이동하여 프로필 설정 가능
- 기존 사용자: 바로 대시보드로 이동

사이드바에서 페이지 전환:
- **dashboard** - 프로필 및 노트북 관리 (메인 홈)
- **level_test** - CEFR 기반 독일어 레벨 테스트

## 기술 스택

### Backend
- **Python 3.11+**
- **Sentence Transformers**: 문장 임베딩 (다국어 MPNET)
- **Datasets**: MERLIN 독일어 코퍼스
- **OpenAI GPT-4o mini**: AI 피드백 생성

### Frontend
- **Streamlit**: 웹 UI 프레임워크

### 평가 기준 (AI 피드백)
1. 문법 정확도 (0-5점)
2. 구문 복잡도 (0-5점)
3. 어휘 범위 (0-5점)
4. 유창성/응집성 (0-5점)
5. 과제 적합성 (0-5점)

## 비용

- **코사인 유사도 기반 평가**: 완전 무료 (로컬 모델)
- **AI 피드백**: GPT-4o mini API 호출 (~$0.001-0.002/테스트)

## 데이터 출처 및 인용

본 프로젝트는 다음 오픈 라이센스 데이터를 사용합니다:

### 1. MERLIN 코퍼스 (독일어 레벨 테스트)

독일어 레벨 평가를 위해 MERLIN (Multilingual platform for European Reference Levels: Interlanguage Exploration) 코퍼스의 독일어 학습자 텍스트 데이터를 사용합니다.

- **데이터셋**: MERLIN German Corpus
- **출처**: [UniversalCEFR/merlin_de](https://huggingface.co/datasets/UniversalCEFR/merlin_de)
- **라이센스**: CC BY-SA 4.0

**인용:**
```bibtex
@inproceedings{boyd2014merlin,
  title={The MERLIN corpus: Learner language and the CEFR},
  author={Boyd, Adriane and Hana, Jirka and Nicolas, Lionel and Meurers, Detmar and Wis{\'n}iewski, Katrin and Abel, Andrea and Schöne, Karin and Stindlov{\'a}, Barbora and Vettori, Chiara},
  booktitle={Proceedings of the Ninth International Conference on Language Resources and Evaluation (LREC'14)},
  pages={1281--1288},
  year={2014}
}
```

**참고 문헌:**
Boyd, A., Hana, J., Nicolas, L., Meurers, D., Wisniewski, K., Abel, A., Schöne, K., Stindlová, B., & Vettori, C. (2014). The MERLIN corpus: Learner language and the CEFR. In *Proceedings of the Ninth International Conference on Language Resources and Evaluation (LREC'14)* (pp. 1281-1288).

### 2. Deutsch im Blick (문법 학습 콘텐츠)

독일어 문법 학습을 위한 구조화된 데이터로 활용합니다.

- **출처**: Grammar to Accompany Deutsch im Blick
- **저자**: Zsuzsanna Abrams et al.
- **라이센스**: [CC BY 4.0 International](https://creativecommons.org/licenses/by/4.0/)
- **수정 사항**: 구조화된 데이터셋으로 변환 (CSV/JSON)

**참고 문헌:**
Abrams, Z., et al. *Grammar to Accompany Deutsch im Blick*. Licensed under CC BY 4.0. https://creativecommons.org/licenses/by/4.0/

## 개발 로드맵

- [x] CEFR 기반 레벨 테스트
- [x] 적응형 질문 선택
- [x] AI 상세 피드백
- [x] 대시보드 및 프로필 관리
- [x] 노트북 관리 시스템
- [ ] 학습 사이클 (개념 설명 → 퀴즈 → 작문)
- [ ] 회화 연습 모드
- [ ] 문법 학습 콘텐츠
- [ ] 학습 통계 및 분석

## 라이센스

This project is licensed under the MIT License.

## 기여

기여는 언제나 환영합니다! Issue나 Pull Request를 자유롭게 제출해 주세요.
