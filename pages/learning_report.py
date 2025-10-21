"""
학습 리포트 페이지

사용자의 스킬별 숙련도를 시각화하여 보여줍니다.
- 카테고리별 그룹핑 (관사, 동사, 형용사 등)
- CEFR 레벨별 필터링
- 가로 막대 프로그레스 바로 숙련도 표시 (0-100)
"""

import streamlit as st
import sys
from pathlib import Path
import json
from collections import defaultdict

# 프로필 관리 임포트
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from models import ProfileManager
import csv

# 온톨로지 로드 (스킬 메타데이터)
ontology_path = project_root / "data" / "grammar_ontology" / "grammar_ontology.json"
skill_tree_path = project_root / "data" / "grammar_ontology" / "skill_tree.csv"


def load_ontology():
    """온톨로지 데이터 로드 (CSV 메타데이터 + JSON 컨텐츠 합침)"""
    # 1. CSV에서 메타데이터 로드
    metadata = {}
    if skill_tree_path.exists():
        with open(skill_tree_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                metadata[row['skill_id']] = {
                    'id': row['skill_id'],
                    'title_ko': row['name'],
                    'title_en': row['name'],
                    'category': row['area'],
                    'cefr_level': row['cefr'],
                    'domain': row['domain'],
                }

    # 2. JSON에서 컨텐츠 로드
    if not ontology_path.exists():
        return metadata  # CSV 메타데이터만이라도 반환

    with open(ontology_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 리스트 형식 처리
    topics = data if isinstance(data, list) else data.get("topics", [])

    # 3. 메타데이터와 컨텐츠 합치기
    skills = {}
    for topic in topics:
        skill_id = topic.get("skill_id") or topic.get("id")
        if skill_id in metadata:
            # 메타데이터 + JSON 컨텐츠 합침
            skills[skill_id] = {**metadata[skill_id], **topic}
        else:
            # JSON만 있는 경우
            skills[skill_id] = topic

    # 4. JSON에 없지만 CSV에만 있는 스킬 추가 (메타데이터만)
    for skill_id, meta in metadata.items():
        if skill_id not in skills:
            skills[skill_id] = meta

    return skills


# =============================================================================
# 페이지 설정
# =============================================================================

st.set_page_config(
    page_title="학습 리포트",
    page_icon="📊",
    layout="wide",
)

# 커스텀 CSS
st.markdown(
    """
<style>
    /* 사이드바 완전히 숨기기 */
    [data-testid="stSidebar"] {
        display: none;
    }

    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }

    .category-header {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }

    .skill-row {
        background-color: #ffffff;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }

    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
    }

    .skill-title {
        font-weight: 500;
        color: #333;
    }

    .skill-score {
        font-weight: 600;
        color: #667eea;
    }

    /* 프로그레스 바 커스텀 스타일 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
</style>
""",
    unsafe_allow_html=True,
)


# =============================================================================
# 메인 앱
# =============================================================================


def main():
    # 헤더
    st.markdown(
        """
    <div class="main-header">
        <h1>📊 학습 리포트</h1>
        <p>스킬별 숙련도를 확인하고 학습 방향을 점검하세요</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 프로필 로드
    profile_manager = ProfileManager()
    profile = profile_manager.load_profile()

    # 스킬 숙련도 확인
    skill_proficiency = profile.skill_proficiency

    if not skill_proficiency:
        st.warning("⚠️ 아직 스킬 숙련도 데이터가 없습니다.")
        st.info("레벨 테스트를 완료하면 스킬별 숙련도가 자동으로 평가됩니다.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📊 레벨 테스트 하러 가기", use_container_width=True, type="primary"):
                st.switch_page("pages/level_test.py")

        st.markdown("---")
        if st.button("🏠 대시보드로 돌아가기", use_container_width=False):
            st.switch_page("pages/dashboard.py")

        return

    # 온톨로지 로드
    ontology = load_ontology()

    if not ontology:
        st.error("❌ 온톨로지 데이터를 로드할 수 없습니다.")
        st.caption(f"파일 경로: {ontology_path}")
        return

    # 프로필 정보 표시
    st.markdown("### 👤 프로필 정보")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("닉네임", profile.nickname)
    with col2:
        st.metric("현재 레벨", profile.level)
    with col3:
        # None 값 필터링
        valid_scores = [v for v in skill_proficiency.values() if v is not None]
        total_skills = len(valid_scores)
        avg_proficiency = sum(valid_scores) / total_skills if total_skills > 0 else 0
        st.metric("평균 숙련도", f"{avg_proficiency:.1f}/100")

    st.markdown("---")

    # 필터 옵션
    st.markdown("### 🔍 필터")
    col1, col2 = st.columns(2)

    with col1:
        cefr_filter = st.multiselect(
            "CEFR 레벨",
            options=["A1", "A2", "B1", "B2", "C1"],
            default=["A1", "A2", "B1", "B2"],
            help="표시할 CEFR 레벨 선택"
        )

    with col2:
        category_options = sorted(set(skill["category"] for skill in ontology.values()))
        category_filter = st.multiselect(
            "카테고리",
            options=category_options,
            default=category_options[:5] if len(category_options) > 5 else category_options,
            help="표시할 카테고리 선택"
        )

    st.markdown("---")

    # 스킬을 카테고리별로 그룹화
    skills_by_category = defaultdict(list)

    for skill_id, score in skill_proficiency.items():
        # None 값 스킵
        if score is None:
            continue

        if skill_id in ontology:
            skill = ontology[skill_id]

            # 필터 적용
            if skill.get("cefr_level") not in cefr_filter:
                continue
            if skill.get("category") not in category_filter:
                continue

            skills_by_category[skill.get("category", "기타")].append({
                "id": skill_id,
                "title_ko": skill.get("title_ko", skill_id),
                "title_en": skill.get("title_en", ""),
                "cefr_level": skill.get("cefr_level", ""),
                "score": score
            })

    # 카테고리명 매핑 (한국어)
    category_names = {
        "articles": "관사",
        "nouns": "명사",
        "cases": "격",
        "pronouns": "대명사",
        "adjectives": "형용사",
        "verbs": "동사",
        "negation": "부정",
        "word_order": "어순",
        "clauses": "절",
        "questions": "의문문",
        "imperatives": "명령문",
        "prepositions": "전치사",
        "time": "시간/수사",
        "particles": "조사",
        "other": "기타"
    }

    # 카테고리별 표시
    if not skills_by_category:
        st.info("선택한 필터 조건에 맞는 스킬이 없습니다.")
    else:
        st.markdown("### 📚 스킬별 숙련도")

        for category, skills in sorted(skills_by_category.items()):
            # 카테고리 헤더
            category_name_ko = category_names.get(category, category)
            avg_score = sum(s["score"] for s in skills) / len(skills)

            st.markdown(
                f"""
            <div class="category-header">
                <h4>{category_name_ko} ({category})</h4>
                <p style="margin: 0; color: #666;">
                    {len(skills)}개 스킬 | 평균 숙련도: {avg_score:.1f}/100
                </p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # 스킬별 프로그레스 바
            for skill in sorted(skills, key=lambda x: x["cefr_level"] + x["title_ko"]):
                # 레벨 뱃지
                level_color = {
                    "A1": "🟢",
                    "A2": "🔵",
                    "B1": "🟡",
                    "B2": "🟠",
                    "C1": "🔴"
                }.get(skill["cefr_level"], "⚪")

                # 스킬 제목 및 점수
                st.markdown(
                    f"""
                <div class="skill-row">
                    <div class="progress-label">
                        <span class="skill-title">
                            {level_color} {skill['cefr_level']} | {skill['title_ko']}
                        </span>
                        <span class="skill-score">{skill['score']}/100</span>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # 프로그레스 바
                st.progress(skill['score'] / 100)

            st.markdown("<br>", unsafe_allow_html=True)

    # 하단 버튼
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏠 대시보드로 돌아가기", use_container_width=True, type="primary"):
            st.switch_page("pages/dashboard.py")

    with col2:
        if st.button("📊 레벨 테스트 다시 하기", use_container_width=True):
            st.switch_page("pages/level_test.py")


if __name__ == "__main__":
    main()
