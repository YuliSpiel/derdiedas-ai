"""
GPT 기반 학습 컨텐츠 생성기

1회 호출로 모든 컨텐츠 생성:
- 개념 설명 (독일어 + 한국어)
- 예문 (최소 5개)
- 단답형 문제 10개
- 작문 과제 1개
"""

import json
import os
from typing import Dict, Optional
import openai
from pathlib import Path


class LearningContentGenerator:
    """학습 컨텐츠 생성기"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_content(
        self,
        skill_id: str,
        skill_name: str,
        skill_description: str,
        user_cefr_level: str = "A2",
        user_interests: list = None,
        user_goals: list = None,
        model: str = "gpt-4o-mini"
    ) -> Dict:
        """
        학습 컨텐츠 일괄 생성

        Args:
            skill_id: 스킬 ID (예: G.ART.DEF.NOM)
            skill_name: 스킬 이름 (예: Definite article – nominative)
            skill_description: 스킬 설명 (한국어)
            user_cefr_level: 사용자 CEFR 레벨
            user_interests: 사용자 관심사 (예: ["여행", "음악", "IT"])
            user_goals: 사용자 목표 (예: ["회화", "문법"])
            model: 사용할 GPT 모델

        Returns:
            {
                "concept_de": "독일어 설명",
                "concept_ko": "한국어 설명",
                "examples": [{"de": "...", "ko": "..."}],
                "quiz_questions": [{...}],
                "writing_task": {...}
            }
        """

        prompt = self._build_content_generation_prompt(
            skill_id, skill_name, skill_description, user_cefr_level,
            user_interests or [], user_goals or []
        )

        try:
            print(f"🤖 GPT 컨텐츠 생성 중... (스킬: {skill_id})")

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 독일어 교육 전문가입니다. 학습자의 수준에 맞는 명확하고 효과적인 학습 컨텐츠를 생성합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            print("✅ 컨텐츠 생성 완료")

            return result

        except Exception as e:
            print(f"❌ 컨텐츠 생성 실패: {e}")
            return self._get_fallback_content(skill_name)

    def _build_content_generation_prompt(
        self,
        skill_id: str,
        skill_name: str,
        skill_description: str,
        user_cefr_level: str,
        user_interests: list,
        user_goals: list
    ) -> str:
        """컨텐츠 생성 프롬프트 구성"""

        # 관심사/목표 문자열 생성
        interests_str = ", ".join(user_interests) if user_interests else "일반적인 주제"
        goals_str = ", ".join(user_goals) if user_goals else "전반적인 독일어 실력 향상"

        prompt = f"""
다음 독일어 문법 주제에 대한 학습 컨텐츠를 생성해 주세요.

## 주제 정보
- **스킬 ID**: {skill_id}
- **스킬 이름**: {skill_name}
- **설명**: {skill_description}
- **학습자 레벨**: {user_cefr_level}

## 학습자 프로필
- **관심사**: {interests_str}
- **학습 목표**: {goals_str}

**중요**: 예문, 퀴즈 문제, 작문 과제를 생성할 때 학습자의 관심사와 목표를 최대한 반영하세요.
예를 들어:
- 관심사가 "여행"이면 → 여행 관련 문장 사용 (호텔, 관광지, 교통수단 등)
- 관심사가 "음악"이면 → 음악 관련 문장 사용 (악기, 콘서트, 음악가 등)
- 목표가 "회화"이면 → 실제 대화에서 자주 쓰이는 표현 우선
- 목표가 "문법"이면 → 문법 규칙에 더 집중

## 생성할 컨텐츠

### 1. 개념 설명
- **독일어 설명** (concept_de): {user_cefr_level} 레벨 학습자가 이해할 수 있는 쉬운 독일어로 작성
  - 핵심 문법 규칙 설명
  - 2-3 문단 분량
  - 명확하고 간결하게
- **한국어 설명** (concept_ko): 한국어 모국어 화자를 위한 자세한 설명
  - 독일어 설명과 동일한 내용
  - 더 자세한 예시와 비유 사용 가능

### 2. 예문 (examples)
- **최소 7개** 제공
- 각 예문:
  - `de`: 독일어 문장 (타겟 문법 요소 포함)
  - `ko`: 한국어 번역
- 다양한 상황과 어휘 사용
- 쉬운 것부터 어려운 순서로 배치

### 3. 단답형 문제 (quiz_questions)
- **정확히 10개** 생성
- 문제 유형:
  - `fill_blank`: 빈칸 채우기 (가장 많이 사용)
  - `multiple_choice`: 객관식 (2-3개)
- 각 문제 구조:
  - `id`: "q1", "q2", ... "q10"
  - `type`: "fill_blank" 또는 "multiple_choice"
  - `question`: 문제 텍스트 (독일어)
  - `options`: 선택지 배열 (multiple_choice인 경우, 3-4개)
  - `correct_answer`: 정답
  - `hint`: 힌트 (한국어, **정답을 직접 언급하지 않고** 문제 해결 방향만 제시)
  - `explanation`: 정답 해설 (한국어, 정답 공개 후에 보여줄 자세한 설명)
- 난이도: 쉬운 것부터 어려운 순서
- 다양한 문맥 사용

**중요**:
- `hint`는 정답을 직접 말하지 않고 문제를 푸는 방법만 알려주세요
  - 예: "명사의 성을 먼저 확인하세요" (O)
  - 예: "답은 'die'입니다" (X)
- `explanation`은 정답 공개 후 자세한 설명이므로 정답 포함 가능

### 4. 작문 과제 (writing_task)
- `prompt_de`: 독일어 지시문
- `prompt_ko`: 한국어 지시문 (동일 내용)
- `min_sentences`: 최소 문장 수 (3)
- `target_grammar`: 사용해야 할 문법 요소 (학습한 주제)
- 학습자가 배운 문법을 실제로 사용해볼 수 있는 과제

## 출력 형식 (JSON)

```json
{{
  "concept_de": "독일어 개념 설명...",
  "concept_ko": "한국어 개념 설명...",
  "examples": [
    {{"de": "Der Mann geht zur Schule.", "ko": "그 남자는 학교에 간다."}},
    ...
  ],
  "quiz_questions": [
    {{
      "id": "q1",
      "type": "fill_blank",
      "question": "__ Katze schläft auf dem Sofa.",
      "correct_answer": "Die",
      "hint": "명사 'Katze'의 성을 먼저 확인하세요. 주격 형태입니다.",
      "explanation": "'Katze'는 여성 명사이고 주격이므로 'die'를 사용합니다."
    }},
    {{
      "id": "q2",
      "type": "multiple_choice",
      "question": "Ich sehe __ Auto.",
      "options": ["der", "die", "das"],
      "correct_answer": "das",
      "hint": "'Auto'의 성과 문장에서의 격을 생각해보세요.",
      "explanation": "'Auto'는 중성 명사이고 대격(목적어)이므로 'das'를 사용합니다."
    }},
    ...
  ],
  "writing_task": {{
    "prompt_de": "Schreibe 3 Sätze über deinen Alltag. Benutze definite Artikel im Nominativ.",
    "prompt_ko": "일상에 대해 3문장을 쓰세요. 주격 정관사를 사용하세요.",
    "min_sentences": 3,
    "target_grammar": "{skill_name}"
  }}
}}
```

**중요**:
- 모든 독일어 문장은 문법적으로 정확해야 합니다
- 예문과 문제는 학습자 레벨에 맞는 어휘 사용
- 정답 해설은 명확하고 이해하기 쉽게
- 반드시 유효한 JSON 형식으로 출력
"""
        return prompt.strip()

    def _get_fallback_content(self, skill_name: str) -> Dict:
        """API 실패 시 기본 컨텐츠"""
        return {
            "concept_de": "Inhalt konnte nicht generiert werden.",
            "concept_ko": "컨텐츠를 생성할 수 없습니다. API 키를 확인해주세요.",
            "examples": [],
            "quiz_questions": [],
            "writing_task": {
                "prompt_de": "Keine Aufgabe verfügbar.",
                "prompt_ko": "과제를 생성할 수 없습니다.",
                "min_sentences": 3,
                "target_grammar": skill_name
            }
        }


if __name__ == "__main__":
    # 테스트
    generator = LearningContentGenerator()

    content = generator.generate_content(
        skill_id="G.ART.DEF.NOM",
        skill_name="Definite article – nominative",
        skill_description="독일어 정관사 주격: der, die, das의 사용법",
        user_cefr_level="A2"
    )

    print("\n" + "=" * 60)
    print("생성된 컨텐츠:")
    print("=" * 60)
    print(f"\n📖 개념 설명 (독일어): {content['concept_de'][:100]}...")
    print(f"\n📖 개념 설명 (한국어): {content['concept_ko'][:100]}...")
    print(f"\n📚 예문 개수: {len(content['examples'])}")
    print(f"❓ 문제 개수: {len(content['quiz_questions'])}")
    print(f"\n✍️ 작문 과제: {content['writing_task']['prompt_ko']}")
