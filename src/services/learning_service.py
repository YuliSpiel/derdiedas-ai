"""
학습 서비스 레이어

API 우선 + 직접 호출 폴백 방식
- API 서버가 실행 중이면 API 사용
- API 서버가 없으면 직접 함수 호출
"""

from typing import Dict, List, Optional
from src.utils.api_client import get_api_client
from src.learning.topic_selector import TopicSelector
from src.learning.content_generator import LearningContentGenerator
from src.learning.writing_feedback import WritingFeedbackGenerator
from src.models.user_profile import ProfileManager


class LearningService:
    """학습 관련 서비스 (API 우선 + 폴백)"""

    def __init__(self, use_api: bool = True):
        """
        Args:
            use_api: API 사용 여부 (기본값: True, 자동 폴백)
        """
        self.use_api = use_api
        self.api_client = get_api_client() if use_api else None

        # 폴백용 직접 호출 객체
        self.topic_selector = TopicSelector()
        self.content_generator = LearningContentGenerator()
        self.feedback_generator = WritingFeedbackGenerator()
        self.profile_manager = ProfileManager()

        # API 서버 상태 확인
        if self.use_api:
            self.api_available = self.api_client.is_server_running()
            if not self.api_available:
                print("⚠️ API 서버가 실행 중이 아닙니다. 직접 호출 모드로 전환합니다.")
        else:
            self.api_available = False

    def _should_use_api(self) -> bool:
        """API 사용 여부 판단"""
        return self.use_api and self.api_available

    # ========== 주제 선정 ==========

    def select_topic(
        self,
        user_proficiency: Dict[str, float],
        learning_count: Dict[str, int] = None,
        domain_filter: str = None
    ) -> Optional[Dict]:
        """
        적응형 주제 선정

        Returns:
            {"skill_id": str, "skill_info": {...}}
        """
        if self._should_use_api():
            try:
                result = self.api_client.select_topic(
                    user_proficiency=user_proficiency,
                    learning_count=learning_count,
                    domain_filter=domain_filter
                )
                return result
            except Exception as e:
                print(f"⚠️ API 호출 실패, 직접 호출로 폴백: {e}")
                self.api_available = False

        # 직접 호출 폴백
        skill_id = self.topic_selector.select_topic(
            user_proficiency=user_proficiency,
            learning_count=learning_count,
            domain_filter=domain_filter
        )

        if skill_id:
            skill_info = self.topic_selector.get_skill_info(skill_id)
            return {
                "skill_id": skill_id,
                "skill_info": {
                    "name": skill_info.get("name", ""),
                    "area": skill_info.get("category", ""),
                    "cefr": skill_info.get("cefr_level", ""),
                    "hint": skill_info.get("hint", "")
                }
            }
        return None

    # ========== 컨텐츠 생성 ==========

    def generate_content(
        self,
        skill_id: str,
        skill_name: str,
        skill_description: str,
        user_cefr_level: str,
        user_interests: List[str] = None,
        user_goals: List[str] = None
    ) -> Dict:
        """
        학습 컨텐츠 생성 (GPT)

        Returns:
            {
                "concept_de": str,
                "concept_ko": str,
                "examples": [...],
                "quiz_questions": [...],
                "writing_task": {...}
            }
        """
        if self._should_use_api():
            try:
                result = self.api_client.generate_content(
                    skill_id=skill_id,
                    skill_name=skill_name,
                    skill_description=skill_description,
                    user_cefr_level=user_cefr_level,
                    user_interests=user_interests,
                    user_goals=user_goals
                )
                return result
            except Exception as e:
                print(f"⚠️ API 호출 실패, 직접 호출로 폴백: {e}")
                self.api_available = False

        # 직접 호출 폴백
        return self.content_generator.generate_content(
            skill_id=skill_id,
            skill_name=skill_name,
            skill_description=skill_description,
            user_cefr_level=user_cefr_level,
            user_interests=user_interests,
            user_goals=user_goals
        )

    # ========== 작문 피드백 ==========

    def generate_writing_feedback(
        self,
        user_text: str,
        task_prompt: str,
        target_grammar: str,
        user_cefr_level: str
    ) -> Dict:
        """
        작문 피드백 생성 (GPT)

        Returns:
            {
                "grammar_score": int,
                "vocabulary_score": int,
                "task_completion_score": int,
                "corrections": [...],
                "positive_feedback": [...],
                "improvement_tips": [...],
                "skill_proficiency_change": float
            }
        """
        if self._should_use_api():
            try:
                result = self.api_client.generate_writing_feedback(
                    user_text=user_text,
                    task_prompt=task_prompt,
                    target_grammar=target_grammar,
                    user_cefr_level=user_cefr_level
                )
                return result
            except Exception as e:
                print(f"⚠️ API 호출 실패, 직접 호출로 폴백: {e}")
                self.api_available = False

        # 직접 호출 폴백
        return self.feedback_generator.generate_feedback(
            user_text=user_text,
            task_prompt=task_prompt,
            target_grammar=target_grammar,
            user_cefr_level=user_cefr_level
        )

    # ========== 학습 완료 ==========

    def complete_learning(
        self,
        notebook_id: str,
        skill_proficiency: Dict[str, float] = None,
        learning_count_increment: str = None,
        stamps_increment: int = 0
    ) -> Dict:
        """
        학습 완료 처리

        Returns:
            {"success": bool, "message": str, "updated_stamps": int}
        """
        if self._should_use_api():
            try:
                result = self.api_client.complete_learning(
                    notebook_id=notebook_id,
                    skill_proficiency=skill_proficiency,
                    learning_count_increment=learning_count_increment,
                    stamps_increment=stamps_increment
                )
                return result
            except Exception as e:
                print(f"⚠️ API 호출 실패, 직접 호출로 폴백: {e}")
                self.api_available = False

        # 직접 호출 폴백
        profile = self.profile_manager.load_profile()

        # 스킬 숙련도 업데이트
        if skill_proficiency:
            for skill_id, proficiency in skill_proficiency.items():
                profile.skill_proficiency[skill_id] = proficiency

        # 학습 횟수 증가
        if learning_count_increment:
            current_count = profile.skill_learning_count.get(learning_count_increment, 0)
            profile.skill_learning_count[learning_count_increment] = current_count + 1

        # 스탬프 증가
        profile.total_stamps += stamps_increment

        # 노트북 업데이트
        notebooks = self.profile_manager.load_notebooks()
        for nb in notebooks:
            if nb.id == notebook_id:
                nb.total_sessions += 1
                from datetime import datetime
                nb.last_studied = datetime.now().strftime("%m/%d")

                # 추천 노트북을 일반 노트북으로 변환
                if nb.is_recommended:
                    nb.is_recommended = False
                    if learning_count_increment:
                        nb.skill_id = learning_count_increment
                break

        # 저장
        self.profile_manager.save_profile(profile)
        self.profile_manager.save_notebooks(notebooks)

        # 추천 노트북 갱신
        self.profile_manager.refresh_recommended_notebooks()

        return {
            "success": True,
            "message": "Learning completed successfully",
            "updated_stamps": profile.total_stamps
        }

    # ========== 프로필 관리 ==========

    def get_profile(self) -> Dict:
        """프로필 조회"""
        if self._should_use_api():
            try:
                return self.api_client.get_profile()
            except Exception as e:
                print(f"⚠️ API 호출 실패, 직접 호출로 폴백: {e}")
                self.api_available = False

        # 직접 호출 폴백
        profile = self.profile_manager.load_profile()
        return profile.to_dict()

    def get_notebooks(self) -> List[Dict]:
        """노트북 조회"""
        if self._should_use_api():
            try:
                return self.api_client.get_notebooks()
            except Exception as e:
                print(f"⚠️ API 호출 실패, 직접 호출로 폴백: {e}")
                self.api_available = False

        # 직접 호출 폴백
        notebooks = self.profile_manager.load_notebooks()
        return [nb.to_dict() for nb in notebooks]

    def refresh_recommended_notebooks(self) -> Dict:
        """추천 노트북 갱신"""
        if self._should_use_api():
            try:
                return self.api_client.refresh_recommended_notebooks()
            except Exception as e:
                print(f"⚠️ API 호출 실패, 직접 호출로 폴백: {e}")
                self.api_available = False

        # 직접 호출 폴백
        self.profile_manager.refresh_recommended_notebooks()
        return {"success": True, "message": "Recommended notebooks refreshed"}


# 싱글톤 인스턴스
_learning_service = None


def get_learning_service(use_api: bool = True) -> LearningService:
    """학습 서비스 싱글톤 반환"""
    global _learning_service
    if _learning_service is None:
        _learning_service = LearningService(use_api=use_api)
    return _learning_service


if __name__ == "__main__":
    # 테스트
    service = LearningService(use_api=True)

    print("=== 학습 서비스 테스트 ===")
    print(f"API 사용 가능: {service.api_available}\n")

    # 프로필 조회
    print("1. 프로필 조회:")
    profile = service.get_profile()
    print(f"   닉네임: {profile['nickname']}")
    print(f"   레벨: {profile['level']}")

    # 노트북 조회
    print("\n2. 노트북 조회:")
    notebooks = service.get_notebooks()
    print(f"   노트북 수: {len(notebooks)}")

    print("\n=== 테스트 완료 ===")
