"""
스킬 트리 CSV를 온톨로지 구조로 변환하는 유틸리티

skill_tree.csv 파일을 읽어서 GrammarTopic 구조로 매핑
"""

import csv
from pathlib import Path
from typing import Dict, List
import json


class SkillTreeLoader:
    """스킬 트리 CSV 로더"""

    def __init__(self, csv_path: str = None):
        if csv_path is None:
            project_root = Path(__file__).parent.parent.parent
            csv_path = project_root / "data" / "grammar_ontology" / "skill_tree.csv"

        self.csv_path = Path(csv_path)
        self.skills: List[Dict] = []

    def load(self) -> List[Dict]:
        """CSV 로드"""
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.skills = list(reader)

        print(f"✅ {len(self.skills)}개 스킬 로드 완료")
        return self.skills

    def to_ontology_structure(self) -> Dict:
        """온톨로지 JSON 구조로 변환"""
        topics = []

        for skill in self.skills:
            # prerequisites 파싱 (세미콜론 또는 쉼표 구분)
            prereq_str = skill.get('prerequisites', '').strip()
            if prereq_str:
                prerequisites = [p.strip() for p in prereq_str.replace(';', ',').split(',') if p.strip()]
            else:
                prerequisites = []

            # 카테고리 추출 (area 필드에서)
            area = skill.get('area', 'Grammar')
            category = self._map_area_to_category(area)

            topic = {
                "id": skill['skill_id'],
                "title_de": skill['name'].split('–')[0].strip() if '–' in skill['name'] else skill['name'],
                "title_ko": skill['hint'],
                "title_en": skill['name'],

                "cefr_level": skill['cefr'],
                "category": category,
                "subcategory": area,
                "tags": self._extract_tags(skill),

                "difficulty_score": self._calculate_difficulty(skill['cefr']),
                "estimated_time": 15,  # 기본값
                "prerequisites": prerequisites,
                "related_topics": [],  # GPT가 채울 예정

                "summary": f"{skill['name']} - {skill['hint']}",
                "rules": [],  # GPT가 채울 예정
                "examples": [],  # GPT가 채울 예정
                "exercises": [],  # GPT가 채울 예정
                "common_mistakes": [],  # GPT가 채울 예정

                "source": "Skill Tree CSV",
                "created_at": "",
                "updated_at": "",

                # 추가 메타데이터
                "ud_features": skill.get('ud_features', '')
            }

            topics.append(topic)

        ontology = {
            "version": "1.0",
            "created_at": "",
            "metadata": {
                "total_topics": len(topics),
                "by_category": self._count_by_field(topics, 'category'),
                "by_cefr_level": self._count_by_field(topics, 'cefr_level'),
            },
            "topics": topics
        }

        return ontology

    def _map_area_to_category(self, area: str) -> str:
        """Area를 카테고리로 매핑"""
        mapping = {
            'Articles': 'articles',
            'Nouns': 'nouns',
            'Nouns & Case': 'cases',
            'Pronouns': 'pronouns',
            'Adjectives': 'adjectives',
            'Verbs': 'verbs',
            'Negation': 'negation',
            'Word Order': 'word_order',
            'Clauses': 'clauses',
            'Questions': 'questions',
            'Imperatives': 'imperatives',
            'Prepositions': 'prepositions',
            'Numerals&Time': 'time',
            'Particles': 'particles'
        }
        return mapping.get(area, 'other')

    def _extract_tags(self, skill: Dict) -> List[str]:
        """스킬에서 태그 추출"""
        tags = []

        # name에서 주요 단어 추출
        name = skill['name']
        if '–' in name:
            parts = [p.strip() for p in name.split('–')]
            tags.extend(parts)

        # hint 추가
        if skill['hint']:
            tags.append(skill['hint'])

        return tags[:5]

    def _calculate_difficulty(self, cefr: str) -> float:
        """CEFR 레벨로 난이도 계산"""
        scores = {
            'A1': 1.0,
            'A2': 2.0,
            'B1': 3.0,
            'B2': 4.0,
            'C1': 5.0
        }
        return scores.get(cefr, 2.5)

    def _count_by_field(self, topics: List[Dict], field: str) -> Dict:
        """필드별 카운트"""
        counts = {}
        for topic in topics:
            value = topic[field]
            counts[value] = counts.get(value, 0) + 1
        return counts

    def save_ontology_template(self, output_path: str = None):
        """온톨로지 템플릿 저장"""
        if output_path is None:
            project_root = Path(__file__).parent.parent.parent
            output_path = project_root / "data" / "grammar_ontology" / "ontology_template.json"

        ontology = self.to_ontology_structure()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ontology, f, ensure_ascii=False, indent=2)

        print(f"💾 온톨로지 템플릿 저장: {output_path}")
        print(f"   - 총 {len(ontology['topics'])}개 주제")
        print(f"   - GPT에게 rules, examples, exercises 생성 요청하세요")

        # 통계 출력
        print("\n📊 카테고리별 분포:")
        for cat, count in sorted(ontology['metadata']['by_category'].items()):
            print(f"   {cat}: {count}개")

        print("\n📊 CEFR 레벨별 분포:")
        for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
            count = ontology['metadata']['by_cefr_level'].get(level, 0)
            if count > 0:
                print(f"   {level}: {count}개")


if __name__ == "__main__":
    loader = SkillTreeLoader()
    skills = loader.load()
    loader.save_ontology_template()
