# 독일어 레벨 테스트 시스템

DerDieDas.ai의 CEFR 기반 적응형 독일어 레벨 테스트 시스템입니다.

## 주요 기능

### 1. 작문 기반 평가
- 5개의 작문 과제를 통한 종합적인 언어 능력 평가
- 각 답변은 2-3문장으로 작성
- 실제 언어 사용 능력을 측정

### 2. 적응형 질문 선택
- 첫 질문: 모든 사용자 공통 (A2-1: "Wie heißt du, und woher kommst du?")
- 이후 질문: 이전 답변의 수준에 따라 난이도 조정
- A2 → B1 → B2 → C1 레벨 문항 뱅크에서 선택

### 3. CEFR 코퍼스 기반 레벨 추정
- MERLIN 독일어 코퍼스 활용
- 문장 임베딩을 통한 유사도 비교
- 각 레벨(A2, B1, B2, C1)별 코퍼스와의 매칭

### 4. 세부 레벨 판정
- 메인 레벨: A2, B1, B2, C1
- 서브 레벨: 초반, 중반, 후반
- 최종 결과: "B1-중반", "B2-후반" 등

### 5. AI 기반 상세 피드백 (GPT-4o mini)
- 5개의 질문-답변을 종합 분석
- 5가지 평가 기준별 0-5점 점수 및 상세 코멘트
  - 문법 정확도 (관사, 격, 동사 어순 등)
  - 구문 복잡도 (종속절, 접속사 등)
  - 어휘 범위 (추상어, 동의어 등)
  - 유창성/응집성 (담화 표지, 논리적 흐름)
  - 과제 적합성 (질문 의도 충족도)
- 강점 및 개선점 제시

## 시스템 구조

### [CEFR_Eval.py](../src/level_test/CEFR_Eval.py)

핵심 평가 로직을 담당하는 백엔드 모듈입니다.

#### 주요 클래스:

1. **CEFRCorpusLoader**
   - MERLIN 독일어 코퍼스 로드
   - 문장 임베딩 모델 초기화
   - 레벨별 코퍼스 임베딩 생성

2. **LevelEstimator**
   - 사용자 답변 임베딩 생성
   - 코퍼스와의 코사인 유사도 계산
   - 레벨 및 서브레벨 추정

3. **AdaptiveQuestionSelector**
   - 이전 답변 분석
   - 적응형 질문 선택 알고리즘
   - 질문 중복 방지

4. **FinalLevelAssessor**
   - 5개 답변 종합 분석
   - 최종 레벨 판정
   - 상세 분석 리포트 생성

5. **AIFeedbackGenerator**
   - GPT-4o mini API 통합
   - 5개 답변 종합 분석
   - 5가지 기준별 상세 피드백 생성
   - JSON 구조화된 응답 파싱

6. **LevelTestSession**
   - 전체 테스트 세션 관리
   - 상태 관리 (진행 중/완료)
   - 답변 히스토리 추적
   - AI 피드백 생성 통합

### [level_test_app.py](../src/level_test/level_test_app.py)

Streamlit 기반 프론트엔드 웹 앱입니다.

#### 주요 화면:

1. **시작 화면** (`show_welcome_screen`)
   - 테스트 안내
   - 평가 기준 설명
   - 테스트 시작 버튼

2. **테스트 진행 화면** (`show_test_screen`)
   - 진행률 표시 (1/5 ~ 5/5)
   - 현재 질문 표시
   - 답변 입력 텍스트 영역
   - 이전 답변 히스토리

3. **결과 화면** (`show_result_screen`)
   - 최종 레벨 표시
   - 레벨별 설명
   - 상세 분석 (레벨 분포, 신뢰도 등)
   - AI 피드백 (5가지 평가 기준, 강점/개선점)
   - 맞춤 학습 추천

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. OpenAI API 키 설정 (선택사항)

AI 피드백 기능을 사용하려면 OpenAI API 키가 필요합니다:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

또는 `.env` 파일에 추가:
```
OPENAI_API_KEY=your-api-key-here
```

**참고:** API 키가 없어도 코사인 유사도 기반 레벨 판정은 정상 작동합니다. AI 피드백만 비활성화됩니다.

### 3. 앱 실행

프로젝트 루트에서:

```bash
streamlit run run_level_test.py
```

또는 직접 실행:

```bash
streamlit run src/level_test/level_test_app.py
```

앱이 실행되면 브라우저가 자동으로 열립니다 (기본: http://localhost:8501)

## 질문 뱅크 구조

### A2 레벨 (기초 회화, 단문 중심)
- A2-1: 자기소개 - "Wie heißt du, und woher kommst du?"
- A2-2: 일상/취미 - "Was machst du gern in deiner Freizeit?"
- A2-3: 가족/친구 - "Erzähl mir etwas über deine Familie oder deine Freunde."
- A2-4: 일상 루틴 - "Wie sieht ein normaler Tag bei dir aus?"
- A2-5: 음식/날씨 - "Was isst du am liebsten, wenn es kalt ist?"

### B1 레벨 (경험·감정·이유 설명)
- B1-1: 학습 어려움 - "Was findest du schwierig beim Deutschlernen? Warum?"
- B1-2: 여행 경험 - "Erzähl mir von einer schönen Reise, die du gemacht hast."
- B1-3: 취미 이유 - "Warum ist dein Hobby wichtig für dich?"
- B1-4: 인간관계 - "Wie beschreibst du eine gute Freundschaft?"
- B1-5: 생활환경 - "Was gefällt dir an deiner Stadt, und was nicht?"

### B2 레벨 (의견·가치·논리적 전개)
- B2-1: 미래 계획 - "Wie stellst du dir dein Leben in fünf Jahren vor?"
- B2-2: 사회적 주제 - "Findest du, dass Technologie unser Leben besser oder schlechter macht?"
- B2-3: 문화/예술 - "Welche Rolle spielt Musik oder Kunst in deinem Leben?"
- B2-4: 학습 전략 - "Was machst du, wenn du etwas Neues lernen möchtest?"
- B2-5: 일·진로 - "Welche Arbeit würdest du gern machen, und warum?"

### C1 레벨 (추상적·비판적 사고 중심)
- C1-1: 사회 문제 - "Manche sagen, dass soziale Medien die Gesellschaft verändern. Was denkst du darüber?"
- C1-2: 문화 비교 - "Wie unterscheiden sich deiner Meinung nach die koreanische und die deutsche Kultur?"
- C1-3: 가정/추론 - "Wenn du die Möglichkeit hättest, überall zu leben, wo würdest du wohnen – und warum?"
- C1-4: 인생 철학 - "Was bedeutet "Glück" für dich persönlich?"
- C1-5: 비판적 평가 - "Findest du, dass Erfolg wichtiger als Zufriedenheit ist?"

## 평가 알고리즘

### 1. 단일 답변 평가
```python
user_text → 임베딩 생성 → 각 레벨 코퍼스와 유사도 계산 → 최고 유사도 레벨 선택 → 서브레벨 판정
```

### 2. 적응형 질문 선택
```python
첫 질문: A2-1 (고정)
두 번째 질문:
  - 첫 답변이 A2 수준 → B1 문항 선택
  - 첫 답변이 B1 수준 → B1 문항 선택
  - 첫 답변이 B2+ 수준 → B2 문항 선택

세 번째 질문 이후:
  - 평균 레벨 < 2.0 → B1 문항
  - 평균 레벨 < 3.0 → B2 문항
  - 평균 레벨 ≥ 3.0 → C1 문항
```

### 3. 최종 레벨 판정
```python
5개 답변의 평균 레벨 값 계산
평균 < 1.5 → A2
평균 < 2.5 → B1
평균 < 3.5 → B2
평균 ≥ 3.5 → C1

서브레벨:
소수점 < 0.33 → 초반
소수점 < 0.67 → 중반
소수점 ≥ 0.67 → 후반
```

## 기술 스택

- **프론트엔드**: Streamlit
- **백엔드 로직**: Python 3.11+
- **NLP 모델**: Sentence Transformers (paraphrase-multilingual-mpnet-base-v2)
- **코퍼스**: MERLIN 독일어 데이터셋 (UniversalCEFR/merlin_de)
- **임베딩**: 다국어 MPNET 모델
- **유사도 계산**: 코사인 유사도

## 데이터 흐름

```
사용자 → Streamlit UI → LevelTestSession
                            ↓
                    CEFRCorpusLoader (초기화)
                            ↓
                    질문 제시 ← AdaptiveQuestionSelector
                            ↓
                    답변 제출
                            ↓
                    LevelEstimator (레벨 추정)
                            ↓
                    UserResponse 저장
                            ↓
                    [5회 반복]
                            ↓
                    FinalLevelAssessor (최종 판정)
                            ↓
                    결과 표시
```

## 캐시 관리

모델과 데이터셋은 `./models_cache` 디렉토리에 저장됩니다:
- Sentence Transformer 모델
- MERLIN 독일어 코퍼스
- 생성된 임베딩 (메모리 캐시)

## 성능 최적화

1. **코퍼스 샘플링**: 각 레벨당 최대 500개 문장 사용
2. **상위 10% 유사도**: 가장 유사한 상위 10% 문장의 평균으로 레벨 판정
3. **세션 상태 관리**: Streamlit 세션 스테이트로 재로딩 방지

## 향후 개선 사항

- [ ] 문법 오류 자동 감지 및 피드백
- [ ] 어휘 다양성 분석
- [ ] 발음 평가 (음성 입력)
- [ ] 상세한 피드백 리포트
- [ ] 레벨별 학습 자료 추천
- [ ] 테스트 결과 저장 및 진행 추적

## 라이센스

이 프로젝트는 DerDieDas.ai의 일부입니다.
