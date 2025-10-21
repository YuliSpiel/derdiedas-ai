"""
DerDieDas.ai - 독일어 학습 플랫폼

메인 진입점: 최초 접속 시 프로필 설정, 기존 사용자는 대시보드로 리다이렉트
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

from models import ProfileManager

# 프로필 체크
profile_manager = ProfileManager()
profile = profile_manager.load_profile()

# 최초 접속 여부 확인 (닉네임이 기본값인 경우)
is_first_visit = profile.nickname == "학습자" and profile.level == "미측정"

if is_first_visit:
    # 최초 접속: 프로필 설정 페이지로 이동
    st.switch_page("pages/dashboard.py")
else:
    # 기존 사용자: 대시보드로 이동
    st.switch_page("pages/dashboard.py")
