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
        st.title("개발 모드")

        st.warning("⚠️ 개발/테스트 전용")

        # 데이터 초기화 버튼만 표시
        if st.button("🗑️ 데이터 초기화", use_container_width=True, type="primary"):
            prod_profile = get_production_data_path("user_profile.json")
            prod_notebooks = get_production_data_path("notebooks.json")

            if os.path.exists(prod_profile):
                os.remove(prod_profile)
            if os.path.exists(prod_notebooks):
                os.remove(prod_notebooks)

            # 세션 스테이트 초기화
            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.success("✅ 데이터 초기화 완료")
            return True  # 페이지 리로드 필요

        st.caption("모든 사용자 데이터를 삭제하고 첫 접속 상태로 초기화합니다.")

    return False
