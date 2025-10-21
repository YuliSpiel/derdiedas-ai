"""
적응형 주제 선정 로직

사용자의 스킬 숙련도를 기반으로 다음 학습 주제를 선정합니다.
- 낮은 숙련도 주제 우선 선정 (가중치 기반)
- 학습 횟수가 적은 주제 우선
- 선행 스킬 충족 여부 확인
"""

import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import csv


class TopicSelector:
    """적응형 주제 선정기"""

    # 숙련도별 선택 확률 (수정 가능)
    PROFICIENCY_WEIGHTS = {
        "0-40": 0.40,    # 40%
        "40-60": 0.30,   # 30%
        "60-80": 0.20,   # 20%
        "80-100": 0.10,  # 10%
    }

    def __init__(
        self,
        skill_tree_path: str = None,
        ontology_path: str = None,
        custom_weights: Dict[str, float] = None
    ):
        """
        Args:
            skill_tree_path: skill_tree.csv 경로
            ontology_path: grammar_ontology.json 경로
            custom_weights: 커스텀 확률 가중치 (선택사항)
        """
        if skill_tree_path is None:
            project_root = Path(__file__).parent.parent.parent
            skill_tree_path = project_root / "data" / "grammar_ontology" / "skill_tree.csv"
            ontology_path = project_root / "data" / "grammar_ontology" / "grammar_ontology.json"

        self.skill_tree_path = Path(skill_tree_path)
        self.ontology_path = Path(ontology_path)

        # 가중치 설정
        if custom_weights:
            self.weights = custom_weights
        else:
            self.weights = self.PROFICIENCY_WEIGHTS.copy()

        # 스킬 메타데이터 로드
        self.skills = self._load_skills()

    def _load_skills(self) -> Dict:
        """스킬 트리 로드 (CSV + JSON 합침)"""
        skills = {}

        # 1. CSV에서 메타데이터 로드
        if self.skill_tree_path.exists():
            with open(self.skill_tree_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skills[row['skill_id']] = {
                        'id': row['skill_id'],
                        'name': row['name'],
                        'category': row['area'],
                        'cefr_level': row['cefr'],
                        'domain': row['domain'],
                        'prerequisites': row.get('prerequisites', '').split(',') if row.get('prerequisites') else [],
                    }

        # 2. JSON에서 컨텐츠 로드 (있으면)
        if self.ontology_path.exists():
            try:
                with open(self.ontology_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    topics = data if isinstance(data, list) else data.get("topics", [])

                    for topic in topics:
                        skill_id = topic.get("skill_id") or topic.get("id")
                        if skill_id in skills:
                            skills[skill_id].update(topic)
            except Exception as e:
                # JSON 파싱 실패 시 CSV 메타데이터만 사용
                print(f"⚠️ grammar_ontology.json 로딩 실패: {e}")
                print(f"   CSV 메타데이터만 사용합니다.")

        return skills

    def select_topic(
        self,
        user_proficiency: Dict[str, float],
        learning_count: Dict[str, int] = None,
        domain_filter: str = None,
        exclude_skills: List[str] = None
    ) -> Optional[str]:
        """
        적응형 주제 선정

        Args:
            user_proficiency: {skill_id: proficiency (0-100)}
            learning_count: {skill_id: count} 학습 횟수
            domain_filter: "Grammar" or "Expression" 필터 (선택사항)
            exclude_skills: 제외할 스킬 리스트

        Returns:
            선정된 skill_id (또는 None)
        """
        if learning_count is None:
            learning_count = {}

        if exclude_skills is None:
            exclude_skills = []

        # 1. 후보 스킬 필터링
        candidates = []
        for skill_id, skill in self.skills.items():
            # 제외 리스트 확인
            if skill_id in exclude_skills:
                continue

            # 도메인 필터
            if domain_filter and skill.get('domain') != domain_filter:
                continue

            # 숙련도 데이터가 있는 스킬만
            if skill_id in user_proficiency:
                candidates.append(skill_id)

        if not candidates:
            print("⚠️ 선택 가능한 주제가 없습니다.")
            return None

        # 2. 숙련도 구간별로 그룹화
        proficiency_groups = {
            "0-40": [],
            "40-60": [],
            "60-80": [],
            "80-100": [],
        }

        for skill_id in candidates:
            proficiency = user_proficiency[skill_id]

            if proficiency < 40:
                proficiency_groups["0-40"].append(skill_id)
            elif proficiency < 60:
                proficiency_groups["40-60"].append(skill_id)
            elif proficiency < 80:
                proficiency_groups["60-80"].append(skill_id)
            else:
                proficiency_groups["80-100"].append(skill_id)

        # 3. 가중치 기반으로 숙련도 구간 선택
        selected_group = self._select_proficiency_group(proficiency_groups)

        if not selected_group or not proficiency_groups[selected_group]:
            print("⚠️ 선택된 숙련도 구간에 주제가 없습니다.")
            return None

        # 4. 선택된 구간 내에서 학습 횟수가 적은 주제 우선 선정
        group_skills = proficiency_groups[selected_group]
        selected_skill = self._select_least_practiced(group_skills, learning_count)

        print(f"📚 선정된 주제: {selected_skill} (숙련도 구간: {selected_group})")
        print(f"   숙련도: {user_proficiency[selected_skill]:.1f}/100")
        print(f"   학습 횟수: {learning_count.get(selected_skill, 0)}회")

        return selected_skill

    def _select_proficiency_group(self, proficiency_groups: Dict[str, List[str]]) -> Optional[str]:
        """가중치 기반 숙련도 구간 선택"""
        # 각 구간에 스킬이 있는지 확인하고 가중치 계산
        valid_groups = []
        valid_weights = []

        for group, skills in proficiency_groups.items():
            if skills:  # 스킬이 있는 구간만
                valid_groups.append(group)
                valid_weights.append(self.weights[group])

        if not valid_groups:
            return None

        # 가중치 정규화
        total_weight = sum(valid_weights)
        normalized_weights = [w / total_weight for w in valid_weights]

        # 가중치 기반 랜덤 선택
        selected = random.choices(valid_groups, weights=normalized_weights, k=1)[0]

        return selected

    def _select_least_practiced(
        self,
        skill_ids: List[str],
        learning_count: Dict[str, int]
    ) -> str:
        """학습 횟수가 가장 적은 주제 선정"""
        # 학습 횟수 정렬
        sorted_skills = sorted(
            skill_ids,
            key=lambda s: learning_count.get(s, 0)
        )

        # 가장 적게 학습한 횟수
        min_count = learning_count.get(sorted_skills[0], 0)

        # 같은 횟수인 스킬들 중에서 랜덤 선택
        least_practiced = [
            s for s in sorted_skills
            if learning_count.get(s, 0) == min_count
        ]

        return random.choice(least_practiced)

    def get_skill_info(self, skill_id: str) -> Optional[Dict]:
        """스킬 정보 반환"""
        return self.skills.get(skill_id)

    def check_prerequisites(
        self,
        skill_id: str,
        user_proficiency: Dict[str, float],
        threshold: float = 50.0
    ) -> Tuple[bool, List[str]]:
        """
        선행 스킬 충족 여부 확인

        Args:
            skill_id: 확인할 스킬 ID
            user_proficiency: 사용자 숙련도
            threshold: 선행 스킬 요구 숙련도 (기본 50)

        Returns:
            (충족 여부, 미달 선행 스킬 리스트)
        """
        skill = self.skills.get(skill_id)
        if not skill:
            return False, []

        prerequisites = skill.get('prerequisites', [])
        if not prerequisites:
            return True, []

        unmet = []
        for prereq_id in prerequisites:
            if not prereq_id.strip():  # 빈 문자열 스킵
                continue

            proficiency = user_proficiency.get(prereq_id, 0)
            if proficiency < threshold:
                unmet.append(prereq_id)

        return len(unmet) == 0, unmet


if __name__ == "__main__":
    # 테스트
    selector = TopicSelector()

    # 샘플 숙련도 데이터
    user_proficiency = {
        "G.ART.DEF.NOM": 30,   # 낮은 숙련도
        "G.ART.DEF.ACC": 45,   # 중간 숙련도
        "G.ART.INDEF.NOM": 70, # 높은 숙련도
        "G.V.TENSE.PRES": 85,  # 매우 높은 숙련도
    }

    # 샘플 학습 횟수
    learning_count = {
        "G.ART.DEF.NOM": 0,
        "G.ART.DEF.ACC": 2,
        "G.ART.INDEF.NOM": 1,
        "G.V.TENSE.PRES": 3,
    }

    print("=" * 60)
    print("적응형 주제 선정 테스트")
    print("=" * 60)

    for i in range(5):
        print(f"\n[시도 {i+1}]")
        selected = selector.select_topic(user_proficiency, learning_count)

        if selected:
            skill_info = selector.get_skill_info(selected)
            print(f"스킬 이름: {skill_info.get('name')}")
            print(f"카테고리: {skill_info.get('category')}")
            print(f"CEFR 레벨: {skill_info.get('cefr_level')}")
