"""
DerDieDas.ai - 독일어 학습 플랫폼

메인 진입점
"""

import streamlit as st
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트 설정
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

# 환경 변수 로드
env_file = project_root / "config" / ".env"
if env_file.exists():
    load_dotenv(env_file)

# 페이지 설정
st.set_page_config(
    page_title="DerDieDas.ai",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 메인 페이지 (홈/대시보드)
from models import UserProfile, Notebook, ProfileManager

# 커스텀 CSS
st.markdown(
    """
<style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 3rem;
    }
    .welcome-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        text-align: center;
    }
    .feature-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 2rem;
        margin: 1rem 0;
        background: white;
        transition: all 0.3s;
    }
    .feature-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
</style>
""",
    unsafe_allow_html=True,
)

# 헤더
st.markdown('<h1 class="main-title">🇩🇪 DerDieDas.ai</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI 기반 독일어 학습 플랫폼</p>', unsafe_allow_html=True)

# 프로필 로드
profile_manager = ProfileManager()
profile = profile_manager.load_profile()

# 환영 카드
st.markdown(
    f"""
<div class="welcome-card">
    <h2>안녕하세요, {profile.nickname}님! {profile.profile_icon}</h2>
    <p style="font-size: 1.1rem; margin-top: 1rem;">
        현재 레벨: <strong>{profile.level}</strong> |
        연속 학습: <strong>{profile.consecutive_days}일</strong> |
        스탬프: <strong>{profile.total_stamps}개</strong>
    </p>
</div>
""",
    unsafe_allow_html=True,
)

# 주요 기능 안내
st.markdown("## 🎯 주요 기능")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
    <div class="feature-card">
        <h3>📊 레벨 테스트</h3>
        <p>5개의 작문 문제로 당신의 독일어 실력을 정확하게 측정합니다.</p>
        <ul style="text-align: left;">
            <li>CEFR 기반 평가 (A2-C1)</li>
            <li>적응형 질문 시스템</li>
            <li>AI 기반 상세 피드백</li>
            <li>세부 레벨 측정 (초반/중반/후반)</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
    <div class="feature-card">
        <h3>📚 학습 대시보드</h3>
        <p>당신만의 학습 노트북을 만들고 관리하세요.</p>
        <ul style="text-align: left;">
            <li>프로필 및 학습 목표 관리</li>
            <li>맞춤형 학습 노트북</li>
            <li>학습 통계 및 진척도</li>
            <li>AI 추천 학습 컨텐츠</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# 빠른 시작
st.markdown("## 🚀 빠른 시작")

col1, col2, col3 = st.columns(3)

with col1:
    if profile.level == "미측정":
        st.info("👈 왼쪽 사이드바에서 **📊 레벨 테스트**를 선택하여 시작하세요!")
    else:
        st.success(f"현재 레벨: **{profile.level}**")

with col2:
    notebooks = profile_manager.load_notebooks()
    user_notebooks = [nb for nb in notebooks if not nb.is_recommended]
    st.metric("내 노트북", f"{len(user_notebooks)}개")

with col3:
    st.metric("누적 스탬프", f"{profile.total_stamps}개")

# 푸터
st.markdown("---")
st.markdown(
    """
<div style="text-align: center; color: #999; padding: 1rem;">
    <p>🇩🇪 DerDieDas.ai - AI 기반 독일어 학습 플랫폼</p>
    <p>궁금한 점이 있으시면 사이드바의 메뉴를 이용해주세요.</p>
</div>
""",
    unsafe_allow_html=True,
)
