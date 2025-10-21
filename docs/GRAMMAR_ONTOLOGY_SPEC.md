# 문법 학습 온톨로지 명세서

## 📋 개요

이 문서는 GPT가 생성할 문법 학습 온톨로지의 데이터 구조를 정의합니다.

## 🎯 목표

1. 체계적인 문법 주제 분류
2. CEFR 레벨 기반 학습 경로
3. 연습 문제 및 예제 데이터
4. 사용자 숙련도 추적 지원

---

## 📊 데이터 구조

### 1. GrammarTopic (문법 주제)

```json
{
  "id": "akkusativ-case",
  "title_de": "Der Akkusativ",
  "title_ko": "대격 (4격)",
  "title_en": "The Accusative Case",

  "cefr_level": "A2",
  "category": "cases",
  "subcategory": "noun_cases",
  "tags": ["격변화", "명사", "관사"],

  "difficulty_score": 2.3,
  "estimated_time": 20,
  "prerequisites": ["nominativ-case", "articles-overview"],
  "related_topics": ["dativ-case", "akkusativ-prepositions"],

  "summary": "대격(Akkusativ)은 독일어의 4격으로, 동작의 직접 목적어를 나타냅니다...",

  "rules": [
    {
      "title": "정관사 변화",
      "description": "대격에서 남성 정관사 'der'는 'den'으로 변합니다...",
      "examples": [
        {
          "german": "Ich sehe den Mann.",
          "korean": "나는 그 남자를 봅니다.",
          "english": "I see the man.",
          "notes": "남성 명사 Mann 앞의 정관사가 den으로 변화"
        }
      ],
      "exceptions": ["중성과 여성 명사는 주격과 동일"]
    }
  ],

  "examples": [
    {
      "german": "Ich kaufe einen Apfel.",
      "korean": "나는 사과 하나를 삽니다.",
      "english": "I buy an apple."
    }
  ],

  "exercises": [
    {
      "id": "akk-ex-001",
      "type": "multiple_choice",
      "difficulty": "easy",
      "question": "빈칸에 알맞은 관사를 고르세요: Ich sehe ___ Hund.",
      "options": ["der", "den", "dem", "des"],
      "correct_answer": "den",
      "explanation": "Hund는 남성 명사이고 직접 목적어이므로 대격 정관사 'den'을 사용합니다.",
      "hints": ["동사 'sehen'의 목적어입니다", "Hund는 남성 명사입니다"]
    },
    {
      "id": "akk-ex-002",
      "type": "fill_in_blank",
      "difficulty": "medium",
      "question": "문장을 완성하세요: Er liest ____ Buch. (das)",
      "correct_answer": "das",
      "explanation": "중성 명사의 대격은 주격과 동일합니다.",
      "hints": ["Buch는 중성 명사입니다"]
    }
  ],

  "common_mistakes": [
    {
      "mistake": "Ich sehe der Mann.",
      "correction": "Ich sehe den Mann.",
      "explanation": "남성 명사의 대격에서는 'der'가 아닌 'den'을 사용해야 합니다."
    }
  ],

  "source": "Deutsch im Blick - Grammar",
  "created_at": "2024-10-21T10:00:00Z",
  "updated_at": "2024-10-21T10:00:00Z"
}
```

---

## 🔑 필드 설명

### 기본 정보
- **id**: 고유 식별자 (영문, 소문자, 하이픈)
- **title_de**: 독일어 제목
- **title_ko**: 한국어 제목
- **title_en**: 영어 제목

### 분류
- **cefr_level**: A1, A2, B1, B2, C1 중 하나
- **category**: verbs, nouns, adjectives, cases, prepositions, pronouns, conjunctions, word_order, vocabulary
- **subcategory**: 세부 분류 (예: verb_tenses, noun_cases)
- **tags**: 검색용 태그 배열

### 학습 정보
- **difficulty_score**: 1.0-5.0 (소수점 첫째자리)
- **estimated_time**: 예상 학습 시간 (분)
- **prerequisites**: 선행 학습 주제 ID 배열
- **related_topics**: 관련 주제 ID 배열

### 콘텐츠
- **summary**: 주제 요약 (200-500자)
- **rules**: 문법 규칙 배열
  - title, description, examples, exceptions
- **examples**: 예제 문장 배열 (최소 10개, 권장 20-30개)
  - german, korean, english(선택), notes(선택)
- **exercises**: 연습 문제 배열 (최소 10개, 권장 15-20개)
  - 난이도별 분포: easy 40%, medium 40%, hard 20%
  - 유형별 분포: multiple_choice 40%, fill_in_blank 30%, 기타 30%

### 연습 문제 유형
1. **multiple_choice**: 객관식
2. **fill_in_blank**: 빈칸 채우기
3. **sentence_building**: 문장 만들기
4. **translation**: 번역
5. **writing**: 자유 작문

### 메타데이터
- **source**: 출처
- **created_at**: 생성 시각 (ISO 8601)
- **updated_at**: 수정 시각 (ISO 8601)

---

## 📦 전체 온톨로지 파일 구조

```json
{
  "version": "1.0",
  "created_at": "2024-10-21T10:00:00Z",
  "metadata": {
    "total_topics": 69,
    "by_category": {
      "verbs": 27,
      "nouns": 25,
      "articles": 14
    },
    "by_cefr_level": {
      "A1": 42,
      "A2": 17,
      "B1": 10
    }
  },
  "topics": [
    /* GrammarTopic 객체 배열 */
  ]
}
```

---

## ✅ 품질 기준

### 각 주제별 필수 사항
- ✅ 예제 문장 최소 10개 이상
- ✅ 연습 문제 최소 10개 이상
- ✅ 다양한 문제 유형 포함
- ✅ 난이도 분포 적절
- ✅ 명확한 설명과 해설

### 예제 문장 요구사항
- 독일어 + 한국어 번역 필수
- 실생활에서 자주 쓰이는 표현
- 다양한 상황과 맥락
- 문법 포인트 명확히 표현

### 연습 문제 요구사항
- 명확한 질문
- 정답과 해설
- 힌트 제공 (선택)
- 점진적 난이도 증가

---

## 🎯 GPT 생성 가이드

### 프롬프트 예시

```
당신은 독일어 교육 전문가입니다.
다음 주제에 대한 체계적인 학습 콘텐츠를 생성해주세요:

주제: {topic_title}
CEFR 레벨: {cefr_level}
카테고리: {category}

다음을 포함해주세요:
1. 명확한 한국어 문법 설명
2. 실용적인 예제 문장 20개 (독일어 + 한국어)
3. 다양한 연습 문제 15개 (객관식, 빈칸채우기, 작문)
4. 학습자가 자주 하는 실수 3-5개

JSON 형식으로 출력해주세요.
```

---

## 📁 파일 저장 위치

```
data/
  grammar_ontology/
    grammar_ontology.json          # 전체 온톨로지
    topics/                        # 주제별 개별 파일 (선택)
      akkusativ-case.json
      perfekt-tense.json
      ...
```

---

## 🔄 연동 인터페이스

### Python 로드 예시

```python
from src.models.grammar_ontology import GrammarOntologyLoader

# 온톨로지 로드
loader = GrammarOntologyLoader()
topics = loader.load_all_topics()

# 특정 주제 조회
topic = loader.get_topic_by_id("akkusativ-case")

# 레벨별 조회
a2_topics = loader.get_topics_by_level(CEFRLevel.A2)

# 추천 주제
recommended = loader.get_recommended_topics(
    user_level=CEFRLevel.A2,
    user_progress=user_progress,
    limit=5
)
```

---

## 📊 예상 데이터 볼륨

- 주제당 평균 크기: ~50KB
- 전체 69개 주제: ~3-4MB
- 압축 시: ~1MB

---

## 🚀 다음 단계

1. ✅ 데이터 구조 정의 완료
2. ⏳ GPT로 온톨로지 생성
3. ⏳ 데이터 로드 및 검증
4. ⏳ 학습 사이클 페이지 구현
5. ⏳ 숙련도 추적 시스템 연동
