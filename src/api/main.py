"""
DerDieDas.ai FastAPI 백엔드

기존 Streamlit 프론트엔드에서 직접 호출하던 로직들을 API 엔드포인트로 분리
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sys
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from models import ProfileManager, UserProfile
from learning.topic_selector import TopicSelector
from learning.content_generator import LearningContentGenerator
from learning.writing_feedback import WritingFeedbackGenerator

# FastAPI 앱 생성
app = FastAPI(
    title="DerDieDas.ai API",
    description="독일어 학습 플랫폼 백엔드 API",
    version="1.0.0"
)

# CORS 설정 (Streamlit에서 호출 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request/Response 모델
# =============================================================================

class TopicSelectionRequest(BaseModel):
    user_proficiency: Dict[str, float]
    learning_count: Dict[str, int]
    domain_filter: str = "Grammar"


class ContentGenerationRequest(BaseModel):
    skill_id: str
    skill_name: str
    skill_description: str
    user_cefr_level: str = "A2"
    user_interests: List[str] = []
    user_goals: List[str] = []


class WritingFeedbackRequest(BaseModel):
    user_text: str
    task_prompt: str
    target_grammar: str
    user_cefr_level: str = "A2"


class NotebookUpdateRequest(BaseModel):
    notebook_id: str
    skill_proficiency: Optional[Dict[str, float]] = None
    learning_count_increment: Optional[str] = None
    stamps_increment: int = 0


# =============================================================================
# 엔드포인트
# =============================================================================

@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "status": "online",
        "message": "DerDieDas.ai API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


# -----------------------------------------------------------------------------
# 프로필 관리
# -----------------------------------------------------------------------------

@app.get("/api/profile")
async def get_profile():
    """사용자 프로필 조회"""
    try:
        profile_manager = ProfileManager()
        profile = profile_manager.load_profile()
        return profile.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class UpdateLevelRequest(BaseModel):
    level: str
    skill_proficiency: Optional[Dict[str, float]] = None


@app.post("/api/profile/update-level")
async def update_level(request: UpdateLevelRequest):
    """레벨 테스트 결과 업데이트"""
    try:
        # 디버깅 로그
        print(f"\n📊 레벨 업데이트 요청:")
        print(f"   레벨: {request.level}")
        print(f"   스킬 숙련도: {request.skill_proficiency}")
        if request.skill_proficiency:
            print(f"   스킬 개수: {len(request.skill_proficiency)}")
        else:
            print(f"   ⚠️ 스킬 숙련도 데이터 없음!")

        profile_manager = ProfileManager()
        profile_manager.update_level_from_test(request.level, request.skill_proficiency)
        return {"success": True, "level": request.level, "skill_count": len(request.skill_proficiency) if request.skill_proficiency else 0}
    except Exception as e:
        print(f"❌ 레벨 업데이트 에러: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# 노트북 관리
# -----------------------------------------------------------------------------

@app.get("/api/notebooks")
async def get_notebooks():
    """모든 노트북 조회"""
    try:
        profile_manager = ProfileManager()
        notebooks = profile_manager.load_notebooks()
        return [nb.to_dict() for nb in notebooks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notebooks/recommended")
async def get_recommended_notebooks():
    """추천 노트북만 조회"""
    try:
        profile_manager = ProfileManager()
        notebooks = profile_manager.load_notebooks()
        recommended = [nb.to_dict() for nb in notebooks if nb.is_recommended]
        return recommended
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/notebooks/refresh-recommended")
async def refresh_recommended_notebooks():
    """추천 노트북 갱신"""
    try:
        profile_manager = ProfileManager()
        profile_manager.refresh_recommended_notebooks()
        return {"success": True, "message": "Recommended notebooks refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------------------------------
# 학습 컨텐츠 생성
# -----------------------------------------------------------------------------

@app.post("/api/learning/select-topic")
async def select_topic(request: TopicSelectionRequest):
    """적응형 주제 선정"""
    try:
        selector = TopicSelector()
        selected_skill = selector.select_topic(
            user_proficiency=request.user_proficiency,
            learning_count=request.learning_count,
            domain_filter=request.domain_filter
        )

        if not selected_skill:
            raise HTTPException(status_code=404, detail="No suitable topic found")

        skill_info = selector.get_skill_info(selected_skill)
        return {
            "skill_id": selected_skill,
            "skill_info": skill_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/learning/generate-content")
async def generate_content(request: ContentGenerationRequest):
    """학습 컨텐츠 생성 (GPT)"""
    try:
        generator = LearningContentGenerator()
        content = generator.generate_content(
            skill_id=request.skill_id,
            skill_name=request.skill_name,
            skill_description=request.skill_description,
            user_cefr_level=request.user_cefr_level,
            user_interests=request.user_interests,
            user_goals=request.user_goals
        )
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/learning/writing-feedback")
async def generate_writing_feedback(request: WritingFeedbackRequest):
    """작문 피드백 생성 (GPT)"""
    try:
        generator = WritingFeedbackGenerator()
        feedback = generator.generate_feedback(
            user_text=request.user_text,
            task_prompt=request.task_prompt,
            target_grammar=request.target_grammar,
            user_cefr_level=request.user_cefr_level
        )
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/learning/complete")
async def complete_learning(request: NotebookUpdateRequest):
    """학습 완료 처리 (숙련도, 스탬프, 카운트 업데이트)"""
    try:
        profile_manager = ProfileManager()
        profile = profile_manager.load_profile()

        # 스킬 숙련도 업데이트
        if request.skill_proficiency:
            for skill_id, proficiency in request.skill_proficiency.items():
                profile.skill_proficiency[skill_id] = proficiency

        # 학습 횟수 증가
        if request.learning_count_increment:
            skill_id = request.learning_count_increment
            if skill_id not in profile.skill_learning_count:
                profile.skill_learning_count[skill_id] = 0
            profile.skill_learning_count[skill_id] += 1

        # 스탬프 증가
        if request.stamps_increment > 0:
            profile.total_stamps += request.stamps_increment

        profile_manager.save_profile(profile)

        # 노트북 세션 업데이트
        if request.notebook_id:
            profile_manager.update_notebook_session(request.notebook_id)

        # 추천 노트북 갱신
        if request.skill_proficiency:
            profile_manager.refresh_recommended_notebooks()

        return {
            "success": True,
            "message": "Learning completed successfully",
            "updated_stamps": profile.total_stamps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 서버 실행 (개발용)
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
