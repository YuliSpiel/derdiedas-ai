"""
노트북 생성 컴포넌트

두 가지 모드:
1. 학습 자료 업로드: 파일/URL로 학습 자료 제공
2. 자료 없이 시작: AI가 사용자 수준에 맞게 자동 구성
"""

import streamlit as st
from typing import Optional, List
import uuid
from datetime import datetime


def show_notebook_creator_modal() -> Optional[dict]:
    """
    노트북 생성 모달 표시

    Returns:
        생성된 노트북 정보 딕셔너리 (생성되지 않으면 None)
    """

    st.markdown("## 📒 새 노트북 만들기")
    st.markdown("어떤 주제를 공부할까요?")

    # 기본 정보 입력
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        domain = st.radio(
            "분야",
            options=["표현", "문법"],
            horizontal=True,
            key="notebook_domain"
        )

    with col2:
        # 주제 제안
        topic_suggestions = {
            "표현": [
                "여행 - 숙소 체크인",
                "레스토랑 - 음식 주문",
                "쇼핑 - 옷 구매",
                "병원 - 증상 설명",
                "직장 - 회의 참여",
            ],
            "문법": [
                "현재완료 (Perfekt)",
                "관사 - 격 변화",
                "전치사 지배",
                "분리동사",
                "종속절 어순",
            ]
        }

        topic = st.selectbox(
            "주제",
            options=topic_suggestions[domain] + ["직접 입력..."],
            key="notebook_topic"
        )

        if topic == "직접 입력...":
            topic = st.text_input("주제를 입력하세요", key="custom_topic")

    st.markdown("---")

    # 두 가지 모드 선택
    col_left, col_right = st.columns(2)

    notebook_data = None

    with col_left:
        st.markdown("### 📂 학습 자료 업로드")
        st.caption("파일이나 URL을 제공하여 맞춤 학습")

        # 파일 업로드
        uploaded_files = st.file_uploader(
            "파일 업로드 (PDF, TXT, DOCX)",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=True,
            key="uploaded_files"
        )

        # URL 입력
        url_input = st.text_area(
            "또는 URL 입력 (한 줄에 하나씩)",
            placeholder="https://example.com/lesson1\nhttps://example.com/lesson2",
            height=100,
            key="material_urls"
        )

        if st.button("📂 학습 시작 (자료 업로드)", use_container_width=True, type="primary"):
            if not topic or topic == "직접 입력...":
                st.error("주제를 입력해주세요")
            elif not uploaded_files and not url_input.strip():
                st.error("파일을 업로드하거나 URL을 입력해주세요")
            else:
                # 노트북 생성
                material_urls = [url.strip() for url in url_input.split('\n') if url.strip()]

                notebook_data = {
                    "notebook_id": str(uuid.uuid4()),
                    "title": topic,
                    "domain": domain,
                    "topic": topic,
                    "created_at": datetime.now().isoformat(),
                    "has_user_materials": True,
                    "uploaded_files": [f.name for f in uploaded_files] if uploaded_files else [],
                    "material_urls": material_urls,
                    "auto_generated": False,
                }

                st.success(f"✅ 노트북 '{topic}' 생성 완료!")
                st.info("업로드된 자료를 분석하여 학습 컨텐츠를 생성합니다...")

    with col_right:
        st.markdown("### 🤖 자료 없이 시작")
        st.caption("사용자의 수준에 맞는 학습을 자동 구성합니다")

        st.info("📊 현재 레벨과 스킬 숙련도를 기반으로 최적의 학습 경로를 생성합니다")

        # 난이도 선택 (선택사항)
        difficulty = st.selectbox(
            "난이도 (선택사항)",
            options=["자동 (프로필 기반)", "A1", "A2", "B1", "B2", "C1"],
            key="difficulty"
        )

        if st.button("🤖 학습 시작 (AI 자동 구성)", use_container_width=True):
            if not topic or topic == "직접 입력...":
                st.error("주제를 입력해주세요")
            else:
                # AI 자동 생성 노트북
                target_level = None if difficulty == "자동 (프로필 기반)" else difficulty

                notebook_data = {
                    "notebook_id": str(uuid.uuid4()),
                    "title": topic,
                    "domain": domain,
                    "topic": topic,
                    "created_at": datetime.now().isoformat(),
                    "has_user_materials": False,
                    "material_urls": [],
                    "auto_generated": True,
                    "target_cefr_level": target_level,
                }

                st.success(f"✅ 노트북 '{topic}' 생성 완료!")
                st.info("AI가 학습 컨텐츠를 자동으로 구성합니다...")

    return notebook_data


if __name__ == "__main__":
    st.set_page_config(page_title="노트북 생성", layout="centered")

    st.markdown("# 노트북 생성 테스트")

    result = show_notebook_creator_modal()

    if result:
        st.markdown("---")
        st.markdown("### 생성된 노트북 정보")
        st.json(result)
