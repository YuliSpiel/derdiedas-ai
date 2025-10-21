"""
노트북 생성 컴포넌트

스킬 기반 노트북 생성
"""

import streamlit as st
from typing import Optional, Dict, List
import uuid
from datetime import datetime
from pathlib import Path
import csv


def load_skills() -> List[Dict]:
    """스킬 데이터 로드"""
    try:
        skill_tree_path = Path("data/grammar_ontology/skill_tree.csv")
        if skill_tree_path.exists():
            with open(skill_tree_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return list(reader)
        return []
    except Exception as e:
        st.error(f"스킬 데이터 로드 실패: {e}")
        return []


def show_notebook_creator_modal() -> Optional[dict]:
    """
    노트북 생성 모달 표시

    Returns:
        생성된 노트북 정보 딕셔너리 (생성되지 않으면 None)
    """

    st.markdown("## 📒 새 노트북 만들기")
    st.markdown("학습할 스킬을 선택하세요")

    st.markdown("---")

    # 스킬 데이터 로드
    skills = load_skills()

    if not skills:
        st.error("스킬 데이터를 불러올 수 없습니다.")
        return None

    # CEFR 레벨별로 그룹화
    skills_by_level = {}
    for skill in skills:
        level = skill['cefr']
        if level not in skills_by_level:
            skills_by_level[level] = []
        skills_by_level[level].append(skill)

    # 레벨 선택
    col1, col2 = st.columns([1, 2])

    with col1:
        selected_level = st.selectbox(
            "CEFR 레벨",
            options=sorted(skills_by_level.keys()),
            key="skill_level"
        )

    with col2:
        # 선택된 레벨의 스킬 목록
        level_skills = skills_by_level[selected_level]

        # 스킬 이름을 드롭다운 옵션으로 표시
        skill_options = [f"{skill['name']} ({skill['area']})" for skill in level_skills]

        selected_skill_idx = st.selectbox(
            "스킬",
            options=range(len(skill_options)),
            format_func=lambda i: skill_options[i],
            key="selected_skill"
        )

    selected_skill = level_skills[selected_skill_idx]

    # 선택된 스킬 정보 표시
    with st.container(border=True):
        st.markdown(f"**{selected_skill['name']}**")
        st.caption(f"📚 영역: {selected_skill['area']} | 🎯 레벨: {selected_skill['cefr']}")
        if selected_skill.get('hint'):
            st.info(f"💡 {selected_skill['hint']}")

    st.markdown("---")

    notebook_data = None

    # 노트북 생성 버튼
    if st.button("📖 학습 시작", use_container_width=True, type="primary"):
        # 노트북 생성
        notebook_data = {
            "notebook_id": f"nb_{selected_skill['skill_id']}",
            "skill_id": selected_skill['skill_id'],
            "title": selected_skill['name'],
            "category": "Grammar",
            "topic": selected_skill['area'],
            "cefr_level": selected_skill['cefr'],
            "created_at": datetime.now().isoformat(),
            "is_recommended": False,
        }

        st.success(f"✅ 노트북 '{selected_skill['name']}' 생성 완료!")
        st.info("학습을 시작합니다...")

    return notebook_data


if __name__ == "__main__":
    st.set_page_config(page_title="노트북 생성", layout="centered")

    st.markdown("# 노트북 생성 테스트")

    result = show_notebook_creator_modal()

    if result:
        st.markdown("---")
        st.markdown("### 생성된 노트북 정보")
        st.json(result)
