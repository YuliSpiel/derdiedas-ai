"""
DerDieDas.ai 대시보드

사용자 프로필, 추천 노트북, 노트북 관리를 제공하는 메인 대시보드
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import uuid

# 프로젝트 루트를 Python path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from models import UserProfile, Notebook, ProfileManager

# 테스트 모드 임포트 (프로덕션 배포 시 삭제)
from utils.test_mode import render_test_sidebar

# =============================================================================
# 페이지 설정
# =============================================================================

st.set_page_config(
    page_title="DerDieDas.ai - 대시보드",
    page_icon="📚",
    layout="wide",
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

    /* 메인 컨텐츠 전체 너비 사용 */
    .main > div {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .profile-banner {
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .profile-icon {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .profile-stat {
        display: inline-block;
        margin: 0 1rem;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .notebook-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        transition: all 0.3s;
    }
    .notebook-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    .notebook-card-recommended {
        border: 2px solid #e8eaf6;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #f5f5f5;
        opacity: 0.7;
    }
    .notebook-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .notebook-meta {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 2rem 0 1rem 0;
        color: #333;
    }
    .recommended-badge {
        display: inline-block;
        background: #ffd700;
        color: #333;
        padding: 0.2rem 0.5rem;
        border-radius: 3px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .coming-soon {
        font-style: italic;
        color: #999;
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
    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"
    if "show_profile_edit" not in st.session_state:
        st.session_state.show_profile_edit = False


# =============================================================================
# 프로필 배너
# =============================================================================


def show_profile_banner(profile: UserProfile):
    """프로필 배너 표시"""
    st.markdown(
        f"""
    <div class="profile-banner" style="background: {profile.profile_bg_color};">
        <div class="profile-icon">{profile.profile_icon}</div>
        <h2 style="text-align: center; margin-bottom: 1rem;">{profile.nickname}</h2>
        <div style="text-align: center;">
            <span class="profile-stat">📊 레벨: {profile.level}</span>
            <span class="profile-stat">🏆 스탬프: {profile.total_stamps}개</span>
            <span class="profile-stat">🔥 연속 학습: {profile.consecutive_days}일</span>
        </div>
        <div style="text-align: center; margin-top: 1rem; font-size: 0.9rem;">
            <strong>관심사:</strong> {", ".join(profile.interests)} |
            <strong>목표:</strong> {", ".join(profile.goals)}
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 프로필 수정 버튼
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✏️ 프로필 수정", use_container_width=True):
            st.session_state.show_profile_edit = True
            st.rerun()


# =============================================================================
# 프로필 수정
# =============================================================================


def show_profile_edit(profile: UserProfile):
    """프로필 수정 화면"""
    st.markdown("### ✏️ 프로필 수정")

    with st.form("profile_edit_form"):
        new_nickname = st.text_input("닉네임", value=profile.nickname)

        # 아이콘 선택
        icons = ["🐶", "🐱", "🐥", "🐯", "🐼", "🐻", "⛄️", "🩵"]
        icon_idx = icons.index(profile.profile_icon) if profile.profile_icon in icons else 0
        new_icon = st.selectbox("프로필 아이콘", icons, index=icon_idx)

        # 배경색 선택 (이모지 포함 옵션들을 3열로 배치)
        st.markdown("**배경색 선택**")

        bg_colors = [
            ("🟣 보라", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"),
            ("🔵 파랑", "linear-gradient(135deg, #2196F3 0%, #1976D2 100%)"),
            ("🩷 핑크", "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"),
            ("🩵 청록", "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"),
            ("🧡 오렌지", "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"),
            ("💚 민트", "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"),
        ]

        # 현재 배경색 인덱스 찾기
        current_idx = 0
        for idx, (_, gradient) in enumerate(bg_colors):
            if gradient == profile.profile_bg_color:
                current_idx = idx
                break

        # 3열 라디오 버튼 배치
        col1, col2, col3 = st.columns(3)

        with col1:
            choice1 = st.radio("", [bg_colors[0][0], bg_colors[1][0]], index=0 if current_idx in [0, 1] else (1 if current_idx == 1 else 0), key="bg_col1", label_visibility="collapsed")
        with col2:
            choice2 = st.radio("", [bg_colors[2][0], bg_colors[3][0]], index=0 if current_idx in [2, 3] else (1 if current_idx == 3 else 0), key="bg_col2", label_visibility="collapsed")
        with col3:
            choice3 = st.radio("", [bg_colors[4][0], bg_colors[5][0]], index=0 if current_idx in [4, 5] else (1 if current_idx == 5 else 0), key="bg_col3", label_visibility="collapsed")

        # 선택된 배경색 찾기
        selected_name = choice1 if choice1 in [bg_colors[0][0], bg_colors[1][0]] else (choice2 if choice2 in [bg_colors[2][0], bg_colors[3][0]] else choice3)
        new_bg_color = next((gradient for name, gradient in bg_colors if name == selected_name), bg_colors[0][1])

        # 관심사
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

        # 기존 관심사 중 목록에 없는 것들 추가
        existing_custom_interests = [i for i in profile.interests if i not in interest_options]

        new_interests = st.multiselect(
            "관심사 (복수 선택)",
            interest_options,
            default=[i for i in profile.interests if i in interest_options]
        )

        # 커스텀 관심사 입력
        custom_interest = st.text_input(
            "기타 관심사 (직접 입력, 쉼표로 구분)",
            value=", ".join(existing_custom_interests),
            placeholder="예: 게임, 사진, 디자인"
        )

        # 커스텀 관심사 파싱
        if custom_interest.strip():
            custom_list = [i.strip() for i in custom_interest.split(",") if i.strip()]
            new_interests.extend(custom_list)

        # 목표
        goal_options = ["회화", "문법", "작문", "독해", "시험 대비", "비즈니스 독일어", "여행", "취미", "유학 준비"]
        new_goals = st.multiselect("학습 목표 (복수 선택)", goal_options, default=profile.goals)

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 저장", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("취소", use_container_width=True)

        if submitted:
            profile.nickname = new_nickname
            profile.profile_icon = new_icon
            profile.profile_bg_color = new_bg_color
            profile.interests = new_interests
            profile.goals = new_goals
            st.session_state.profile_manager.save_profile(profile)
            st.session_state.show_profile_edit = False
            st.success("프로필이 업데이트되었습니다!")
            st.rerun()

        if cancelled:
            st.session_state.show_profile_edit = False
            st.rerun()


# =============================================================================
# 추천 노트북
# =============================================================================


def show_recommended_notebooks(notebooks: list):
    """추천 노트북 표시"""
    st.markdown('<div class="section-header">📌 오늘의 추천 사이클 노트북</div>', unsafe_allow_html=True)

    recommended = [nb for nb in notebooks if nb.is_recommended]

    if not recommended:
        st.info("추천 노트북이 없습니다. 새 노트북을 만들어 보세요!")
        return

    # 2열로 표시
    col1, col2 = st.columns(2)

    for idx, notebook in enumerate(recommended[:2]):
        with col1 if idx == 0 else col2:
            # 추천 노트북 카드 (아직 생성 전이므로 옅은 스타일)
            st.markdown(
                f"""
            <div class="notebook-card-recommended">
                <div class="notebook-title">
                    {notebook.title}
                    <span class="recommended-badge">추천</span>
                </div>
                <div class="notebook-meta">
                    <span class="coming-soon">곧 제공될 예정입니다</span>
                </div>
                <div class="notebook-meta">
                    총 학습 횟수: {notebook.total_sessions}회
                    {f" · 최근: {notebook.last_studied}" if notebook.last_studied else ""}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # 열기 버튼 (비활성화)
            st.button(
                "📖 열기 (준비 중)",
                key=f"open_rec_{notebook.id}",
                disabled=True,
                use_container_width=True,
            )


# =============================================================================
# 노트북 목록
# =============================================================================


def show_notebook_list(notebooks: list):
    """노트북 목록 표시"""
    st.markdown('<div class="section-header">📚 내 노트북</div>', unsafe_allow_html=True)

    # 추천 노트북 제외
    user_notebooks = [nb for nb in notebooks if not nb.is_recommended]

    if not user_notebooks:
        st.info("아직 생성한 노트북이 없습니다. 새 노트북을 만들어 보세요!")
    else:
        for notebook in user_notebooks:
            st.markdown(
                f"""
            <div class="notebook-card">
                <div class="notebook-title">{notebook.title}</div>
                <div class="notebook-meta">
                    총 학습 횟수: {notebook.total_sessions}회
                    {f" · 최근: {notebook.last_studied}" if notebook.last_studied else ""}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                if st.button("📖 열기", key=f"open_{notebook.id}", use_container_width=True):
                    st.info("학습 사이클은 곧 제공될 예정입니다!")
                    # TODO: 학습 사이클 페이지로 이동
            with col2:
                if st.button(
                    "🗑️ 삭제", key=f"delete_{notebook.id}", use_container_width=True
                ):
                    st.session_state.profile_manager.delete_notebook(notebook.id)
                    st.success(f"'{notebook.title}' 노트북이 삭제되었습니다.")
                    st.rerun()
            with col3:
                pass  # 여백


# =============================================================================
# 새 노트북 만들기
# =============================================================================


def show_create_notebook_button():
    """새 노트북 만들기 버튼"""
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➕ 새 노트북 만들기", use_container_width=True, type="primary"):
            st.session_state.show_create_notebook = True
            st.rerun()


def show_create_notebook_form():
    """새 노트북 생성 폼"""
    st.markdown("### ➕ 새 노트북 만들기")

    with st.form("create_notebook_form"):
        category = st.selectbox("카테고리", ["문법", "표현", "어휘", "독해", "작문"])
        topic = st.text_input("주제 (예: 정관사, 출장 회화, 날씨 표현 등)")

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("✅ 생성", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("취소", use_container_width=True)

        if submitted:
            if not topic.strip():
                st.error("주제를 입력해 주세요.")
            else:
                # 새 노트북 생성
                new_notebook = Notebook(
                    id=f"nb_{uuid.uuid4().hex[:8]}",
                    title=f"{category} · {topic}",
                    category=category,
                    topic=topic,
                    created_at=datetime.now().isoformat(),
                )
                st.session_state.profile_manager.add_notebook(new_notebook)
                st.session_state.show_create_notebook = False
                st.success(f"'{new_notebook.title}' 노트북이 생성되었습니다!")
                st.rerun()

        if cancelled:
            st.session_state.show_create_notebook = False
            st.rerun()


# =============================================================================
# 메인 앱
# =============================================================================


def main():
    # 테스트 모드 사이드바 렌더링 (프로덕션 배포 시 삭제)
    if render_test_sidebar():
        st.rerun()

    init_session_state()

    # 프로필 로드
    profile_manager = st.session_state.profile_manager
    profile = profile_manager.load_profile()
    notebooks = profile_manager.load_notebooks()

    # 헤더
    st.title("🇩🇪 DerDieDas.ai")

    # 프로필 수정 모드
    if st.session_state.show_profile_edit:
        show_profile_edit(profile)
        return

    # 노트북 생성 모드
    if st.session_state.get("show_create_notebook", False):
        show_create_notebook_form()
        return

    # 프로필 배너
    show_profile_banner(profile)

    # 추천 노트북
    show_recommended_notebooks(notebooks)

    # 내 노트북 목록
    show_notebook_list(notebooks)

    # 새 노트북 만들기 버튼
    show_create_notebook_button()

    # 하단 네비게이션
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📊 레벨 테스트 하러 가기", use_container_width=True, type="primary"):
            st.switch_page("pages/level_test.py")


# =============================================================================
# 앱 실행
# =============================================================================

if __name__ == "__main__":
    main()
