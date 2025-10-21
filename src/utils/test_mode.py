"""
테스트 모드 유틸리티

이 파일은 개발/테스트 목적으로만 사용됩니다.
프로덕션 배포 시 이 파일과 관련 코드를 삭제하면 됩니다.

사용법:
    from src.utils.test_mode import render_test_sidebar

    # 페이지 상단에 추가
    if render_test_sidebar():
        st.rerun()
"""

import streamlit as st
import os
import shutil
from typing import Optional

# 테스트 모드 활성화 플래그 (프로덕션에서는 False로 설정)
TEST_MODE_ENABLED = True

# 테스트 사용자 목록
TEST_USERS = [
    {"id": "default", "name": "기본 사용자", "description": "캐시 초기화된 상태"},
    {"id": "user_a1", "name": "A1 학습자", "description": "초급 학습자"},
    {"id": "user_a2", "name": "A2 학습자", "description": "초중급 학습자"},
    {"id": "user_b1", "name": "B1 학습자", "description": "중급 학습자"},
    {"id": "custom", "name": "커스텀 사용자", "description": "직접 입력"},
]

def get_test_data_dir() -> str:
    """테스트 데이터 디렉토리 경로"""
    return os.path.join(os.getcwd(), "data", "test_users")

def get_user_data_path(user_id: str, filename: str) -> str:
    """특정 사용자의 데이터 파일 경로"""
    test_dir = get_test_data_dir()
    os.makedirs(os.path.join(test_dir, user_id), exist_ok=True)
    return os.path.join(test_dir, user_id, filename)

def get_production_data_path(filename: str) -> str:
    """프로덕션 데이터 파일 경로"""
    return os.path.join(os.getcwd(), "data", filename)

def switch_user(user_id: str):
    """
    사용자를 전환합니다.
    - 현재 프로덕션 데이터를 백업
    - 선택한 사용자의 데이터를 로드
    """
    # 프로덕션 데이터 백업
    prod_profile = get_production_data_path("user_profile.json")
    prod_notebooks = get_production_data_path("notebooks.json")

    backup_dir = os.path.join(get_test_data_dir(), "_backup")
    os.makedirs(backup_dir, exist_ok=True)

    if os.path.exists(prod_profile):
        shutil.copy(prod_profile, os.path.join(backup_dir, "user_profile.json"))
    if os.path.exists(prod_notebooks):
        shutil.copy(prod_notebooks, os.path.join(backup_dir, "notebooks.json"))

    # 사용자 데이터 로드
    if user_id == "default":
        # 기본 사용자 = 캐시 삭제
        if os.path.exists(prod_profile):
            os.remove(prod_profile)
        if os.path.exists(prod_notebooks):
            os.remove(prod_notebooks)
    else:
        user_profile = get_user_data_path(user_id, "user_profile.json")
        user_notebooks = get_user_data_path(user_id, "notebooks.json")

        if os.path.exists(user_profile):
            shutil.copy(user_profile, prod_profile)
        elif os.path.exists(prod_profile):
            os.remove(prod_profile)

        if os.path.exists(user_notebooks):
            shutil.copy(user_notebooks, prod_notebooks)
        elif os.path.exists(prod_notebooks):
            os.remove(prod_notebooks)

    # 세션 스테이트 초기화
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def save_current_user(user_id: str):
    """현재 상태를 특정 사용자로 저장"""
    prod_profile = get_production_data_path("user_profile.json")
    prod_notebooks = get_production_data_path("notebooks.json")

    user_profile = get_user_data_path(user_id, "user_profile.json")
    user_notebooks = get_user_data_path(user_id, "notebooks.json")

    if os.path.exists(prod_profile):
        shutil.copy(prod_profile, user_profile)
    if os.path.exists(prod_notebooks):
        shutil.copy(prod_notebooks, user_notebooks)

def render_test_sidebar() -> bool:
    """
    테스트 모드 사이드바를 렌더링합니다.

    Returns:
        bool: 사용자가 전환되었으면 True (페이지 리로드 필요)
    """
    if not TEST_MODE_ENABLED:
        return False

    # 사이드바 표시 (CSS 오버라이드)
    st.markdown("""
    <style>
    /* 테스트 모드에서는 사이드바 표시 */
    [data-testid="stSidebar"] {
        display: block !important;
    }

    /* 테스트 모드 표시 */
    .test-mode-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.5rem;
        font-weight: bold;
        font-size: 0.75rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown('<div class="test-mode-badge">🧪 TEST MODE</div>', unsafe_allow_html=True)
        st.title("테스트 모드")

        st.warning("⚠️ 개발/테스트 전용 기능입니다.")

        # 현재 사용자 표시
        current_user = st.session_state.get("test_user_id", "default")
        st.info(f"현재 사용자: **{current_user}**")

        st.divider()

        # 사용자 선택
        st.subheader("사용자 전환")

        selected_user = st.selectbox(
            "사용자 선택",
            options=[u["id"] for u in TEST_USERS],
            format_func=lambda x: next(u["name"] for u in TEST_USERS if u["id"] == x),
            index=[u["id"] for u in TEST_USERS].index(current_user) if current_user in [u["id"] for u in TEST_USERS] else 0,
            key="test_user_select"
        )

        # 선택한 사용자 설명
        user_desc = next((u["description"] for u in TEST_USERS if u["id"] == selected_user), "")
        st.caption(user_desc)

        # 커스텀 사용자 ID 입력
        if selected_user == "custom":
            custom_id = st.text_input("사용자 ID 입력", value="", key="custom_user_id")
            if custom_id:
                selected_user = custom_id

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 전환", use_container_width=True, type="primary"):
                if selected_user != current_user:
                    switch_user(selected_user)
                    st.session_state.test_user_id = selected_user
                    st.success(f"✅ {selected_user}로 전환됨")
                    return True  # 페이지 리로드 필요

        with col2:
            if st.button("💾 저장", use_container_width=True):
                save_current_user(current_user)
                st.success(f"✅ {current_user}에 저장됨")

        st.divider()

        # 캐시 관리
        st.subheader("캐시 관리")

        if st.button("🗑️ 전체 캐시 삭제", use_container_width=True):
            prod_profile = get_production_data_path("user_profile.json")
            prod_notebooks = get_production_data_path("notebooks.json")

            if os.path.exists(prod_profile):
                os.remove(prod_profile)
            if os.path.exists(prod_notebooks):
                os.remove(prod_notebooks)

            # 세션 스테이트 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.success("✅ 캐시 삭제 완료")
            return True  # 페이지 리로드 필요

        st.divider()

        # 디버그 정보
        with st.expander("🔍 디버그 정보"):
            st.json({
                "current_user": current_user,
                "session_state_keys": list(st.session_state.keys()),
                "data_dir": get_test_data_dir(),
            })

    return False
