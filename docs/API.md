# DerDieDas.ai API 문서

FastAPI 기반 백엔드 API

## 서버 실행

```bash
# 개발 모드 (자동 리로드)
python run_api.py

# 또는 직접 uvicorn 실행
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

서버 주소: `http://localhost:8000`

API 문서 (Swagger UI): `http://localhost:8000/docs`

## 엔드포인트

### 시스템

#### GET `/`
API 상태 확인

**Response:**
```json
{
  "status": "online",
  "message": "DerDieDas.ai API is running",
  "version": "1.0.0"
}
```

#### GET `/health`
헬스 체크

---

### 프로필 관리

#### GET `/api/profile`
사용자 프로필 조회

**Response:**
```json
{
  "nickname": "학습자",
  "level": "B1-중반",
  "total_stamps": 15,
  "interests": ["여행", "음악", "IT"],
  "goals": ["회화", "문법"],
  "skill_proficiency": {
    "G.ART.DEF.NOM": 75.5,
    "G.VERB.PRES.REG": 60.0
  },
  "skill_learning_count": {
    "G.ART.DEF.NOM": 3,
    "G.VERB.PRES.REG": 2
  }
}
```

#### POST `/api/profile/update-level`
레벨 테스트 결과 업데이트

**Parameters:**
- `level` (str): 레벨 (예: "B1-중반")
- `skill_proficiency` (dict, optional): 스킬별 숙련도

**Response:**
```json
{
  "success": true,
  "level": "B1-중반"
}
```

---

### 노트북 관리

#### GET `/api/notebooks`
모든 노트북 조회

**Response:**
```json
[
  {
    "id": "nb_G.ART.DEF.NOM",
    "title": "Definite article – nominative",
    "category": "Grammar",
    "topic": "Articles",
    "total_sessions": 3,
    "last_studied": "10/21",
    "is_recommended": false,
    "skill_id": "G.ART.DEF.NOM"
  }
]
```

#### GET `/api/notebooks/recommended`
추천 노트북만 조회

**Response:**
```json
[
  {
    "id": "nb_rec_G.ART.DEF.ACC",
    "title": "Definite article – accusative",
    "is_recommended": true,
    ...
  }
]
```

#### POST `/api/notebooks/refresh-recommended`
추천 노트북 갱신 (숙련도 업데이트 후 호출)

**Response:**
```json
{
  "success": true,
  "message": "Recommended notebooks refreshed"
}
```

---

### 학습 컨텐츠 생성

#### POST `/api/learning/select-topic`
적응형 주제 선정 (숙련도 기반)

**Request Body:**
```json
{
  "user_proficiency": {
    "G.ART.DEF.NOM": 25.0,
    "G.VERB.PRES.REG": 65.0
  },
  "learning_count": {
    "G.ART.DEF.NOM": 0,
    "G.VERB.PRES.REG": 2
  },
  "domain_filter": "Grammar"
}
```

**Response:**
```json
{
  "skill_id": "G.ART.DEF.NOM",
  "skill_info": {
    "name": "Definite article – nominative",
    "area": "Articles",
    "cefr": "A1",
    "hint": "Der/Die/Das + 주어"
  }
}
```

#### POST `/api/learning/generate-content`
학습 컨텐츠 생성 (GPT 호출)

**Request Body:**
```json
{
  "skill_id": "G.ART.DEF.NOM",
  "skill_name": "Definite article – nominative",
  "skill_description": "정관사 주격 변화",
  "user_cefr_level": "A2",
  "user_interests": ["여행", "음악"],
  "user_goals": ["회화"]
}
```

**Response:**
```json
{
  "concept_de": "독일어 개념 설명...",
  "concept_ko": "한국어 개념 설명...",
  "examples": [
    {
      "de": "Der Mann geht zur Schule.",
      "ko": "그 남자는 학교에 간다."
    }
  ],
  "quiz_questions": [
    {
      "id": "q1",
      "type": "fill_blank",
      "question": "__ Katze schläft.",
      "correct_answer": "Die",
      "hint": "명사의 성을 확인하세요",
      "explanation": "'Katze'는 여성 명사이므로..."
    }
  ],
  "writing_task": {
    "prompt_de": "Schreibe 3 Sätze...",
    "prompt_ko": "3문장을 쓰세요...",
    "min_sentences": 3,
    "target_grammar": "Definite article – nominative"
  }
}
```

#### POST `/api/learning/writing-feedback`
작문 피드백 생성 (GPT 호출)

**Request Body:**
```json
{
  "user_text": "Der Mann geht zur Schule. Die Frau kocht das Essen.",
  "task_prompt": "일상에 대해 3문장을 쓰세요",
  "target_grammar": "Definite article – nominative",
  "user_cefr_level": "A2"
}
```

**Response:**
```json
{
  "grammar_score": 4,
  "vocabulary_score": 4,
  "task_completion_score": 5,
  "corrections": [
    {
      "original": "...",
      "corrected": "...",
      "explanation": "...",
      "error_type": "grammar"
    }
  ],
  "positive_feedback": [
    "정관사를 정확하게 사용했어요!"
  ],
  "improvement_tips": [
    "더 다양한 어휘를 사용해보세요"
  ],
  "skill_proficiency_change": 6.5
}
```

#### POST `/api/learning/complete`
학습 완료 처리 (통합 업데이트)

**Request Body:**
```json
{
  "notebook_id": "nb_G.ART.DEF.NOM",
  "skill_proficiency": {
    "G.ART.DEF.NOM": 82.5
  },
  "learning_count_increment": "G.ART.DEF.NOM",
  "stamps_increment": 1
}
```

**Response:**
```json
{
  "success": true,
  "message": "Learning completed successfully",
  "updated_stamps": 16
}
```

**처리 내용:**
- 스킬 숙련도 업데이트
- 학습 횟수 증가
- 스탬프 증가
- 노트북 세션 업데이트 (total_sessions, last_studied)
- 추천 노트북 갱신

---

## 에러 응답

모든 에러는 다음 형식으로 반환됩니다:

```json
{
  "detail": "Error message here"
}
```

**HTTP 상태 코드:**
- `200`: 성공
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류

---

## 사용 예시

### Python (requests)

```python
import requests

# API 기본 URL
BASE_URL = "http://localhost:8000"

# 프로필 조회
response = requests.get(f"{BASE_URL}/api/profile")
profile = response.json()
print(profile)

# 학습 컨텐츠 생성
content_request = {
    "skill_id": "G.ART.DEF.NOM",
    "skill_name": "Definite article – nominative",
    "skill_description": "정관사 주격",
    "user_cefr_level": "A2",
    "user_interests": ["여행", "음악"],
    "user_goals": ["회화"]
}

response = requests.post(
    f"{BASE_URL}/api/learning/generate-content",
    json=content_request
)
content = response.json()
print(content["quiz_questions"])
```

### cURL

```bash
# 프로필 조회
curl http://localhost:8000/api/profile

# 추천 노트북 갱신
curl -X POST http://localhost:8000/api/notebooks/refresh-recommended

# 학습 완료 처리
curl -X POST http://localhost:8000/api/learning/complete \
  -H "Content-Type: application/json" \
  -d '{
    "notebook_id": "nb_G.ART.DEF.NOM",
    "skill_proficiency": {"G.ART.DEF.NOM": 82.5},
    "learning_count_increment": "G.ART.DEF.NOM",
    "stamps_increment": 1
  }'
```

---

## 개발 노트

### 기존 Streamlit에서 분리된 로직

다음 기능들이 API로 분리되었습니다:

1. **TopicSelector** → `/api/learning/select-topic`
2. **LearningContentGenerator** → `/api/learning/generate-content`
3. **WritingFeedbackGenerator** → `/api/learning/writing-feedback`
4. **ProfileManager** → `/api/profile/*`, `/api/notebooks/*`

### Streamlit에서 API 호출 방법

```python
import requests

# Streamlit 페이지에서
API_URL = "http://localhost:8000"

# 기존: 직접 호출
# generator = LearningContentGenerator()
# content = generator.generate_content(...)

# 변경: API 호출
response = requests.post(
    f"{API_URL}/api/learning/generate-content",
    json={...}
)
content = response.json()
```

### 장점

1. **관심사 분리**: 비즈니스 로직과 UI 분리
2. **재사용성**: 다른 클라이언트(모바일 앱 등)에서도 사용 가능
3. **확장성**: 독립적으로 스케일 가능
4. **테스트**: API 단위 테스트 용이
5. **성능**: 캐싱, 로드 밸런싱 등 최적화 가능
