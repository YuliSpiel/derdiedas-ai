"""
DerDieDas.ai 대시보드

사용자 프로필, 추천 노트북, 노트북 관리를 제공하는 메인 대시보드
"""

import streamlit as st
import sys
from pathlib import Path

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
        border-radius: 10px 10px 0 0;
        padding: 1.5rem;
        padding-bottom: 1rem;
        margin: 1rem 0 0 0;
        background: white;
        transition: all 0.3s;
    }
    .notebook-card:hover {
        border-color: #667eea;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
    }
    .notebook-actions {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #f0f0f0;
    }
    /* 노트북 카드 바로 다음 요소 (버튼 컨테이너) 스타일 */
    .notebook-card + div {
        border: 2px solid #e0e0e0;
        border-top: 1px solid #f0f0f0;
        border-radius: 0 0 10px 10px;
        padding: 1rem 1.5rem 1.2rem 1.5rem;
        margin: 0 0 1.5rem 0;
        background: white;
    }
    .notebook-card:hover + div {
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

    # 세션에 임시 배경색 저장
    if "temp_bg_color" not in st.session_state:
        st.session_state.temp_bg_color = profile.profile_bg_color

    # 배경색 선택 (form 밖에서 처리)
    st.markdown("**배경색 선택**")

    bg_colors = [
        ("보라", "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"),
        ("파랑", "linear-gradient(135deg, #2196F3 0%, #1976D2 100%)"),
        ("핑크", "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"),
        ("청록", "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"),
        ("오렌지", "linear-gradient(135deg, #fa709a 0%, #fee140 100%)"),
        ("민트", "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"),
    ]

    # 색상 버튼을 3열로 배치
    cols = st.columns(3)
    for idx, (name, gradient) in enumerate(bg_colors):
        with cols[idx % 3]:
            is_selected = st.session_state.temp_bg_color == gradient
            border_style = "3px solid #667eea" if is_selected else "2px solid #ddd"

            # 색상 프리뷰 버튼 (HTML + CSS)
            button_html = f"""
            <div style="
                background: {gradient};
                height: 60px;
                border-radius: 8px;
                border: {border_style};
                cursor: pointer;
                margin: 5px 0;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                text-shadow: 0 1px 2px rgba(0,0,0,0.3);
            ">
                {name}
            </div>
            """
            st.markdown(button_html, unsafe_allow_html=True)

            if st.button(
                f"선택 {idx}",
                key=f"bg_btn_{idx}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
            ):
                st.session_state.temp_bg_color = gradient
                st.rerun()

    st.markdown("---")

    with st.form("profile_edit_form"):
        new_nickname = st.text_input("닉네임", value=profile.nickname)

        # 아이콘 선택
        icons = ["🐶", "🐱", "🐥", "🐯", "🐼", "🐻", "⛄️", "🩵"]
        icon_idx = (
            icons.index(profile.profile_icon) if profile.profile_icon in icons else 0
        )
        new_icon = st.selectbox("프로필 아이콘", icons, index=icon_idx)

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
        existing_custom_interests = [
            i for i in profile.interests if i not in interest_options
        ]

        new_interests = st.multiselect(
            "관심사 (복수 선택)",
            interest_options,
            default=[i for i in profile.interests if i in interest_options],
        )

        # 커스텀 관심사 입력
        custom_interest = st.text_input(
            "기타 관심사 (직접 입력, 쉼표로 구분)",
            value=", ".join(existing_custom_interests),
            placeholder="예: 게임, 사진, 디자인",
        )

        # 커스텀 관심사 파싱
        if custom_interest.strip():
            custom_list = [i.strip() for i in custom_interest.split(",") if i.strip()]
            new_interests.extend(custom_list)

        # 목표
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
        new_goals = st.multiselect(
            "학습 목표 (복수 선택)", goal_options, default=profile.goals
        )

        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 저장", use_container_width=True)
        with col2:
            cancelled = st.form_submit_button("취소", use_container_width=True)

        if submitted:
            profile.nickname = new_nickname
            profile.profile_icon = new_icon
            profile.profile_bg_color = st.session_state.temp_bg_color
            profile.interests = new_interests
            profile.goals = new_goals
            st.session_state.profile_manager.save_profile(profile)
            st.session_state.show_profile_edit = False
            # 세션 초기화
            if "temp_bg_color" in st.session_state:
                del st.session_state.temp_bg_color
            st.success("프로필이 업데이트되었습니다!")
            st.rerun()

        if cancelled:
            st.session_state.show_profile_edit = False
            # 세션 초기화
            if "temp_bg_color" in st.session_state:
                del st.session_state.temp_bg_color
            st.rerun()


# =============================================================================
# 추천 노트북
# =============================================================================


def show_recommended_notebooks(notebooks: list):
    """추천 노트북 표시"""
    st.markdown(
        '<div class="section-header">📌 오늘의 추천 사이클 노트북</div>',
        unsafe_allow_html=True,
    )

    recommended = [nb for nb in notebooks if nb.is_recommended]

    if not recommended:
        st.info("추천 노트북이 없습니다. 새 노트북을 만들어 보세요!")
        return

    # 2열로 표시
    col1, col2 = st.columns(2)

    for idx, notebook in enumerate(recommended[:2]):
        with col1 if idx == 0 else col2:
            # Streamlit 네이티브 컨테이너 사용 (추천 노트북)
            with st.container(border=True):
                # 제목과 추천 뱃지
                st.markdown(f"### {notebook.title} 🌟")
                st.caption("적응형 주제 선정 - 당신의 실력에 맞춰 문제가 생성됩니다")
                st.caption(f"총 학습 횟수: {notebook.total_sessions}회{f' · 최근: {notebook.last_studied}' if notebook.last_studied else ''}")

                st.markdown("---")

                # 버튼
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(
                        "📖 열기",
                        key=f"open_rec_{notebook.id}",
                        use_container_width=True,
                        type="primary"
                    ):
                        st.session_state.selected_notebook_id = notebook.id
                        st.switch_page("pages/learning_session.py")
                with col_btn2:
                    if st.button(
                        "🗑️ 삭제",
                        key=f"delete_rec_{notebook.id}",
                        use_container_width=True
                    ):
                        st.session_state.profile_manager.delete_notebook(notebook.id)
                        st.rerun()


# =============================================================================
# 노트북 목록
# =============================================================================


def show_notebook_list(notebooks: list):
    """노트북 목록 표시"""
    st.markdown(
        '<div class="section-header">📚 내 노트북</div>', unsafe_allow_html=True
    )

    # 추천 노트북 제외
    user_notebooks = [nb for nb in notebooks if not nb.is_recommended]

    if not user_notebooks:
        st.info("아직 생성한 노트북이 없습니다. 새 노트북을 만들어 보세요!")
    else:
        # 2열로 표시
        col1, col2 = st.columns(2)

        for idx, notebook in enumerate(user_notebooks):
            with col1 if idx % 2 == 0 else col2:
                # Streamlit 네이티브 컨테이너 사용
                with st.container(border=True):
                    # 노트북 정보
                    st.markdown(f"### {notebook.title}")
                    st.caption(f"총 학습 횟수: {notebook.total_sessions}회{f' · 최근: {notebook.last_studied}' if notebook.last_studied else ''}")

                    st.markdown("---")

                    # 버튼
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button(
                            "📖 열기", key=f"open_{notebook.id}", use_container_width=True, type="primary"
                        ):
                            # 학습 세션 페이지로 이동
                            st.session_state.selected_notebook_id = notebook.id
                            st.switch_page("pages/learning_session.py")
                    with col_btn2:
                        if st.button(
                            "🗑️ 삭제", key=f"delete_{notebook.id}", use_container_width=True
                        ):
                            st.session_state.profile_manager.delete_notebook(notebook.id)
                            st.success(f"'{notebook.title}' 노트북이 삭제되었습니다.")
                            st.rerun()


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
    """새 노트북 생성 폼 (스킬 기반)"""
    # notebook_creator는 이미 src path에 있음
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))

    from components.notebook_creator import show_notebook_creator_modal

    # 노트북 생성 UI 표시
    notebook_data = show_notebook_creator_modal()

    if notebook_data:
        # 노트북 생성
        new_notebook = Notebook(
            id=notebook_data["notebook_id"],
            title=notebook_data["title"],
            category=notebook_data["category"],
            topic=notebook_data["topic"],
            created_at=notebook_data["created_at"],
            is_recommended=notebook_data.get("is_recommended", False),
            skill_id=notebook_data.get("skill_id"),  # 사용자 선택 스킬 ID
        )
        st.session_state.profile_manager.add_notebook(new_notebook)
        st.session_state.show_create_notebook = False

        # 바로 학습 시작으로 이동
        st.session_state.selected_notebook_id = new_notebook.id
        st.switch_page("pages/learning_session.py")

    # 취소 버튼
    st.markdown("---")
    if st.button("⬅️ 취소", use_container_width=True):
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
    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "📊 레벨 테스트 하러 가기", use_container_width=True, type="primary"
        ):
            # 레벨 테스트 세션 초기화
            if "test_session" in st.session_state:
                del st.session_state.test_session
            if "initialized" in st.session_state:
                del st.session_state.initialized
            if "show_result" in st.session_state:
                del st.session_state.show_result
            st.switch_page("pages/level_test.py")
    with col2:
        if st.button(
            "📈 학습 리포트 보기", use_container_width=True
        ):
            st.switch_page("pages/learning_report.py")


# =============================================================================
# 앱 실행
# =============================================================================

if __name__ == "__main__":
    main()
