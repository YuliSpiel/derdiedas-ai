"""
DerDieDas.ai 온보딩 (첫 이용자 프로필 설정)

2단계 온보딩 플로우:
1. 닉네임 + 프로필 아이콘 설정
2. 관심사 + 학습 목표 설정
3. 완료 후 자동으로 레벨 테스트로 이동
"""

import streamlit as st
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from models import UserProfile, ProfileManager

# 테스트 모드 임포트 (프로덕션 배포 시 삭제)
from utils.test_mode import render_test_sidebar

# =============================================================================
# 페이지 설정
# =============================================================================

st.set_page_config(
    page_title="DerDieDas.ai - 환영합니다",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# 커스텀 CSS
st.markdown(
    """
<style>
    /* 사이드바 완전히 숨기기 */
    [data-testid="stSidebar"] {
        display: none;
    }

    .onboarding-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .step-indicator {
        text-align: center;
        margin: 2rem 0;
        font-size: 1rem;
        color: #666;
    }

    .step-dot {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #ddd;
        margin: 0 0.5rem;
    }

    .step-dot.active {
        background: #667eea;
        width: 16px;
        height: 16px;
    }

    .icon-selector {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }

    .icon-option {
        font-size: 3rem;
        cursor: pointer;
        padding: 1rem;
        border: 3px solid transparent;
        border-radius: 10px;
        transition: all 0.3s;
    }

    .icon-option:hover {
        background: #f5f5f5;
        transform: scale(1.1);
    }

    .icon-option.selected {
        border-color: #667eea;
        background: #e8eaf6;
    }

    .welcome-message {
        text-align: center;
        font-size: 1.2rem;
        color: #333;
        margin: 2rem 0;
        line-height: 1.8;
    }

    .form-section {
        background: #f9f9f9;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .section-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 세션 상태 초기화
# =============================================================================


def init_session_state():
    """세션 상태 초기화"""
    if "profile_manager" not in st.session_state:
        st.session_state.profile_manager = ProfileManager()
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 1
    if "onboarding_data" not in st.session_state:
        st.session_state.onboarding_data = {
            "nickname": "",
            "icon": "🎓",
            "interests": [],
            "goals": [],
        }


# =============================================================================
# 단계 인디케이터
# =============================================================================


def show_step_indicator(current_step: int, total_steps: int = 2):
    """단계 인디케이터 표시"""
    dots = ""
    for i in range(1, total_steps + 1):
        dot_class = "step-dot active" if i == current_step else "step-dot"
        dots += f'<span class="{dot_class}"></span>'

    st.markdown(
        f"""
    <div class="step-indicator">
        {dots}
        <br>
        <span style="font-weight: bold;">Step {current_step} / {total_steps}</span>
    </div>
    """,
        unsafe_allow_html=True,
    )


# =============================================================================
# Step 1: 닉네임 + 아이콘
# =============================================================================


def show_step1():
    """Step 1: 닉네임과 프로필 아이콘 설정"""
    st.markdown('<h1 class="onboarding-header">🇩🇪 DerDieDas.ai</h1>', unsafe_allow_html=True)
    show_step_indicator(1)

    st.markdown(
        """
    <div class="welcome-message">
        <strong>환영합니다!</strong><br>
        독일어 학습을 시작하기 전에<br>
        간단한 프로필을 설정해주세요.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">닉네임 설정</div>', unsafe_allow_html=True)

    nickname = st.text_input(
        "닉네임을 입력해주세요",
        value=st.session_state.onboarding_data["nickname"],
        placeholder="예: 독일어왕",
        label_visibility="collapsed",
        key="nickname_input",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # 아이콘 선택
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">프로필 아이콘 선택</div>', unsafe_allow_html=True)

    icons = ["🎓", "📚", "✏️", "🌟", "🚀", "💡", "🎯", "🔥"]
    selected_icon = st.session_state.onboarding_data["icon"]

    # 아이콘 선택 UI
    cols = st.columns(4)
    for idx, icon in enumerate(icons):
        with cols[idx % 4]:
            if st.button(
                icon,
                key=f"icon_{idx}",
                use_container_width=True,
                type="primary" if icon == selected_icon else "secondary",
            ):
                st.session_state.onboarding_data["icon"] = icon
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # 다음 버튼
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("다음 ➡️", use_container_width=True, type="primary", disabled=not nickname.strip()):
            st.session_state.onboarding_data["nickname"] = nickname.strip()
            st.session_state.onboarding_step = 2
            st.rerun()

    if not nickname.strip():
        st.caption("💡 닉네임을 입력하면 다음 단계로 넘어갈 수 있습니다.")


# =============================================================================
# Step 2: 관심사 + 학습 목표
# =============================================================================


def show_step2():
    """Step 2: 관심사와 학습 목표 설정"""
    st.markdown('<h1 class="onboarding-header">🇩🇪 DerDieDas.ai</h1>', unsafe_allow_html=True)
    show_step_indicator(2)

    nickname = st.session_state.onboarding_data["nickname"]
    icon = st.session_state.onboarding_data["icon"]

    st.markdown(
        f"""
    <div class="welcome-message">
        {icon} <strong>{nickname}</strong>님,<br>
        맞춤 학습을 위해<br>
        관심사와 학습 목표를 알려주세요!
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 관심사 선택
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">관심사 선택</div>', unsafe_allow_html=True)
    st.caption("학습 예문을 관심사에 맞춰 제공해드립니다.")

    interest_options = [
        "여행",
        "음악",
        "IT",
        "요리",
        "스포츠",
        "영화",
        "독서",
        "미술",
        "패션",
        "비즈니스",
    ]

    interests = st.multiselect(
        "관심사 (복수 선택 가능)",
        interest_options,
        default=st.session_state.onboarding_data["interests"],
        label_visibility="collapsed",
        key="interests_select",
    )

    # 커스텀 관심사 입력
    custom_interest = st.text_input(
        "기타 관심사 (직접 입력, 쉼표로 구분)",
        placeholder="예: 게임, 사진, 디자인",
        key="custom_interests_input",
    )

    # 커스텀 관심사 파싱
    all_interests = interests.copy()
    if custom_interest.strip():
        custom_list = [i.strip() for i in custom_interest.split(",") if i.strip()]
        all_interests.extend(custom_list)

    st.markdown("</div>", unsafe_allow_html=True)

    # 학습 목표 선택
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">학습 목표 선택</div>', unsafe_allow_html=True)
    st.caption("목표에 맞는 학습 콘텐츠를 추천해드립니다.")

    goal_options = [
        "회화",
        "문법",
        "작문",
        "독해",
        "시험 대비",
        "비즈니스 독일어",
        "여행",
        "취미",
        "유학 준비",
    ]

    goals = st.multiselect(
        "학습 목표 (복수 선택 가능)",
        goal_options,
        default=st.session_state.onboarding_data["goals"],
        label_visibility="collapsed",
        key="goals_select",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # 버튼
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()

    with col2:
        can_proceed = len(all_interests) > 0 and len(goals) > 0
        if st.button(
            "완료 🎉",
            use_container_width=True,
            type="primary",
            disabled=not can_proceed,
        ):
            # 프로필 생성 및 저장
            st.session_state.onboarding_data["interests"] = all_interests
            st.session_state.onboarding_data["goals"] = goals

            profile_manager = st.session_state.profile_manager
            profile = profile_manager.load_profile()

            profile.nickname = nickname
            profile.profile_icon = icon
            profile.interests = all_interests
            profile.goals = goals

            profile_manager.save_profile(profile)

            # 온보딩 완료 플래그 설정
            st.session_state.onboarding_completed = True

            # 레벨 테스트로 이동
            st.switch_page("pages/level_test.py")

    if not can_proceed:
        st.caption("💡 관심사와 학습 목표를 각각 1개 이상 선택해주세요.")


# =============================================================================
# 메인 앱
# =============================================================================


def main():
    # 테스트 모드 사이드바 렌더링 (프로덕션 배포 시 삭제)
    if render_test_sidebar():
        st.rerun()

    init_session_state()

    # 단계별 화면 표시
    if st.session_state.onboarding_step == 1:
        show_step1()
    elif st.session_state.onboarding_step == 2:
        show_step2()


# =============================================================================
# 앱 실행
# =============================================================================

if __name__ == "__main__":
    main()
