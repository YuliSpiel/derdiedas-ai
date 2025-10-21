"""
사용자 프로필 및 노트북 데이터 모델
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json
from pathlib import Path


@dataclass
class UserProfile:
    """사용자 프로필"""

    nickname: str = "학습자"
    level: str = "미측정"  # 예: "B1-중반"
    total_stamps: int = 0
    consecutive_days: int = 0
    interests: List[str] = field(default_factory=lambda: ["여행", "음악", "IT"])
    goals: List[str] = field(default_factory=lambda: ["회화", "문법"])
    last_active: Optional[str] = None
    profile_icon: str = "🎓"
    profile_bg_color: str = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"  # 배경 그라디언트
    skill_proficiency: Dict[str, float] = field(default_factory=dict)  # 스킬별 숙련도 (0-100)
    skill_learning_count: Dict[str, int] = field(default_factory=dict)  # 스킬별 학습 횟수
    created_at: Optional[str] = None

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "nickname": self.nickname,
            "level": self.level,
            "total_stamps": self.total_stamps,
            "consecutive_days": self.consecutive_days,
            "interests": self.interests,
            "goals": self.goals,
            "last_active": self.last_active,
            "profile_icon": self.profile_icon,
            "profile_bg_color": self.profile_bg_color,
            "skill_proficiency": self.skill_proficiency,
            "skill_learning_count": self.skill_learning_count,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        """딕셔너리에서 생성"""
        return cls(
            nickname=data.get("nickname", "학습자"),
            level=data.get("level", "미측정"),
            total_stamps=data.get("total_stamps", 0),
            consecutive_days=data.get("consecutive_days", 0),
            interests=data.get("interests", ["여행", "음악", "IT"]),
            goals=data.get("goals", ["회화", "문법"]),
            last_active=data.get("last_active"),
            profile_icon=data.get("profile_icon", "🎓"),
            profile_bg_color=data.get("profile_bg_color", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"),
            skill_proficiency=data.get("skill_proficiency", {}),
            skill_learning_count=data.get("skill_learning_count", {}),
            created_at=data.get("created_at"),
        )


@dataclass
class Notebook:
    """학습 노트북"""

    id: str
    title: str  # 예: "Definite article – nominative"
    category: str  # "Grammar", "Expression" 등
    topic: str  # "Articles", "Verbs" 등
    total_sessions: int = 0
    last_studied: Optional[str] = None
    created_at: Optional[str] = None
    is_recommended: bool = False  # 추천 노트북 여부 (적응형 주제 선정)
    skill_id: Optional[str] = None  # 사용자 선택 스킬 ID (고정 주제)

    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "topic": self.topic,
            "total_sessions": self.total_sessions,
            "last_studied": self.last_studied,
            "created_at": self.created_at,
            "is_recommended": self.is_recommended,
            "skill_id": self.skill_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Notebook":
        """딕셔너리에서 생성"""
        return cls(
            id=data["id"],
            title=data["title"],
            category=data["category"],
            topic=data["topic"],
            total_sessions=data.get("total_sessions", 0),
            last_studied=data.get("last_studied"),
            created_at=data.get("created_at"),
            is_recommended=data.get("is_recommended", False),
            skill_id=data.get("skill_id"),
        )


class ProfileManager:
    """프로필 관리 클래스"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.profile_file = self.data_dir / "user_profile.json"
        self.notebooks_file = self.data_dir / "notebooks.json"

    def load_profile(self) -> UserProfile:
        """프로필 로드"""
        if self.profile_file.exists():
            with open(self.profile_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UserProfile.from_dict(data)
        else:
            # 기본 프로필 생성
            profile = UserProfile(created_at=datetime.now().isoformat())
            self.save_profile(profile)
            return profile

    def save_profile(self, profile: UserProfile):
        """프로필 저장"""
        profile.last_active = datetime.now().isoformat()
        with open(self.profile_file, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)

    def update_level_from_test(self, level: str, skill_proficiency: Dict[str, float] = None):
        """레벨 테스트 결과 반영 (레벨 + 스킬 숙련도)"""
        profile = self.load_profile()
        profile.level = level

        # 스킬 숙련도 업데이트
        if skill_proficiency:
            profile.skill_proficiency = skill_proficiency

        self.save_profile(profile)

    def load_notebooks(self) -> List[Notebook]:
        """노트북 목록 로드"""
        if self.notebooks_file.exists():
            with open(self.notebooks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Notebook.from_dict(nb) for nb in data]
        else:
            # 기본 노트북 생성
            default_notebooks = self._create_default_notebooks()
            self.save_notebooks(default_notebooks)
            return default_notebooks

    def save_notebooks(self, notebooks: List[Notebook]):
        """노트북 목록 저장"""
        with open(self.notebooks_file, "w", encoding="utf-8") as f:
            json.dump(
                [nb.to_dict() for nb in notebooks], f, ensure_ascii=False, indent=2
            )

    def add_notebook(self, notebook: Notebook):
        """노트북 추가"""
        notebooks = self.load_notebooks()
        notebooks.append(notebook)
        self.save_notebooks(notebooks)

    def delete_notebook(self, notebook_id: str):
        """노트북 삭제"""
        notebooks = self.load_notebooks()
        notebooks = [nb for nb in notebooks if nb.id != notebook_id]
        self.save_notebooks(notebooks)

    def update_notebook_session(self, notebook_id: str):
        """노트북 학습 세션 업데이트"""
        notebooks = self.load_notebooks()
        for nb in notebooks:
            if nb.id == notebook_id:
                nb.total_sessions += 1
                nb.last_studied = datetime.now().strftime("%m/%d")
                break
        self.save_notebooks(notebooks)

        # 프로필 스탬프도 증가
        profile = self.load_profile()
        profile.total_stamps += 1
        self.save_profile(profile)

    def _create_default_notebooks(self) -> List[Notebook]:
        """기본 노트북 생성 (추천용)"""
        # 스킬 데이터 기반 추천 노트북 생성
        try:
            from pathlib import Path
            import csv

            skill_tree_path = Path("data/grammar_ontology/skill_tree.csv")
            if skill_tree_path.exists():
                with open(skill_tree_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    skills = list(reader)

                # A1 레벨 스킬 중 일부를 추천 노트북으로 생성
                recommended_skills = [s for s in skills if s['cefr'] == 'A1'][:3]

                notebooks = []
                for skill in recommended_skills:
                    notebooks.append(Notebook(
                        id=f"nb_{skill['skill_id']}",
                        title=skill['name'],  # 스킬 이름을 타이틀로 직접 사용
                        category="Grammar",
                        topic=skill['area'],
                        is_recommended=True,
                        created_at=datetime.now().isoformat(),
                    ))

                return notebooks if notebooks else self._fallback_notebooks()
            else:
                return self._fallback_notebooks()
        except Exception as e:
            print(f"스킬 데이터 로드 실패: {e}")
            return self._fallback_notebooks()

    def _fallback_notebooks(self) -> List[Notebook]:
        """기본 노트북 (폴백)"""
        return [
            Notebook(
                id="nb_grammar_articles",
                title="Definite article – nominative",
                category="Grammar",
                topic="Articles",
                is_recommended=True,
                created_at=datetime.now().isoformat(),
            ),
            Notebook(
                id="nb_grammar_verbs",
                title="Present tense – regular verbs",
                category="Grammar",
                topic="Verbs",
                is_recommended=True,
                created_at=datetime.now().isoformat(),
            ),
        ]
