"""
문법 학습 온톨로지 데이터 모델

GPT가 생성한 온톨로지 데이터를 로드하고 관리하는 모듈
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path
import json


class CEFRLevel(Enum):
    """CEFR 레벨"""
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"


class DifficultyLevel(Enum):
    """난이도"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(Enum):
    """문제 유형"""
    MULTIPLE_CHOICE = "multiple_choice"
    FILL_IN_BLANK = "fill_in_blank"
    SENTENCE_BUILDING = "sentence_building"
    TRANSLATION = "translation"
    WRITING = "writing"


@dataclass
class Example:
    """예제 문장"""
    german: str
    korean: str
    english: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Exercise:
    """연습 문제"""
    id: str
    type: QuestionType
    difficulty: DifficultyLevel
    question: str
    options: Optional[List[str]] = None  # 객관식 선택지
    correct_answer: str = ""
    explanation: str = ""
    hints: List[str] = field(default_factory=list)


@dataclass
class CommonMistake:
    """흔한 실수"""
    mistake: str
    correction: str
    explanation: str


@dataclass
class GrammarRule:
    """문법 규칙"""
    title: str
    description: str
    examples: List[Example] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)


@dataclass
class GrammarTopic:
    """문법 주제 (온톨로지 기반)"""
    # 기본 정보
    id: str
    title_de: str
    title_ko: str
    title_en: str

    # 분류
    cefr_level: CEFRLevel
    category: str  # verbs, nouns, adjectives, etc.
    subcategory: str
    tags: List[str] = field(default_factory=list)

    # 학습 정보
    difficulty_score: float  # 1.0-5.0
    estimated_time: int  # 분
    prerequisites: List[str] = field(default_factory=list)  # topic IDs
    related_topics: List[str] = field(default_factory=list)

    # 콘텐츠
    summary: str = ""  # 요약 설명
    rules: List[GrammarRule] = field(default_factory=list)
    examples: List[Example] = field(default_factory=list)
    exercises: List[Exercise] = field(default_factory=list)
    common_mistakes: List[CommonMistake] = field(default_factory=list)

    # 메타데이터
    source: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class UserTopicProgress:
    """사용자 주제별 학습 진도"""
    user_id: str
    topic_id: str

    # 숙련도 점수
    proficiency_score: float = 0.0  # 0-100

    # 학습 통계
    total_attempts: int = 0
    exercises_completed: int = 0
    exercises_correct: int = 0

    # 퀴즈 결과
    quiz_scores: List[float] = field(default_factory=list)

    # 작문 샘플
    writing_samples: List[Dict] = field(default_factory=list)

    # 상태
    status: str = "not_started"  # not_started, learning, practicing, mastered

    # 시간
    first_studied: Optional[str] = None
    last_studied: Optional[str] = None
    total_study_time: int = 0  # 분


class GrammarOntologyLoader:
    """문법 온톨로지 로더"""

    def __init__(self, data_path: str = None):
        if data_path is None:
            project_root = Path(__file__).parent.parent.parent
            data_path = project_root / "data" / "grammar_ontology"

        self.data_path = Path(data_path)
        self.topics: Dict[str, GrammarTopic] = {}

    def load_all_topics(self) -> Dict[str, GrammarTopic]:
        """모든 주제 로드"""
        ontology_file = self.data_path / "grammar_ontology.json"

        if not ontology_file.exists():
            print(f"⚠️  온톨로지 파일을 찾을 수 없습니다: {ontology_file}")
            return {}

        with open(ontology_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # JSON을 GrammarTopic 객체로 변환
        for topic_data in data.get('topics', []):
            topic = self._parse_topic(topic_data)
            self.topics[topic.id] = topic

        print(f"✅ {len(self.topics)}개 주제 로드 완료")
        return self.topics

    def _parse_topic(self, data: Dict) -> GrammarTopic:
        """JSON 데이터를 GrammarTopic 객체로 변환"""
        # 기본 파싱
        topic = GrammarTopic(
            id=data['id'],
            title_de=data.get('title_de', ''),
            title_ko=data.get('title_ko', ''),
            title_en=data.get('title_en', ''),
            cefr_level=CEFRLevel(data.get('cefr_level', 'A1')),
            category=data.get('category', ''),
            subcategory=data.get('subcategory', ''),
            tags=data.get('tags', []),
            difficulty_score=data.get('difficulty_score', 2.5),
            estimated_time=data.get('estimated_time', 15),
            prerequisites=data.get('prerequisites', []),
            related_topics=data.get('related_topics', []),
            summary=data.get('summary', ''),
            source=data.get('source', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )

        # 문법 규칙 파싱
        for rule_data in data.get('rules', []):
            rule = GrammarRule(
                title=rule_data.get('title', ''),
                description=rule_data.get('description', ''),
                examples=[
                    Example(**ex) for ex in rule_data.get('examples', [])
                ],
                exceptions=rule_data.get('exceptions', [])
            )
            topic.rules.append(rule)

        # 예제 파싱
        for ex_data in data.get('examples', []):
            topic.examples.append(Example(**ex_data))

        # 연습 문제 파싱
        for ex_data in data.get('exercises', []):
            exercise = Exercise(
                id=ex_data['id'],
                type=QuestionType(ex_data['type']),
                difficulty=DifficultyLevel(ex_data.get('difficulty', 'medium')),
                question=ex_data['question'],
                options=ex_data.get('options'),
                correct_answer=ex_data.get('correct_answer', ''),
                explanation=ex_data.get('explanation', ''),
                hints=ex_data.get('hints', [])
            )
            topic.exercises.append(exercise)

        # 흔한 실수 파싱
        for mistake_data in data.get('common_mistakes', []):
            topic.common_mistakes.append(CommonMistake(**mistake_data))

        return topic

    def get_topic_by_id(self, topic_id: str) -> Optional[GrammarTopic]:
        """ID로 주제 조회"""
        return self.topics.get(topic_id)

    def get_topics_by_level(self, level: CEFRLevel) -> List[GrammarTopic]:
        """레벨별 주제 조회"""
        return [t for t in self.topics.values() if t.cefr_level == level]

    def get_topics_by_category(self, category: str) -> List[GrammarTopic]:
        """카테고리별 주제 조회"""
        return [t for t in self.topics.values() if t.category == category]

    def get_recommended_topics(
        self,
        user_level: CEFRLevel,
        user_progress: Dict[str, UserTopicProgress],
        limit: int = 5
    ) -> List[GrammarTopic]:
        """
        사용자 레벨과 진도에 맞는 추천 주제

        추천 로직:
        1. 사용자 레벨에 맞는 주제 필터링
        2. 선행 학습 완료 확인
        3. 미학습 또는 숙련도 낮은 주제 우선
        4. 난이도순 정렬
        """
        # 레벨에 맞는 주제
        suitable_topics = self.get_topics_by_level(user_level)

        recommendations = []

        for topic in suitable_topics:
            # 이미 마스터한 주제는 제외
            progress = user_progress.get(topic.id)
            if progress and progress.status == "mastered":
                continue

            # 선행 학습 확인
            prerequisites_met = all(
                user_progress.get(prereq_id, UserTopicProgress("", "")).status in ["practicing", "mastered"]
                for prereq_id in topic.prerequisites
            )

            if prerequisites_met:
                recommendations.append(topic)

        # 난이도순 정렬
        recommendations.sort(key=lambda t: t.difficulty_score)

        return recommendations[:limit]


class UserProgressManager:
    """사용자 진도 관리"""

    def __init__(self, user_id: str, data_path: str = None):
        self.user_id = user_id

        if data_path is None:
            project_root = Path(__file__).parent.parent.parent
            data_path = project_root / "data" / "user_progress"

        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)

        self.progress_file = self.data_path / f"{user_id}_grammar_progress.json"
        self.progress: Dict[str, UserTopicProgress] = {}

        self.load_progress()

    def load_progress(self):
        """진도 로드"""
        if not self.progress_file.exists():
            return

        with open(self.progress_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for topic_id, progress_data in data.items():
            self.progress[topic_id] = UserTopicProgress(**progress_data)

    def save_progress(self):
        """진도 저장"""
        data = {
            topic_id: {
                'user_id': p.user_id,
                'topic_id': p.topic_id,
                'proficiency_score': p.proficiency_score,
                'total_attempts': p.total_attempts,
                'exercises_completed': p.exercises_completed,
                'exercises_correct': p.exercises_correct,
                'quiz_scores': p.quiz_scores,
                'writing_samples': p.writing_samples,
                'status': p.status,
                'first_studied': p.first_studied,
                'last_studied': p.last_studied,
                'total_study_time': p.total_study_time
            }
            for topic_id, p in self.progress.items()
        }

        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update_quiz_result(self, topic_id: str, score: float):
        """퀴즈 결과 업데이트"""
        if topic_id not in self.progress:
            self.progress[topic_id] = UserTopicProgress(
                user_id=self.user_id,
                topic_id=topic_id
            )

        progress = self.progress[topic_id]
        progress.quiz_scores.append(score)
        progress.total_attempts += 1

        # 숙련도 계산 (최근 3개 점수 평균)
        recent_scores = progress.quiz_scores[-3:]
        progress.proficiency_score = sum(recent_scores) / len(recent_scores)

        # 상태 업데이트
        if progress.proficiency_score >= 80:
            progress.status = "mastered"
        elif progress.proficiency_score >= 50:
            progress.status = "practicing"
        else:
            progress.status = "learning"

        self.save_progress()

    def get_weak_topics(self, min_attempts: int = 1) -> List[str]:
        """약점 주제 반환 (숙련도 낮은 주제)"""
        weak_topics = [
            topic_id
            for topic_id, p in self.progress.items()
            if p.total_attempts >= min_attempts and p.proficiency_score < 70
        ]

        # 숙련도 낮은 순으로 정렬
        weak_topics.sort(key=lambda tid: self.progress[tid].proficiency_score)

        return weak_topics


# 사용 예시
if __name__ == "__main__":
    # 온톨로지 로드
    loader = GrammarOntologyLoader()
    topics = loader.load_all_topics()

    print(f"총 {len(topics)}개 주제 로드됨")

    # 샘플 주제 확인
    if topics:
        sample = list(topics.values())[0]
        print(f"\n샘플 주제: {sample.title_ko}")
        print(f"레벨: {sample.cefr_level.value}")
        print(f"카테고리: {sample.category}")
        print(f"연습 문제 수: {len(sample.exercises)}개")
