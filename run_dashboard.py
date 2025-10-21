"""
DerDieDas.ai 대시보드 실행 스크립트

프로젝트 루트에서 실행하는 래퍼 스크립트입니다.

사용법:
    streamlit run run_dashboard.py
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로
project_root = Path(__file__).parent

# 환경 변수 로드 (config/.env 파일)
env_file = project_root / "config" / ".env"
if env_file.exists():
    print(f"✅ 환경 변수 로딩: {env_file}")
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
else:
    print(f"⚠️  환경 변수 파일을 찾을 수 없습니다: {env_file}")

# src 폴더를 Python path에 추가
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 실제 앱 임포트 및 실행
if __name__ == "__main__":
    # src/dashboard/dashboard_app.py 실행
    app_path = project_root / "src" / "dashboard" / "dashboard_app.py"

    # Streamlit으로 실행
    os.system(f'streamlit run "{app_path}"')
