# 레벨 테스트 로직

## 개요

DerDieDas.ai의 레벨 테스트는 **적응형 질문 선정**과 **GPT 기반 최종 판정**을 결합한 하이브리드 방식입니다.

## 시스템 구조

### 1. 코사인 유사도 (MERLIN Corpus)
**역할**: 다음 질문 난이도 조정용

- **사용 시점**: 각 답변 제출 직후
- **목적**: 다음 질문의 난이도를 동적으로 조정
- **방법**:
  1. 사용자 답변을 임베딩
  2. MERLIN 코퍼스(A2~C1 레이블링된 학습자 작문)와 코사인 유사도 계산
  3. 가장 유사한 코퍼스의 CEFR 레벨 추정
  4. 다음 질문 난이도 결정

**예시**:
```
사용자 답변 → 코사인 유사도 → B1 추정
→ 다음 질문: B1 레벨 질문 출제
```

### 2. GPT-4o mini (최종 판정)
**역할**: 최종 CEFR 레벨 판정

- **사용 시점**: 5개 질문 모두 완료 후
- **목적**: 정확한 레벨 판정 및 상세 피드백
- **평가 기준**:
  1. 문법 정확도 (0-5점)
  2. 구문 복잡도 (0-5점)
  3. 어휘 범위 (0-5점)
  4. 유창성/응집성 (0-5점)
  5. 과제 적합성 (0-5점)

**출력**:
```json
{
  "suggested_cefr_level": "B1",
  "suggested_sub_level": "중반",
  "grammar_accuracy": 3,
  "syntax_complexity": 3,
  ...
}
```

## 전체 흐름

```
1. 첫 질문 (고정)
   "Wie heißt du, und woher kommst du?"
   ↓
2. 답변 제출
   ↓
3. 코사인 유사도로 추정 레벨 계산 (예: A2)
   ↓
4. 다음 질문 난이도 조정 (A2~B1 범위)
   ↓
5. 2-4 반복 (총 5개 질문)
   ↓
6. GPT-4o mini로 종합 분석
   - 5개 답변 전체 검토
   - 5가지 기준 평가
   - CEFR 레벨 판정 (A2~C1)
   - 세부 단계 판정 (초반/중반/후반)
   ↓
7. GPT 판정 결과를 최종 레벨로 사용
   (코사인 유사도 결과는 참고용으로만 출력)
```

## 왜 하이브리드 방식?

### 코사인 유사도의 장점
- ✅ 빠른 응답 (실시간)
- ✅ 추가 비용 없음
- ✅ 적응형 난이도 조정에 적합

### 코사인 유사도의 한계
- ❌ 문법 오류 감지 불가
- ❌ 맥락 이해 부족
- ❌ 단순 단어 유사도 기반

### GPT의 장점
- ✅ 문법 정확도 평가
- ✅ 구문 복잡도 이해
- ✅ 맥락 기반 종합 판단
- ✅ 상세 피드백 제공

### GPT의 한계
- ❌ API 비용 발생
- ❌ 응답 시간 (5-10초)

### 결론
**코사인 유사도로 질문 난이도 조정** + **GPT로 정확한 최종 판정**

## 코드 위치

### 적응형 질문 선정
**파일**: `src/level_test/CEFR_Eval.py`

```python
class LevelEstimator:
    def estimate_level(self, user_text: str):
        # 코사인 유사도 계산
        # → 다음 질문 난이도 조정용
```

### GPT 레벨 판정
**파일**: `src/level_test/CEFR_Eval.py`

```python
class AIFeedbackGenerator:
    def generate_feedback(self, questions, responses):
        # GPT-4o mini 호출
        # → 최종 레벨 판정
```

### 최종 결과 반환
**파일**: `src/level_test/CEFR_Eval.py`

```python
class LevelTestSession:
    def get_final_result(self):
        # 1. GPT 피드백 생성 (레벨 판정 포함)
        # 2. GPT 판정을 최종 레벨로 사용
        # 3. 코사인 유사도는 참고용
```

## 레벨 판정 기준

### A2 (기초)
- 간단한 문장 구조
- 기본 어휘 (일상, 가족, 취미)
- 빈번한 문법 오류
- 예: "Ich heiße Anna. Ich komme aus Korea."

### B1 (중급)
- 복잡한 문장 일부 사용
- 다양한 어휘
- 문법 오류 있으나 의사소통 가능
- 예: "Ich arbeite als Lehrer, weil ich Kinder mag."

### B2 (중상급)
- 복잡한 구문 자주 사용
- 풍부한 어휘
- 문법이 대체로 정확
- 예: "Obwohl ich müde war, habe ich bis spät in die Nacht gearbeitet."

### C1 (고급)
- 복잡한 구문 능숙
- 추상적 어휘 구사
- 문법 거의 완벽
- 예: "Die Tatsache, dass die Wirtschaft trotz der Krise wächst, lässt sich durch..."

## 세부 단계 (Sub-Level)

- **초반**: 해당 레벨 진입 단계
- **중반**: 해당 레벨의 전형적 특징
- **후반**: 다음 레벨로 넘어가기 직전

## API 사용량

### 레벨 테스트 1회당
- **GPT-4o mini 호출**: 2회
  1. 최종 피드백 생성 (레벨 판정)
  2. 스킬 숙련도 평가
- **예상 비용**: ~$0.01-0.02 (토큰 수에 따라 변동)

### 임베딩 모델
- **모델**: `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- **로컬 실행**: 비용 없음
- **캐시**: `models_cache/` 디렉토리

## 테스트 방법

```bash
# 레벨 테스트 실행
streamlit run app.py
# → 레벨 테스트 페이지 이동

# 5개 질문 답변 후 결과 확인
# → GPT 판정 레벨 표시
# → 코사인 유사도 참고 정보 (콘솔 출력)
```

## 디버깅

### 레벨 판정 로그 확인
```python
# src/level_test/CEFR_Eval.py:1037
print(f"\n📊 레벨 판정 결과:")
print(f"   GPT 판정: {final_level_name}-{sub_level_name}")
print(f"   코사인 유사도 참고: {cosine_level.name}-{cosine_sub.value}")
```

### GPT 프롬프트 확인
- `AIFeedbackGenerator._build_evaluation_prompt()` 메서드 참조

## 향후 개선 가능성

1. **GPT 응답 캐싱**: 동일한 답변 패턴에 대해 캐싱
2. **앙상블 방식**: 코사인 유사도 + GPT 판정 가중 평균
3. **A1 레벨 지원**: 현재 A2~C1만 지원
4. **실시간 피드백**: 각 답변마다 즉시 피드백 제공
