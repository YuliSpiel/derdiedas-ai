"""
스킬별 숙련도 평가 모듈

레벨테스트 완료 시 사용자의 작문 샘플을 분석하여
온톨로지 기반 스킬별 숙련도(0-100)를 평가합니다.
"""

import json
import csv
from typing import Dict, List
from pathlib import Path
import openai
import os


class SkillProficiencyAssessor:
    """LLM 기반 스킬 숙련도 평가기"""

    def __init__(self, ontology_path: str = None, skill_tree_path: str = None):
        """
        Args:
            ontology_path: grammar_ontology.json 경로
            skill_tree_path: skill_tree.csv 경로
        """
        if ontology_path is None:
            project_root = Path(__file__).parent.parent.parent
            ontology_path = project_root / "data" / "grammar_ontology" / "grammar_ontology.json"
            skill_tree_path = project_root / "data" / "grammar_ontology" / "skill_tree.csv"

        self.ontology_path = Path(ontology_path)
        self.skill_tree_path = Path(skill_tree_path)
        self.skills = self._load_skills()

        # OpenAI API 초기화
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _load_skills(self) -> Dict:
        """온톨로지 스킬 로드 (CSV 메타데이터 + JSON 컨텐츠 합침)"""
        # 1. CSV에서 메타데이터 로드
        metadata = {}
        if self.skill_tree_path.exists():
            with open(self.skill_tree_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    metadata[row['skill_id']] = {
                        'id': row['skill_id'],
                        'title_ko': row['name'],
                        'title_en': row['name'],
                        'category': row['area'],
                        'cefr_level': row['cefr'],
                        'domain': row['domain'],
                        'prerequisites': row.get('prerequisites', '').split(',') if row.get('prerequisites') else [],
                    }

        # 2. JSON에서 컨텐츠 로드
        if not self.ontology_path.exists():
            print(f"⚠️ 온톨로지 파일 없음: {self.ontology_path}")
            return metadata  # CSV 메타데이터만이라도 반환

        with open(self.ontology_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 리스트 형식 처리
        topics = data if isinstance(data, list) else data.get("topics", [])

        # 3. 메타데이터와 컨텐츠 합치기
        skills = {}
        for topic in topics:
            skill_id = topic.get("skill_id") or topic.get("id")
            if skill_id in metadata:
                # 메타데이터 + JSON 컨텐츠 합침
                skills[skill_id] = {**metadata[skill_id], **topic}
            else:
                # JSON만 있는 경우 (메타데이터 없음)
                skills[skill_id] = topic

        # 4. JSON에 없지만 CSV에만 있는 스킬 추가 (메타데이터만)
        for skill_id, meta in metadata.items():
            if skill_id not in skills:
                skills[skill_id] = meta

        return skills

    def assess_proficiency(
        self,
        user_level: str,
        writing_samples: List[str],
        model: str = "gpt-4o-mini"
    ) -> Dict[str, float]:
        """
        사용자의 작문 샘플을 분석하여 스킬별 숙련도 평가

        Args:
            user_level: 사용자 CEFR 레벨 (예: "B1")
            writing_samples: 사용자가 작성한 독일어 문장 리스트
            model: 사용할 OpenAI 모델

        Returns:
            {skill_id: proficiency_score (0-100)} 딕셔너리
        """
        if not self.skills:
            print("⚠️ 스킬 데이터가 로드되지 않았습니다.")
            return {}

        # 사용자 레벨 이하의 스킬만 평가
        target_skills = self._get_skills_up_to_level(user_level)

        if not target_skills:
            print(f"⚠️ {user_level} 레벨 이하 스킬이 없습니다.")
            return {}

        # LLM 프롬프트 생성
        prompt = self._create_assessment_prompt(target_skills, writing_samples)

        try:
            # OpenAI API 호출
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 독일어 문법 전문가입니다. 학습자의 작문을 분석하여 각 문법 스킬의 숙련도를 0-100 점수로 평가합니다."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            # 응답 파싱
            result_text = response.choices[0].message.content
            proficiency_data = json.loads(result_text)

            # None 값 필터링 (평가 불가한 스킬 제외)
            proficiency = proficiency_data.get("proficiency", {})
            return {k: v for k, v in proficiency.items() if v is not None}

        except Exception as e:
            print(f"❌ 숙련도 평가 오류: {e}")
            return {}

    def _get_skills_up_to_level(self, user_level: str) -> List[Dict]:
        """사용자 레벨 이하의 스킬만 필터링"""
        level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]

        try:
            user_level_idx = level_order.index(user_level)
        except ValueError:
            print(f"⚠️ 유효하지 않은 레벨: {user_level}")
            return []

        target_skills = []
        for skill_id, skill in self.skills.items():
            skill_level = skill.get("cefr_level", "A1")
            try:
                skill_level_idx = level_order.index(skill_level)
                if skill_level_idx <= user_level_idx:
                    target_skills.append(skill)
            except ValueError:
                continue

        return target_skills

    def _create_assessment_prompt(
        self,
        target_skills: List[Dict],
        writing_samples: List[str]
    ) -> str:
        """LLM 평가 프롬프트 생성"""

        # 스킬 요약 정보 생성
        skills_summary = []
        for skill in target_skills:
            skills_summary.append({
                "id": skill["id"],
                "title_ko": skill.get("title_ko", ""),
                "title_en": skill.get("title_en", ""),
                "cefr_level": skill.get("cefr_level", ""),
                "summary": skill.get("summary", ""),
            })

        prompt = f"""
다음은 독일어 학습자가 레벨테스트에서 작성한 문장들입니다:

## 학습자 작문 샘플:
{chr(10).join(f"{i+1}. {sample}" for i, sample in enumerate(writing_samples))}

## 평가 대상 문법 스킬:
{json.dumps(skills_summary, ensure_ascii=False, indent=2)}

## 평가 지침:
1. 각 문법 스킬에 대해 학습자의 작문 샘플을 분석하세요.
2. 해당 스킬이 문장에서 **정확하게 사용되었는지** 평가하세요.
3. 숙련도 점수는 0-100 사이 정수로 제공하세요:
   - 0-30: 거의 사용하지 않거나 심각한 오류
   - 31-50: 기본적인 이해는 있으나 자주 실수
   - 51-70: 대체로 정확하나 가끔 실수
   - 71-85: 안정적으로 정확하게 사용
   - 86-100: 완벽하게 숙달

4. **작문 샘플에서 해당 스킬이 전혀 사용되지 않은 경우**, 평가 불가(null)로 처리하세요.

## 출력 형식 (JSON):
```json
{{
  "proficiency": {{
    "G.ART.DEF.NOM": 75,
    "G.ART.INDEF.ACC": 60,
    "G.V.TENSE.PRES": 80,
    ...
  }}
}}
```

**중요**: 모든 스킬 ID에 대해 점수를 제공하되, 평가 불가한 경우 해당 스킬을 제외하세요.
"""
        return prompt.strip()


if __name__ == "__main__":
    # 테스트
    assessor = SkillProficiencyAssessor()

    # 샘플 작문
    samples = [
        "Ich habe gestern ein Buch gelesen.",
        "Der Mann geht in die Schule.",
        "Sie möchte einen Kaffee trinken."
    ]

    # 평가 실행
    result = assessor.assess_proficiency(
        user_level="B1",
        writing_samples=samples
    )

    print("📊 스킬별 숙련도 평가 결과:")
    for skill_id, score in sorted(result.items()):
        print(f"  {skill_id}: {score}/100")
