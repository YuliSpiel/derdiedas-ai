"""
학습 사이클 데이터 모델

노트북 기반 학습 사이클:
1. 개념 설명 (Concept Explanation)
2. 퀴즈 (Quiz) - 적응형 재시도 로직
3. 작문 과제 (Writing Task)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class QuizQuestionType(Enum):
    """퀴즈 문제 유형"""
    FILL_BLANK = "fill_blank"  # 빈칸 채우기
    MULTIPLE_CHOICE = "multiple_choice"  # 객관식
    TRUE_FALSE = "true_false"  # 참/거짓
    MATCHING = "matching"  # 짝 맞추기


class LearningStage(Enum):
    """학습 사이클 단계"""
    CONCEPT = "concept"  # 개념 설명
    QUIZ = "quiz"  # 퀴즈
    MINI_REVIEW = "mini_review"  # 미니 복습 (40-60% 정답률)
    WRITING = "writing"  # 작문
    COMPLETED = "completed"  # 완료


@dataclass
class ConceptExplanation:
    """개념 설명 컨텐츠"""
    title_de: str  # 독일어 제목
    title_ko: str  # 한국어 제목
    explanation: str  # 설명 (한국어)
    examples: List[Dict[str, str]]  # [{"de": "...", "ko": "..."}]
    skill_ids: List[str] = field(default_factory=list)  # 관련 스킬 ID


@dataclass
class QuizQuestion:
    """퀴즈 문제"""
    id: str
    type: QuizQuestionType
    question: str  # 문제 텍스트
    options: List[str] = field(default_factory=list)  # 선택지 (객관식인 경우)
    correct_answer: str = ""  # 정답
    explanation: str = ""  # 해설
    skill_id: Optional[str] = None  # 관련 스킬


@dataclass
class QuizResult:
    """퀴즈 결과"""
    total_questions: int
    correct_answers: int
    score_percentage: float
    wrong_question_ids: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WritingTask:
    """작문 과제"""
    prompt_de: str  # 독일어 프롬프트
    prompt_ko: str  # 한국어 프롬프트
    min_sentences: int = 3  # 최소 문장 수
    target_skills: List[str] = field(default_factory=list)  # 목표 스킬


@dataclass
class WritingFeedback:
    """작문 피드백"""
    user_text: str
    grammar_score: int  # 0-5
    vocabulary_score: int  # 0-5
    task_completion_score: int  # 0-5
    corrections: List[Dict[str, str]] = field(default_factory=list)  # [{"original": "...", "corrected": "...", "explanation": "..."}]
    positive_feedback: List[str] = field(default_factory=list)
    improvement_tips: List[str] = field(default_factory=list)
    skill_updates: Dict[str, float] = field(default_factory=dict)  # {skill_id: proficiency_change}


@dataclass
class LearningSession:
    """학습 세션 (하나의 사이클)"""
    session_id: str
    notebook_id: str
    topic: str  # 학습 주제
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # 학습 컨텐츠
    concept: Optional[ConceptExplanation] = None
    quiz_questions: List[QuizQuestion] = field(default_factory=list)
    writing_task: Optional[WritingTask] = None

    # 진행 상태
    current_stage: LearningStage = LearningStage.CONCEPT
    quiz_result: Optional[QuizResult] = None
    mini_review_questions: List[QuizQuestion] = field(default_factory=list)
    mini_review_result: Optional[QuizResult] = None
    writing_feedback: Optional[WritingFeedback] = None

    # 완료 여부
    is_completed: bool = False
    completed_at: Optional[str] = None
    stamp_awarded: bool = False

    def get_progress_percentage(self) -> float:
        """진행률 계산"""
        stages_completed = 0
        total_stages = 4  # concept, quiz, (mini_review), writing

        if self.current_stage.value in ["quiz", "mini_review", "writing", "completed"]:
            stages_completed += 1  # concept 완료

        if self.quiz_result is not None:
            stages_completed += 1  # quiz 완료

        if self.mini_review_result is not None:
            stages_completed += 0.5  # mini review (선택적)

        if self.writing_feedback is not None:
            stages_completed += 1  # writing 완료

        if self.is_completed:
            stages_completed = total_stages

        return min(100, (stages_completed / total_stages) * 100)

    def should_do_mini_review(self) -> bool:
        """미니 복습 필요 여부 (40-60% 정답률)"""
        if self.quiz_result is None:
            return False
        return 40 <= self.quiz_result.score_percentage < 60

    def should_retry_concept(self) -> bool:
        """개념 재학습 필요 여부 (<40% 정답률)"""
        if self.quiz_result is None:
            return False
        return self.quiz_result.score_percentage < 40

    def complete_session(self):
        """세션 완료 처리"""
        self.is_completed = True
        self.completed_at = datetime.now().isoformat()
        self.current_stage = LearningStage.COMPLETED
        self.stamp_awarded = True


@dataclass
class NotebookMetadata:
    """노트북 메타데이터 (확장)"""
    notebook_id: str
    title: str
    domain: str  # "표현" or "문법"
    topic: str  # "여행-숙소 체크인", "현재완료 (Perfekt)" 등
    created_at: str

    # 자료 업로드 방식
    has_user_materials: bool = False  # 사용자 자료 업로드 여부
    material_urls: List[str] = field(default_factory=list)

    # AI 자동 생성 방식
    auto_generated: bool = False  # AI 자동 구성 여부
    target_cefr_level: Optional[str] = None  # 목표 레벨
    target_skills: List[str] = field(default_factory=list)  # 목표 스킬

    # 학습 세션들
    sessions: List[str] = field(default_factory=list)  # session_id 리스트
    total_sessions_completed: int = 0

    # 진행 상태
    is_active: bool = True
    last_accessed: Optional[str] = None


if __name__ == "__main__":
    # 테스트
    session = LearningSession(
        session_id="test-001",
        notebook_id="notebook-001",
        topic="현재완료 (Perfekt)"
    )

    print(f"세션 ID: {session.session_id}")
    print(f"현재 단계: {session.current_stage.value}")
    print(f"진행률: {session.get_progress_percentage():.1f}%")

    # 퀴즈 결과 시뮬레이션
    session.quiz_result = QuizResult(
        total_questions=5,
        correct_answers=2,
        score_percentage=40.0
    )

    print(f"미니 복습 필요: {session.should_do_mini_review()}")
    print(f"개념 재학습 필요: {session.should_retry_concept()}")
