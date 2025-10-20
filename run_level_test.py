"""
DerDieDas.ai 레벨 테스트 실행 스크립트

프로젝트 루트에서 실행하는 래퍼 스크립트입니다.

사용법:
    streamlit run run_level_test.py
"""

import sys
from pathlib import Path

# src 폴더를 Python path에 추가
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# 실제 앱 임포트 및 실행
if __name__ == "__main__":
    import subprocess
    import os

    # src/level_test/level_test_app.py 실행
    app_path = project_root / "src" / "level_test" / "level_test_app.py"

    # Streamlit으로 실행
    os.system(f'streamlit run "{app_path}"')
