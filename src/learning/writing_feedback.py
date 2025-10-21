"""
GPT 기반 작문 피드백 생성기

사용자의 독일어 작문에 대해:
- 문법 오류 교정
- 어휘 사용 평가
- 과제 완성도 평가
- 구체적인 개선 제안
"""

import json
import os
from typing import Dict, Optional
import openai


class WritingFeedbackGenerator:
    """작문 피드백 생성기"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")

        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_feedback(
        self,
        user_text: str,
        task_prompt: str,
        target_grammar: str,
        user_cefr_level: str = "A2",
        model: str = "gpt-4o-mini"
    ) -> Dict:
        """
        작문 피드백 생성

        Args:
            user_text: 사용자가 작성한 독일어 작문
            task_prompt: 작문 과제 지시문
            target_grammar: 목표 문법 요소
            user_cefr_level: 사용자 CEFR 레벨
            model: 사용할 GPT 모델

        Returns:
            {
                "grammar_score": 0-5,
                "vocabulary_score": 0-5,
                "task_completion_score": 0-5,
                "corrections": [{...}],
                "positive_feedback": [...],
                "improvement_tips": [...],
                "skill_proficiency_change": float (-10 to +10)
            }
        """

        prompt = self._build_feedback_prompt(
            user_text, task_prompt, target_grammar, user_cefr_level
        )

        try:
            print(f"🤖 GPT 피드백 생성 중...")

            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 독일어 교육 전문가입니다. 학습자의 작문을 친절하고 건설적으로 피드백합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # 피드백은 일관성이 중요
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            print("✅ 피드백 생성 완료")

            return result

        except Exception as e:
            print(f"❌ 피드백 생성 실패: {e}")
            return self._get_fallback_feedback()

    def _build_feedback_prompt(
        self,
        user_text: str,
        task_prompt: str,
        target_grammar: str,
        user_cefr_level: str
    ) -> str:
        """피드백 생성 프롬프트 구성"""

        prompt = f"""
다음 독일어 작문에 대한 피드백을 생성해 주세요.

## 과제 정보
- **과제 지시문**: {task_prompt}
- **목표 문법**: {target_grammar}
- **학습자 레벨**: {user_cefr_level}

## 학습자 작문
```
{user_text}
```

## 평가 기준

### 1. 문법 점수 (grammar_score: 0-5)
- 5점: 문법 오류 없음
- 4점: 사소한 오류 1-2개
- 3점: 중간 수준 오류 3-4개
- 2점: 많은 오류, 하지만 의미 전달 가능
- 1점: 심각한 오류, 의미 파악 어려움
- 0점: 작문 불가

### 2. 어휘 점수 (vocabulary_score: 0-5)
- 5점: 레벨에 매우 적합한 다양한 어휘 사용
- 4점: 적절한 어휘 사용
- 3점: 기본적인 어휘 사용, 일부 반복
- 2점: 제한적인 어휘, 많은 반복
- 1점: 매우 제한적인 어휘
- 0점: 어휘 부족

### 3. 과제 완성도 (task_completion_score: 0-5)
- 5점: 과제 요구사항 완벽히 충족
- 4점: 대부분 충족
- 3점: 부분적으로 충족
- 2점: 일부만 충족
- 1점: 거의 충족 못함
- 0점: 과제 미수행

### 4. 교정 사항 (corrections)
각 오류에 대해:
- `original`: 잘못된 부분
- `corrected`: 교정된 내용
- `explanation`: 한국어로 왜 틀렸는지 설명
- `error_type`: "grammar", "vocabulary", "spelling" 중 하나

**최대 5개의 가장 중요한 오류만** 선택하세요.

### 5. 긍정적 피드백 (positive_feedback)
- 잘한 점 2-3개 (구체적으로)
- 한국어로 작성
- 예: "정관사를 정확하게 사용했어요!", "문장 구조가 자연스러워요"

### 6. 개선 팁 (improvement_tips)
- 다음 학습을 위한 구체적인 조언 2-3개
- 한국어로 작성
- 예: "전치사 뒤의 격 변화에 주의하세요", "동사 어미 변화를 복습해보세요"

### 7. 숙련도 변화량 (skill_proficiency_change)
- 목표 문법에 대한 숙련도 변화량
- 범위: -10 ~ +10
- 계산:
  - 문법 점수 5: +8~+10
  - 문법 점수 4: +5~+7
  - 문법 점수 3: +2~+4
  - 문법 점수 2: 0~+1
  - 문법 점수 1: -2~-1
  - 문법 점수 0: -5~-3

## 출력 형식 (JSON)

```json
{{
  "grammar_score": 4,
  "vocabulary_score": 4,
  "task_completion_score": 5,
  "corrections": [
    {{
      "original": "Ich gehe zur Schule.",
      "corrected": "Ich gehe zur Schule.",
      "explanation": "'zur'는 'zu + der'의 축약형으로 올바르게 사용했습니다.",
      "error_type": "grammar"
    }},
    ...
  ],
  "positive_feedback": [
    "정관사 격 변화를 정확하게 사용했어요!",
    "문장 구조가 자연스럽습니다."
  ],
  "improvement_tips": [
    "전치사 지배에 따른 격 변화를 복습해보세요.",
    "더 다양한 어휘를 사용해보세요."
  ],
  "skill_proficiency_change": 6.5
}}
```

**중요**:
- 학습자 레벨({user_cefr_level})에 맞는 기대치를 적용하세요
- 건설적이고 격려하는 톤으로 피드백하세요
- 교정은 가장 중요한 것만 선택하세요 (최대 5개)
- 반드시 유효한 JSON 형식으로 출력하세요
"""
        return prompt.strip()

    def _get_fallback_feedback(self) -> Dict:
        """API 실패 시 기본 피드백"""
        return {
            "grammar_score": 3,
            "vocabulary_score": 3,
            "task_completion_score": 3,
            "corrections": [],
            "positive_feedback": [
                "작문을 완료했습니다!",
                "독일어로 글쓰기를 시도한 것이 훌륭합니다."
            ],
            "improvement_tips": [
                "피드백을 생성할 수 없습니다. API 키를 확인해주세요."
            ],
            "skill_proficiency_change": 0
        }


if __name__ == "__main__":
    # 테스트
    generator = WritingFeedbackGenerator()

    user_text = """
    Ich gehe in die Schule. Der Lehrer ist sehr nett. Ich lerne Deutsch.
    """

    feedback = generator.generate_feedback(
        user_text=user_text,
        task_prompt="일상에 대해 3문장을 쓰세요. 정관사를 사용하세요.",
        target_grammar="Definite article – nominative",
        user_cefr_level="A2"
    )

    print("\n" + "=" * 60)
    print("생성된 피드백:")
    print("=" * 60)
    print(f"\n📊 문법 점수: {feedback['grammar_score']}/5")
    print(f"📚 어휘 점수: {feedback['vocabulary_score']}/5")
    print(f"✅ 과제 완성도: {feedback['task_completion_score']}/5")
    print(f"\n✨ 긍정적 피드백:")
    for item in feedback['positive_feedback']:
        print(f"  - {item}")
    print(f"\n💡 개선 팁:")
    for item in feedback['improvement_tips']:
        print(f"  - {item}")
    print(f"\n📈 숙련도 변화: {feedback['skill_proficiency_change']:+.1f}")
