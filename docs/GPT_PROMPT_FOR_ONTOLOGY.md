# GPT에게 문법 온톨로지 데이터 생성 요청 프롬프트

다음 프롬프트를 GPT에게 전달하여 완전한 문법 온톨로지 데이터를 생성받으세요.

---

## 📋 프롬프트

```
독일어 학습 플랫폼을 위한 문법 온톨로지 데이터를 생성해주세요.

### 입력 데이터

1. **skill_tree.csv**: 66개 문법 스킬의 메타데이터
   - skill_id: 고유 식별자 (예: G.ART.DEF.NOM)
   - name: 영어 이름
   - domain: 도메인 (Grammar)
   - area: 영역 (Articles, Verbs 등)
   - cefr: CEFR 레벨 (A1, A2, B1, B2)
   - prerequisites: 선행 스킬 (세미콜론 구분)
   - ud_features: Universal Dependencies 문법 특성
   - hint: 한국어 힌트

2. **ontology_template.json**: 66개 스킬의 템플릿 구조

### 요청 사항

**아래 JSON 형식으로 66개 스킬 모두에 대한 데이터를 생성해주세요:**

```json
[
  {
    "id": "G.ART.DEF.NOM",
    "title_de": "Definite article – nominative",
    "title_ko": "정관사 - 주격",
    "title_en": "Definite article – nominative",
    "cefr_level": "A1",
    "category": "articles",
    "subcategory": "Articles",
    "tags": ["Definite article", "nominative"],
    "difficulty_score": 1.0,
    "estimated_time": 15,
    "prerequisites": [],
    "related_topics": ["G.ART.DEF.ACC"],
    "summary": "독일어 정관사(der/die/das)의 주격 형태를 다룹니다.",
    "rules": "독일어의 정관사는 명사의 성(남성/여성/중성)과 수(단수/복수)에 따라 형태가 달라집니다. 주격(1격)에서는 남성 명사 앞에 'der', 여성 명사 앞에 'die', 중성 명사 앞에 'das', 복수형 앞에 'die'를 사용합니다. 주격은 문장의 주어를 나타낼 때 사용됩니다.",
    "examples": [
      {"de": "Der Mann ist groß.", "ko": "그 남자는 키가 크다."},
      {"de": "Die Frau arbeitet heute.", "ko": "그 여자는 오늘 일한다."},
      {"de": "Das Kind spielt im Garten.", "ko": "그 아이는 정원에서 논다."},
      {"de": "Die Bücher sind interessant.", "ko": "그 책들은 재미있다."}
      // ... 최소 20개 예문
    ],
    "exercises": [
      {
        "type": "multiple_choice",
        "question": "_____ Hund spielt im Garten.",
        "options": ["Der", "Die", "Das"],
        "answer": "Der",
        "explanation": "'Hund'는 남성 명사이므로 주격에서 'der'를 사용합니다."
      },
      {
        "type": "fill_in_blank",
        "question": "_____ Frau kocht das Essen.",
        "answer": "Die",
        "explanation": "'Frau'는 여성 명사이므로 'die'를 사용합니다."
      }
      // ... 최소 10개 문제
    ],
    "common_mistakes": [
      "명사의 성을 잘못 알고 틀린 정관사를 쓰는 실수 (예: die Mann → der Mann)",
      "정관사를 생략하는 실수 (독일어에서는 명사 앞에 관사가 필수)",
      "복수형에 단수 정관사를 쓰는 실수 (예: das Kinder → die Kinder)"
    ],
    "source": "Skill Tree CSV",
    "created_at": "2025-10-21",
    "updated_at": "2025-10-21",
    "ud_features": "PronType=Art;Definite=Def;Case=Nom"
  }
  // ... 나머지 65개 스킬
]
```

### 품질 기준

각 스킬당:
- ✅ **예문 (examples)**: 최소 20개 (독일어 + 한국어 번역)
  - 실용적이고 자연스러운 문장
  - CEFR 레벨에 맞는 난이도
  - 다양한 상황과 어휘 사용

- ✅ **연습 문제 (exercises)**: 최소 10개
  - 문제 유형: multiple_choice, fill_in_blank 등
  - 명확한 정답과 설명 포함
  - 난이도 점진적 증가

- ✅ **규칙 설명 (rules)**: 명확하고 상세한 한국어 설명
  - 문법 규칙의 핵심 개념
  - 사용 시점과 방법
  - 예외사항 포함

- ✅ **흔한 실수 (common_mistakes)**: 최소 3개
  - 한국인 학습자가 자주 하는 실수
  - 올바른 형태 제시

- ✅ **메타데이터**:
  - skill_tree.csv의 정보 활용
  - prerequisites 관계 유지
  - CEFR 레벨 정확히 반영

### 참고 파일

첨부된 파일들:
1. `skill_tree.csv` - 66개 스킬의 메타데이터
2. `ontology_template.json` - JSON 구조 템플릿

### 출력 형식

- 전체 66개 스킬을 포함한 단일 JSON 배열
- 파일명: `grammar_ontology.json`
- UTF-8 인코딩
- 들여쓰기: 2 spaces

### 우선순위

**필수 스킬 (먼저 생성):**
- A1 레벨: 28개 스킬 (기초 관사, 동사, 명사 등)
- A2 레벨: 20개 스킬
- B1 레벨: 14개 스킬
- B2 레벨: 4개 스킬

### 예문 작성 가이드

- 일상생활에서 자주 쓰이는 표현
- 문화적으로 중립적인 내용
- 명확하고 간결한 문장
- 각 레벨에 적합한 어휘와 구조

### 연습 문제 가이드

**문제 유형 분포:**
- multiple_choice: 60%
- fill_in_blank: 30%
- sentence_building: 10%

**난이도:**
- easy: 40%
- medium: 40%
- hard: 20%

---

생성이 완료되면 `grammar_ontology.json` 파일로 제공해주세요.
```

---

## 📎 첨부할 파일

GPT에게 다음 파일들을 함께 첨부하세요:

1. `data/grammar_ontology/skill_tree.csv`
2. `data/grammar_ontology/ontology_template.json`

## ✅ 완료 후

생성된 `grammar_ontology.json` 파일을:
- `data/grammar_ontology/grammar_ontology.json`에 저장
- 시스템이 자동으로 로드하여 사용

## 🧪 테스트

```bash
python -c "
from src.models.grammar_ontology import GrammarOntologyLoader
loader = GrammarOntologyLoader()
topics = loader.load_all_topics()
print(f'✅ 로드 성공: {len(topics)}개 주제')
"
```
