"""
DerDieDas.ai API 클라이언트

Streamlit 페이지에서 FastAPI 백엔드와 통신하기 위한 유틸리티
"""

import requests
from typing import Dict, List, Optional
import os


class APIClient:
    """FastAPI 백엔드 클라이언트"""

    def __init__(self, base_url: str = None):
        """
        Args:
            base_url: API 서버 주소 (기본값: http://localhost:8000)
        """
        if base_url is None:
            base_url = os.getenv("API_BASE_URL", "http://localhost:8000")

        self.base_url = base_url.rstrip("/")

    def _handle_response(self, response: requests.Response) -> Dict:
        """응답 처리 및 에러 핸들링"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = response.json().get("detail", str(e))
            raise Exception(f"API Error: {error_detail}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network Error: {str(e)}")

    # ========== 프로필 관리 ==========

    def get_profile(self) -> Dict:
        """사용자 프로필 조회"""
        response = requests.get(f"{self.base_url}/api/profile")
        return self._handle_response(response)

    def update_level(self, level: str, skill_proficiency: Dict[str, float] = None) -> Dict:
        """레벨 테스트 결과 업데이트"""
        params = {"level": level}
        if skill_proficiency:
            params["skill_proficiency"] = skill_proficiency

        response = requests.post(
            f"{self.base_url}/api/profile/update-level",
            json=params
        )
        return self._handle_response(response)

    # ========== 노트북 관리 ==========

    def get_notebooks(self) -> List[Dict]:
        """모든 노트북 조회"""
        response = requests.get(f"{self.base_url}/api/notebooks")
        return self._handle_response(response)

    def get_recommended_notebooks(self) -> List[Dict]:
        """추천 노트북만 조회"""
        response = requests.get(f"{self.base_url}/api/notebooks/recommended")
        return self._handle_response(response)

    def refresh_recommended_notebooks(self) -> Dict:
        """추천 노트북 갱신"""
        response = requests.post(f"{self.base_url}/api/notebooks/refresh-recommended")
        return self._handle_response(response)

    # ========== 학습 컨텐츠 생성 ==========

    def select_topic(
        self,
        user_proficiency: Dict[str, float],
        learning_count: Dict[str, int] = None,
        domain_filter: str = None
    ) -> Dict:
        """적응형 주제 선정"""
        payload = {
            "user_proficiency": user_proficiency,
            "learning_count": learning_count or {},
            "domain_filter": domain_filter
        }

        response = requests.post(
            f"{self.base_url}/api/learning/select-topic",
            json=payload
        )
        return self._handle_response(response)

    def generate_content(
        self,
        skill_id: str,
        skill_name: str,
        skill_description: str,
        user_cefr_level: str,
        user_interests: List[str] = None,
        user_goals: List[str] = None
    ) -> Dict:
        """학습 컨텐츠 생성 (GPT)"""
        payload = {
            "skill_id": skill_id,
            "skill_name": skill_name,
            "skill_description": skill_description,
            "user_cefr_level": user_cefr_level,
            "user_interests": user_interests or [],
            "user_goals": user_goals or []
        }

        response = requests.post(
            f"{self.base_url}/api/learning/generate-content",
            json=payload
        )
        return self._handle_response(response)

    def generate_writing_feedback(
        self,
        user_text: str,
        task_prompt: str,
        target_grammar: str,
        user_cefr_level: str
    ) -> Dict:
        """작문 피드백 생성 (GPT)"""
        payload = {
            "user_text": user_text,
            "task_prompt": task_prompt,
            "target_grammar": target_grammar,
            "user_cefr_level": user_cefr_level
        }

        response = requests.post(
            f"{self.base_url}/api/learning/writing-feedback",
            json=payload
        )
        return self._handle_response(response)

    def complete_learning(
        self,
        notebook_id: str,
        skill_proficiency: Dict[str, float] = None,
        learning_count_increment: str = None,
        stamps_increment: int = 0
    ) -> Dict:
        """학습 완료 처리 (통합 업데이트)"""
        payload = {
            "notebook_id": notebook_id,
            "skill_proficiency": skill_proficiency or {},
            "learning_count_increment": learning_count_increment,
            "stamps_increment": stamps_increment
        }

        response = requests.post(
            f"{self.base_url}/api/learning/complete",
            json=payload
        )
        return self._handle_response(response)

    # ========== 헬스 체크 ==========

    def health_check(self) -> Dict:
        """API 서버 상태 확인"""
        response = requests.get(f"{self.base_url}/health")
        return self._handle_response(response)

    def is_server_running(self) -> bool:
        """서버 실행 여부 확인"""
        try:
            self.health_check()
            return True
        except Exception:
            return False


# 싱글톤 인스턴스
_api_client = None


def get_api_client() -> APIClient:
    """API 클라이언트 싱글톤 반환"""
    global _api_client
    if _api_client is None:
        _api_client = APIClient()
    return _api_client


if __name__ == "__main__":
    # 테스트
    client = APIClient()

    print("=== API 서버 테스트 ===")

    # 1. 헬스 체크
    print("\n1. 헬스 체크:")
    try:
        health = client.health_check()
        print(f"✅ 서버 실행 중: {health}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        exit(1)

    # 2. 프로필 조회
    print("\n2. 프로필 조회:")
    try:
        profile = client.get_profile()
        print(f"✅ 닉네임: {profile['nickname']}")
        print(f"   레벨: {profile['level']}")
        print(f"   스탬프: {profile['total_stamps']}")
    except Exception as e:
        print(f"❌ 프로필 조회 실패: {e}")

    # 3. 노트북 조회
    print("\n3. 노트북 조회:")
    try:
        notebooks = client.get_notebooks()
        print(f"✅ 전체 노트북 수: {len(notebooks)}")

        recommended = client.get_recommended_notebooks()
        print(f"   추천 노트북 수: {len(recommended)}")
    except Exception as e:
        print(f"❌ 노트북 조회 실패: {e}")

    print("\n=== 테스트 완료 ===")
