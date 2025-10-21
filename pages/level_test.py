"""
독일어 레벨 테스트 Streamlit 앱

작문 기반 적응형 레벨 테스트:
- 5개의 작문 과제를 순차적으로 제시
- 사용자 답변을 2-3문장으로 받음
- CEFR 코퍼스와의 유사도 기반으로 레벨 추정
- 최종 레벨을 A2~C1 + 초반/중반/후반으로 판정
"""

import streamlit as st
import sys
from pathlib import Path

# 프로필 관리를 위한 임포트
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from level_test.CEFR_Eval import LevelTestSession, CEFRLevel
from models import ProfileManager

# =============================================================================
# 페이지 설정
# =============================================================================

st.set_page_config(
    page_title="DerDieDas.ai 레벨 테스트",
    page_icon="📊",
    layout="centered",
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

    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }
    .progress-info {
        text-align: center;
        color: #666;
        margin: 1rem 0;
    }
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    .result-level {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .analysis-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
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
    if "test_session" not in st.session_state:
        st.session_state.test_session = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "current_answer" not in st.session_state:
        st.session_state.current_answer = ""
    if "show_result" not in st.session_state:
        st.session_state.show_result = False


# =============================================================================
# 메인 앱
# =============================================================================


def main():
    init_session_state()

    # 헤더
    st.markdown(
        """
    <div class="main-header">
        <h1>🇩🇪 DerDieDas.ai</h1>
        <h3>독일어 레벨 테스트</h3>
        <p>5개의 작문 과제로 당신의 독일어 실력을 측정합니다</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 세션이 없으면 시작 화면
    if st.session_state.test_session is None:
        show_welcome_screen()
    # 테스트 완료 시 결과 화면
    elif st.session_state.show_result:
        show_result_screen()
    # 테스트 진행 중
    else:
        show_test_screen()


def show_welcome_screen():
    """시작 화면"""
    st.markdown("### 📋 테스트 안내")

    st.info(
        """
    **테스트 방식:**
    - 총 5개의 작문 질문이 제시됩니다
    - 각 질문에 2-3문장으로 답변해 주세요
    - 답변에 따라 다음 질문의 난이도가 조정됩니다
    - 첫 질문은 모두 동일합니다: "Wie heißt du, und woher kommst du?"

    **예상 소요 시간:** 약 10-15분

    **평가 기준:**
    - 어휘의 다양성과 정확성
    - 문법 구조의 복잡도
    - 의견 표현 및 논리적 서술 능력

    **최종 결과:**
    - CEFR 레벨 (A2, B1, B2, C1)
    - 세부 단계 (초반, 중반, 후반)
    """
    )

    st.markdown("---")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 레벨 테스트 시작하기", use_container_width=True):
            with st.spinner("테스트 환경을 준비하는 중입니다..."):
                # 세션 생성 및 초기화
                session = LevelTestSession()
                session.initialize()
                st.session_state.test_session = session
                st.session_state.initialized = True
                st.rerun()


def show_test_screen():
    """테스트 진행 화면"""
    session = st.session_state.test_session

    # 진행률 표시
    progress = len(session.responses) / 5
    st.progress(progress)
    st.markdown(
        f'<div class="progress-info">질문 {len(session.responses) + 1} / 5</div>',
        unsafe_allow_html=True,
    )

    # 현재 질문 가져오기
    current_question = session.get_current_question()

    # 질문 표시
    st.markdown(
        f"""
    <div class="question-box">
        <h4>📝 질문 {len(session.responses) + 1}</h4>
        <p><strong>주제:</strong> {current_question.topic}</p>
        <p><strong>질문:</strong></p>
        <h3>{current_question.text}</h3>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### ✍️ 답변을 작성해 주세요")
    st.caption("2-3문장 정도로 답변해 주세요. 독일어로 작성해 주세요.")

    # 답변 입력
    user_answer = st.text_area(
        label="답변",
        placeholder="Hier schreiben Sie Ihre Antwort...",
        height=150,
        key=f"answer_{len(session.responses)}",
        label_visibility="collapsed",
    )

    # 답변 제출
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ 답변 제출", use_container_width=True, type="primary"):
            if not user_answer.strip():
                st.error("답변을 입력해 주세요.")
            elif len(user_answer.split()) < 5:
                st.warning("답변이 너무 짧습니다. 2-3문장 정도로 작성해 주세요.")
            else:
                with st.spinner("답변을 분석하는 중..."):
                    # 답변 제출 및 평가
                    session.submit_response(user_answer)

                    # 테스트 완료 확인
                    if session.is_complete():
                        st.session_state.show_result = True
                        st.rerun()
                    else:
                        st.success("답변이 제출되었습니다!")
                        st.balloons()
                        # 다음 질문으로 이동
                        st.rerun()

    # 이전 답변 히스토리 (선택사항)
    if len(session.responses) > 0:
        with st.expander("📚 이전 답변 보기"):
            for i, resp in enumerate(session.responses):
                st.markdown(f"**질문 {i + 1}:** {resp.question_id}")
                st.text(resp.text)
                st.caption(
                    f"추정 레벨: {resp.estimated_level.name} (신뢰도: {resp.similarity_score:.1%})"
                )
                st.markdown("---")


def show_result_screen():
    """결과 화면"""
    session = st.session_state.test_session

    # 최종 결과 계산
    result = session.get_final_result()

    # 결과 표시
    st.markdown(
        f"""
    <div class="result-box">
        <h2>🎉 테스트 완료!</h2>
        <p>당신의 독일어 레벨은...</p>
        <div class="result-level">{result['display_level']}</div>
        <p>입니다!</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 레벨별 설명
    level_descriptions = {
        "A2": """
        **A2 레벨 (기초 단계)**
        - 일상적인 표현과 간단한 문장을 이해하고 사용할 수 있습니다
        - 자신, 가족, 쇼핑, 일 등 친숙한 주제에 대해 의사소통할 수 있습니다
        - 간단하고 일상적인 상황에서 정보를 교환할 수 있습니다
        """,
        "B1": """
        **B1 레벨 (중급 단계)**
        - 일, 학교, 여가 등 익숙한 주제에 대한 표준어를 이해할 수 있습니다
        - 여행 중 발생하는 대부분의 상황을 처리할 수 있습니다
        - 경험, 사건, 꿈, 희망을 설명하고 간단히 이유를 설명할 수 있습니다
        """,
        "B2": """
        **B2 레벨 (중상급 단계)**
        - 추상적인 주제를 포함한 복잡한 텍스트의 주요 내용을 이해할 수 있습니다
        - 원어민과 자연스럽고 유창하게 대화할 수 있습니다
        - 다양한 주제에 대해 명확하고 상세한 텍스트를 작성할 수 있습니다
        """,
        "C1": """
        **C1 레벨 (고급 단계)**
        - 복잡하고 긴 텍스트를 이해하고 함축적 의미를 파악할 수 있습니다
        - 적절한 표현을 찾느라 고민하지 않고 유창하게 표현할 수 있습니다
        - 사회적, 학문적, 직업적 목적으로 언어를 효과적이고 유연하게 사용할 수 있습니다
        """,
    }

    st.markdown(
        f"### 📊 {result['final_level']} 레벨이란?",
    )
    st.info(level_descriptions[result["final_level"]])

    # 상세 분석
    st.markdown("### 📈 상세 분석")

    analysis = result["analysis"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric("평균 레벨 점수", f"{analysis['average_level_value']:.2f}")
    with col2:
        st.metric("평균 신뢰도", f"{analysis['average_confidence']:.1%}")

    # 레벨 분포
    st.markdown("#### 답변별 레벨 분포")
    level_dist = analysis["level_distribution"]
    for level, count in level_dist.items():
        if count > 0:
            st.write(f"**{level}:** {count}개 답변")

    # 각 답변별 상세 점수
    with st.expander("🔍 답변별 상세 점수 (코사인 유사도 기반)"):
        for i, score in enumerate(analysis["response_scores"]):
            st.markdown(
                f"""
            <div class="analysis-box">
                <strong>질문 {i + 1}:</strong> {score['question']}<br>
                <strong>추정 레벨:</strong> {score['level']}<br>
                <strong>신뢰도:</strong> {score['confidence']:.1%}
            </div>
            """,
                unsafe_allow_html=True,
            )

    # AI 피드백
    if "ai_feedback" in result:
        show_ai_feedback(result["ai_feedback"])

    # 추천 학습 경로
    st.markdown("### 🎯 추천 학습 방향")
    recommendations = get_recommendations(result["final_level"], result["sub_level"])
    st.success(recommendations)

    # 하단 버튼
    st.markdown("---")
    # 레벨 결과를 자동으로 프로필에 저장
    try:
        profile_manager = ProfileManager()
        profile_manager.update_level_from_test(result['display_level'])
        st.success("✅ 레벨이 프로필에 저장되었습니다!")
    except Exception as e:
        st.warning(f"프로필 저장 실패: {e}")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 대시보드로 돌아가기", use_container_width=True, type="primary"):
            st.switch_page("pages/dashboard.py")
    with col2:
        if st.button("🔄 테스트 다시 하기", use_container_width=True):
            # 세션 초기화
            st.session_state.test_session = None
            st.session_state.initialized = False
            st.session_state.show_result = False
            st.rerun()


def show_ai_feedback(ai_feedback):
    """AI 피드백 표시"""
    st.markdown("---")
    st.markdown("### 🤖 AI 상세 피드백 (GPT-4o mini)")

    # 5가지 평가 지표
    st.markdown("#### 📊 평가 점수")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("문법 정확도", f"{ai_feedback.grammar_accuracy}/5")
    with col2:
        st.metric("구문 복잡도", f"{ai_feedback.syntax_complexity}/5")
    with col3:
        st.metric("어휘 범위", f"{ai_feedback.vocabulary_range}/5")
    with col4:
        st.metric("유창성", f"{ai_feedback.fluency_cohesion}/5")
    with col5:
        st.metric("과제 적합성", f"{ai_feedback.task_relevance}/5")

    # 전체 평균
    avg_score = (
        ai_feedback.grammar_accuracy
        + ai_feedback.syntax_complexity
        + ai_feedback.vocabulary_range
        + ai_feedback.fluency_cohesion
        + ai_feedback.task_relevance
    ) / 5
    st.metric("전체 평균", f"{avg_score:.1f}/5")

    # 각 항목별 상세 코멘트
    with st.expander("📝 문법 정확도 상세"):
        st.write(ai_feedback.grammar_comment)

    with st.expander("📐 구문 복잡도 상세"):
        st.write(ai_feedback.syntax_comment)

    with st.expander("📚 어휘 범위 상세"):
        st.write(ai_feedback.vocabulary_comment)

    with st.expander("🌊 유창성/응집성 상세"):
        st.write(ai_feedback.fluency_comment)

    with st.expander("🎯 과제 적합성 상세"):
        st.write(ai_feedback.task_comment)

    # 종합 의견
    st.markdown("#### 💬 종합 평가")
    st.info(ai_feedback.overall_comment)

    # 강점과 개선점
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ✅ 강점")
        if ai_feedback.strengths:
            for strength in ai_feedback.strengths:
                st.success(f"• {strength}")
        else:
            st.write("피드백이 없습니다.")

    with col2:
        st.markdown("#### 📈 개선할 점")
        if ai_feedback.improvements:
            for improvement in ai_feedback.improvements:
                st.warning(f"• {improvement}")
        else:
            st.write("피드백이 없습니다.")


def get_recommendations(level: str, sub_level: str) -> str:
    """레벨별 학습 추천"""
    recommendations = {
        "A2": {
            "초반": "기본 문법과 일상 어휘를 더 연습하세요. 간단한 대화 연습이 도움이 될 것입니다.",
            "중반": "다양한 시제와 접속사를 활용한 문장 연습을 시작하세요.",
            "후반": "B1 레벨로 올라가기 위해 과거 경험 서술과 이유 설명 연습을 하세요.",
        },
        "B1": {
            "초반": "복잡한 문장 구조와 다양한 표현을 익히세요. 경험과 의견을 더 상세히 표현하는 연습을 하세요.",
            "중반": "추상적인 주제에 대한 의견 제시 연습을 시작하세요.",
            "후반": "B2 레벨로 올라가기 위해 논리적 전개와 복잡한 논증 연습을 하세요.",
        },
        "B2": {
            "초반": "다양한 주제에 대해 심도 있는 의견을 제시하는 연습을 하세요.",
            "중반": "복잡한 문법 구조와 고급 어휘를 활용한 글쓰기 연습을 계속하세요.",
            "후반": "C1 레벨로 올라가기 위해 학술적/전문적 주제에 대한 논증 능력을 키우세요.",
        },
        "C1": {
            "초반": "유창성을 높이고 다양한 담화 상황에서의 적절한 표현을 익히세요.",
            "중반": "복잡한 사회적, 학문적 주제에 대한 토론 능력을 더욱 발전시키세요.",
            "후반": "원어민 수준의 뉘앙스와 문화적 맥락을 이해하는 데 집중하세요.",
        },
    }

    return recommendations.get(level, {}).get(
        sub_level, "꾸준한 연습으로 실력을 향상시켜 나가세요!"
    )


# =============================================================================
# 앱 실행
# =============================================================================

if __name__ == "__main__":
    main()
