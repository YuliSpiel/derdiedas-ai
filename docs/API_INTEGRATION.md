# API Integration Guide

DerDieDas.ai 프론트엔드-백엔드 통합 가이드

## 아키텍처

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Streamlit UI   │ ──────> │ Learning Service │ ──────> │ FastAPI Backend │
│  (Frontend)     │ <────── │  (Service Layer) │ <────── │   (Backend)     │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │
                                     │ Fallback
                                     ↓
                            ┌──────────────────┐
                            │ Direct Functions │
                            │  (Local Calls)   │
                            └──────────────────┘
```

## 핵심 컴포넌트

### 1. FastAPI Backend (`src/api/main.py`)

**실행 방법:**
```bash
python run_api.py
# 또는
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**엔드포인트:**
- 프로필: `/api/profile`, `/api/profile/update-level`
- 노트북: `/api/notebooks`, `/api/notebooks/recommended`, `/api/notebooks/refresh-recommended`
- 학습: `/api/learning/select-topic`, `/api/learning/generate-content`, `/api/learning/writing-feedback`, `/api/learning/complete`

### 2. API Client (`src/utils/api_client.py`)

HTTP 통신 래퍼:
```python
from src.utils.api_client import get_api_client

client = get_api_client()
profile = client.get_profile()
```

**특징:**
- 자동 에러 핸들링
- JSON 직렬화/역직렬화
- 싱글톤 패턴

### 3. Learning Service (`src/services/learning_service.py`)

**API 우선 + 폴백 전략:**

```python
from src.services.learning_service import get_learning_service

service = get_learning_service()
# API 서버 실행 중 → API 호출
# API 서버 없음 → 직접 함수 호출
```

**장점:**
- ✅ API 서버 실행 여부와 무관하게 작동
- ✅ 개발 중 API 서버 없어도 테스트 가능
- ✅ 프로덕션 배포 시 API로 자동 전환

## Streamlit 페이지 통합

### Before (직접 호출)
```python
from learning.content_generator import LearningContentGenerator

generator = LearningContentGenerator()
content = generator.generate_content(
    skill_id="G.ART.DEF.NOM",
    skill_name="Definite article – nominative",
    skill_description="정관사 주격",
    user_cefr_level="A2",
    user_interests=["여행"],
    user_goals=["회화"]
)
```

### After (서비스 레이어)
```python
from services.learning_service import get_learning_service

service = get_learning_service()
content = service.generate_content(
    skill_id="G.ART.DEF.NOM",
    skill_name="Definite article – nominative",
    skill_description="정관사 주격",
    user_cefr_level="A2",
    user_interests=["여행"],
    user_goals=["회화"]
)
```

**동작:**
1. API 서버 실행 중이면 → `POST /api/learning/generate-content` 호출
2. API 서버 없으면 → `LearningContentGenerator.generate_content()` 직접 호출
3. API 에러 발생 시 → 자동으로 직접 호출로 폴백

## 통합된 페이지

### ✅ pages/learning_session.py
- **컨텐츠 생성**: `service.generate_content()`
- **작문 피드백**: `service.generate_writing_feedback()`
- **학습 완료**: `service.complete_learning()`

### ✅ pages/dashboard.py
- 서비스 레이어 임포트 완료 (읽기 전용 페이지는 직접 호출 유지)

### ⏭️ pages/level_test.py
- 레벨 테스트는 독립적으로 작동 (API 통합 불필요)

## 배포 시나리오

### 1. 로컬 개발 (API 서버 없음)
```bash
streamlit run app.py
# → 자동으로 직접 함수 호출 사용
```

### 2. 로컬 개발 (API 서버 있음)
```bash
# 터미널 1
python run_api.py

# 터미널 2
streamlit run app.py
# → 자동으로 API 호출 사용
```

### 3. 프로덕션 배포
```bash
# Docker Compose 예시
services:
  api:
    command: python run_api.py
    ports:
      - "8000:8000"

  frontend:
    command: streamlit run app.py
    environment:
      - API_BASE_URL=http://api:8000
```

## 환경 변수

### `.env` 파일 (선택사항)
```bash
# API 서버 주소 (기본값: http://localhost:8000)
API_BASE_URL=http://localhost:8000

# OpenAI API 키
OPENAI_API_KEY=sk-...
```

### 환경 변수 우선순위
1. 환경 변수 `API_BASE_URL`
2. 기본값 `http://localhost:8000`

## 테스트

### API 서버 테스트
```bash
# 서버 실행
python run_api.py

# 헬스 체크
curl http://localhost:8000/health

# 프로필 조회
curl http://localhost:8000/api/profile

# API 문서
open http://localhost:8000/docs
```

### API 클라이언트 테스트
```bash
python src/utils/api_client.py
# 출력:
# === API 서버 테스트 ===
# 1. 헬스 체크:
# ✅ 서버 실행 중
# ...
```

### 서비스 레이어 테스트
```bash
python -m src.services.learning_service
# 출력:
# === 학습 서비스 테스트 ===
# API 사용 가능: True
# ...
```

## 트러블슈팅

### 1. API 서버 연결 실패
**증상:**
```
⚠️ API 서버가 실행 중이 아닙니다. 직접 호출 모드로 전환합니다.
```

**해결:**
- API 서버가 실행 중인지 확인: `curl http://localhost:8000/health`
- API 서버 재시작: `python run_api.py`
- 포트 충돌 확인: `lsof -i :8000`

### 2. 모듈 임포트 에러
**증상:**
```
ModuleNotFoundError: No module named 'src'
```

**해결:**
```bash
# Python path 확인
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 또는 모듈 실행
python -m src.services.learning_service
```

### 3. CORS 에러 (브라우저)
**증상:**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:8501' has been blocked by CORS policy
```

**해결:**
- FastAPI의 CORS 설정 확인 (`src/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## API vs 직접 호출 비교

| 항목 | API 방식 | 직접 호출 방식 |
|------|----------|----------------|
| **성능** | 네트워크 오버헤드 있음 | 빠름 (로컬 호출) |
| **확장성** | 독립 스케일링 가능 | Streamlit과 함께 스케일 |
| **캐싱** | API 레벨 캐싱 가능 | 프로세스 내 캐싱만 가능 |
| **모니터링** | API 로그 분리 가능 | Streamlit 로그와 혼재 |
| **재사용성** | 다른 클라이언트 사용 가능 (모바일 앱 등) | Streamlit 전용 |
| **개발** | API + 프론트 분리 개발 | 빠른 프로토타이핑 |

## 권장 사항

### 개발 단계
- ✅ 직접 호출 방식으로 빠른 개발
- ✅ 필요시 API 서버 실행하여 테스트
- ✅ 서비스 레이어를 통한 자동 폴백

### 프로덕션 배포
- ✅ API 서버 필수 실행
- ✅ API 모니터링 및 로깅 설정
- ✅ API 캐싱 전략 (Redis 등)
- ✅ CORS 정책 엄격하게 설정

## 다음 단계

1. **프로필 관리 API 통합** (선택사항)
   - 프로필 업데이트도 API로 처리
   - 현재는 읽기만 API, 쓰기는 직접 호출

2. **레벨 테스트 API 통합** (선택사항)
   - 레벨 테스트 결과 저장 API화
   - 현재는 독립적으로 작동

3. **캐싱 레이어 추가**
   - GPT 응답 캐싱 (동일 요청 재사용)
   - Redis 또는 메모리 캐시

4. **모니터링 추가**
   - API 응답 시간 로깅
   - 에러율 모니터링
   - 사용량 통계

## 관련 문서

- [API.md](./API.md) - FastAPI 엔드포인트 상세 문서
- [README.md](../README.md) - 프로젝트 전체 가이드
- [LEVEL_TEST_LOGIC.md](./LEVEL_TEST_LOGIC.md) - 레벨 테스트 로직
