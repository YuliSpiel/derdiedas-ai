"""
학습 세션 페이지

단계별 학습 플로우:
1. 개념 설명 (독일어/한국어 토글)
2. 퀴즈 (5문제 순차적)
3. 적응형 재시도 (필요시)
4. 작문 과제
5. 완료 화면
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime
import uuid

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from models import ProfileManager
from models.learning_cycle import LearningSession, LearningStage
from learning.topic_selector import TopicSelector
from learning.content_generator import LearningContentGenerator
from learning.writing_feedback import WritingFeedbackGenerator
from services.learning_service import get_learning_service

# =============================================================================
# 페이지 설정
# =============================================================================

st.set_page_config(
    page_title="학습 중",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }

    .concept-box {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 1rem 0;
    }

    .example-box {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
    }

    .quiz-question {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }

    .progress-bar {
        height: 8px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 세션 상태 초기화
# =============================================================================

def init_session_state():
    """세션 상태 초기화"""
    if "learning_session" not in st.session_state:
        st.session_state.learning_session = None
    if "learning_content" not in st.session_state:
        st.session_state.learning_content = None
    if "current_quiz_index" not in st.session_state:
        st.session_state.current_quiz_index = 0
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "show_korean" not in st.session_state:
        st.session_state.show_korean = False
    if "writing_feedback" not in st.session_state:
        st.session_state.writing_feedback = None
    if "selected_skill_id" not in st.session_state:
        st.session_state.selected_skill_id = None


# =============================================================================
# 1. 개념 설명 단계
# =============================================================================

def show_concept_stage():
    """개념 설명 화면"""
    content = st.session_state.learning_content

    st.markdown("## 📖 개념 설명")

    # 진행률
    st.progress(0.25)
    st.caption("1단계 / 4단계: 개념 학습")

    st.markdown("---")

    # 독일어/한국어 토글
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🇩🇪 독일어", use_container_width=True,
                    type="primary" if not st.session_state.show_korean else "secondary"):
            st.session_state.show_korean = False
            st.rerun()
    with col2:
        if st.button("🇰🇷 한국어", use_container_width=True,
                    type="primary" if st.session_state.show_korean else "secondary"):
            st.session_state.show_korean = True
            st.rerun()

    # 개념 설명 표시
    with st.container(border=True):
        if st.session_state.show_korean:
            st.markdown(content["concept_ko"])
        else:
            st.markdown(content["concept_de"])

    # 예문
    st.markdown("### 📚 예문")
    for idx, example in enumerate(content["examples"], 1):
        with st.container(border=True):
            st.markdown(f"**{idx}.** {example['de']}")
            st.caption(example['ko'])

    # 다음 단계 버튼
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶️ 문제 풀기", use_container_width=True, type="primary"):
            st.session_state.learning_session.current_stage = LearningStage.QUIZ
            st.session_state.current_quiz_index = 0
            st.session_state.quiz_answers = {}
            st.session_state.quiz_retry_count = {}
            st.rerun()


# =============================================================================
# 2. 퀴즈 단계
# =============================================================================

def show_quiz_stage():
    """퀴즈 화면"""
    content = st.session_state.learning_content

    # 세션 상태 초기화
    if "quiz_checked" not in st.session_state:
        st.session_state.quiz_checked = {}
    if "quiz_retry_count" not in st.session_state:
        st.session_state.quiz_retry_count = {}  # 문제별 재시도 횟수

    # 필요한 문제 수 결정
    total_needed = 5
    if st.session_state.current_quiz_index >= 5:
        # 추가 문제 단계
        total_needed = 7

    questions = content["quiz_questions"][:total_needed]
    current_idx = st.session_state.current_quiz_index

    # 진행률
    progress = 0.25 + (0.25 * (min(current_idx, 5) / 5))
    st.progress(progress)
    st.caption(f"2단계 / 4단계: 문제 풀기 ({min(current_idx + 1, total_needed)}/{total_needed})")

    st.markdown("---")

    # 모든 문제 완료 확인
    if current_idx >= len(questions):
        show_quiz_results(len(questions))
        return

    # 현재 문제만 표시
    question = questions[current_idx]
    question_key = f"q_{current_idx}"

    st.markdown(f"### 문제 {current_idx + 1}")

    with st.container(border=True):
        # 문제 텍스트만 표시 (정답/선택지 제외)
        # GPT가 괄호 안에 정답을 넣을 수 있으므로 제거
        question_text = question['question']
        # 괄호 부분 제거 (예: "__ Katze (die/der/das)" -> "__ Katze")
        if '(' in question_text:
            question_text = question_text.split('(')[0].strip()

        st.markdown(f"**{question_text}**")

        # 답변 입력
        if question['type'] == 'fill_blank':
            user_answer = st.text_input(
                "답변을 입력하세요",
                key=f"answer_{question_key}",
                placeholder="답을 입력하세요..."
            )
        else:  # multiple_choice
            user_answer = st.radio(
                "답을 선택하세요",
                options=question['options'],
                key=f"answer_{question_key}",
                index=None
            )

        # 확인/다음 버튼 로직
        if st.session_state.quiz_checked.get(question_key, False):
            # 이미 확인한 상태 - 피드백 표시
            answer_data = st.session_state.quiz_answers.get(question['id'])

            if answer_data and answer_data['correct']:
                # 정답인 경우
                st.success("✅ 정답입니다!")
                st.info(f"💡 {question['explanation']}")

                if st.button("➡️ 다음 문제", use_container_width=True, type="primary"):
                    st.session_state.current_quiz_index += 1
                    st.session_state.quiz_checked[question_key] = False
                    st.rerun()
            else:
                # 오답인 경우
                retry_count = st.session_state.quiz_retry_count.get(question_key, 0)

                if retry_count == 0:
                    # 첫 번째 오답 - 재시도 기회 제공
                    st.error("❌ 틀렸습니다. 다시 시도해보세요!")
                    # 힌트 표시 (정답 없는 힌트)
                    hint = question.get('hint', question.get('explanation', '문제를 다시 읽어보세요'))
                    st.warning(f"💡 힌트: {hint}")

                    # 다시 풀기 버튼
                    if st.button("🔄 다시 입력하기", use_container_width=True):
                        st.session_state.quiz_checked[question_key] = False
                        st.session_state.quiz_retry_count[question_key] = 1
                        if question['id'] in st.session_state.quiz_answers:
                            del st.session_state.quiz_answers[question['id']]
                        st.rerun()
                else:
                    # 두 번째 오답 - 정답 공개하고 넘어가기
                    st.error("❌ 틀렸습니다.")
                    st.info(f"**정답:** {question['correct_answer']}")
                    st.warning(f"💡 설명: {question['explanation']}")

                    # 오답으로 기록 (correct=False 유지)
                    if st.button("➡️ 다음 문제", use_container_width=True, type="primary"):
                        st.session_state.current_quiz_index += 1
                        st.session_state.quiz_checked[question_key] = False
                        st.session_state.quiz_retry_count[question_key] = 0  # 리셋
                        st.rerun()
        else:
            # 아직 확인 안한 상태 - 확인 버튼
            if st.button("✅ 확인", use_container_width=True, type="primary", disabled=not user_answer):
                if not user_answer:
                    st.error("답변을 입력해주세요!")
                else:
                    # 정답 확인
                    is_correct = user_answer.strip().lower() == question['correct_answer'].strip().lower()

                    st.session_state.quiz_answers[question['id']] = {
                        'user_answer': user_answer,
                        'correct': is_correct,
                        'question': question
                    }
                    st.session_state.quiz_checked[question_key] = True
                    st.rerun()


def show_quiz_results(total_questions: int):
    """퀴즈 결과 화인 및 적응형 로직"""
    answers = st.session_state.quiz_answers
    correct_count = sum(1 for a in answers.values() if a['correct'])
    accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0

    st.markdown("## 📊 문제 풀이 결과")

    with st.container(border=True):
        st.metric("정답률", f"{accuracy:.0f}%", f"{correct_count}/{total_questions}")

    st.markdown("---")

    # 적응형 로직
    if accuracy < 40:
        st.warning("⚠️ 정답률이 40% 미만입니다.")

        if total_questions == 5:
            # 첫 5문제 - 2문제 더 풀기
            st.info("💪 조금 더 연습이 필요해요! 2문제를 더 풀어봅시다.")

            if st.button("➕ 추가 문제 풀기 (2문제)", use_container_width=True, type="primary"):
                # 6-7번 문제 추가
                st.session_state.current_quiz_index = 5
                st.rerun()
        else:
            # 7문제까지 풀었는데도 40% 미만
            st.error("😢 아직 개념이 확실하지 않은 것 같아요.")
            st.info("개념 설명으로 돌아가서 다시 학습해봅시다!")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 개념 학습으로 돌아가기", use_container_width=True, type="primary"):
                    # 퀴즈 리셋
                    st.session_state.learning_session.current_stage = LearningStage.CONCEPT
                    st.session_state.current_quiz_index = 0
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_retry_count = {}
                    st.rerun()
            with col2:
                if st.button("🏠 대시보드로", use_container_width=True):
                    st.switch_page("pages/dashboard.py")
    else:
        # 40% 이상 - 다음 단계로
        st.success("🎉 잘하셨습니다!")

        if st.button("▶️ 작문 과제로 이동", use_container_width=True, type="primary"):
            st.session_state.learning_session.current_stage = LearningStage.WRITING
            st.rerun()


# =============================================================================
# 3. 작문 과제 단계
# =============================================================================

def show_writing_stage():
    """작문 과제 화면"""
    content = st.session_state.learning_content
    task = content["writing_task"]

    st.progress(0.75)
    st.caption("3단계 / 4단계: 작문 과제")

    st.markdown("## ✍️ 작문 과제")
    st.markdown("---")

    with st.container(border=True):
        st.markdown(f"**{task['prompt_ko']}**")
        st.caption(f"🇩🇪 {task['prompt_de']}")
        st.caption(f"최소 {task['min_sentences']}문장 이상 작성해주세요.")

    # 작문 입력
    user_writing = st.text_area(
        "작문",
        height=200,
        placeholder="여기에 독일어로 작성하세요...",
        label_visibility="collapsed",
        key="user_writing_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 제출하고 피드백 받기", use_container_width=True, type="primary"):
            if not user_writing.strip():
                st.error("작문을 입력해주세요!")
            else:
                # 피드백 생성
                with st.spinner("AI가 피드백을 생성하는 중..."):
                    try:
                        # API 우선 + 폴백 서비스 사용
                        learning_service = get_learning_service()
                        profile_manager = ProfileManager()
                        profile = profile_manager.load_profile()

                        feedback = learning_service.generate_writing_feedback(
                            user_text=user_writing,
                            task_prompt=task['prompt_ko'],
                            target_grammar=task['target_grammar'],
                            user_cefr_level=profile.level.split('-')[0] if '-' in profile.level else profile.level
                        )

                        st.session_state.writing_feedback = feedback
                        st.session_state.user_writing = user_writing
                        st.session_state.learning_session.current_stage = LearningStage.COMPLETED
                        st.rerun()
                    except Exception as e:
                        st.error(f"피드백 생성 중 오류가 발생했습니다: {e}")
    with col2:
        if st.button("⬅️ 뒤로", use_container_width=True):
            st.session_state.learning_session.current_stage = LearningStage.QUIZ
            st.rerun()


# =============================================================================
# 4. 완료 화면
# =============================================================================

def show_completion_stage():
    """학습 완료 화면"""
    st.progress(1.0)
    st.caption("완료! 🎉")

    st.markdown("## 🎉 학습 완료!")

    # 작문 피드백 표시
    if st.session_state.writing_feedback:
        feedback = st.session_state.writing_feedback

        st.markdown("### ✍️ 작문 피드백")

        # 점수
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("문법", f"{feedback['grammar_score']}/5")
        with col2:
            st.metric("어휘", f"{feedback['vocabulary_score']}/5")
        with col3:
            st.metric("과제 완성도", f"{feedback['task_completion_score']}/5")

        st.markdown("---")

        # 긍정적 피드백
        if feedback.get('positive_feedback'):
            with st.container(border=True):
                st.markdown("#### ✨ 잘한 점")
                for item in feedback['positive_feedback']:
                    st.success(f"• {item}")

        # 교정 사항
        if feedback.get('corrections') and len(feedback['corrections']) > 0:
            with st.container(border=True):
                st.markdown("#### 🔧 교정 사항")
                for correction in feedback['corrections']:
                    st.error(f"**원문:** {correction['original']}")
                    st.success(f"**교정:** {correction['corrected']}")
                    st.info(f"💡 {correction['explanation']}")
                    st.markdown("---")

        # 개선 팁
        if feedback.get('improvement_tips'):
            with st.container(border=True):
                st.markdown("#### 💡 다음 학습을 위한 조언")
                for tip in feedback['improvement_tips']:
                    st.warning(f"• {tip}")

    st.markdown("---")

    # 보상
    with st.container(border=True):
        st.markdown("### 🏆 보상")
        st.success("✨ 스탬프 +1 획득!")

        # 숙련도 업데이트 (한 번만 실행)
        if "proficiency_updated" not in st.session_state or not st.session_state.proficiency_updated:
            try:
                # API 우선 + 폴백 서비스 사용
                learning_service = get_learning_service()
                profile_manager = ProfileManager()
                profile = profile_manager.load_profile()

                skill_id = st.session_state.selected_skill_id
                session = st.session_state.learning_session

                if skill_id and st.session_state.writing_feedback and session:
                    proficiency_change = st.session_state.writing_feedback.get('skill_proficiency_change', 0)
                    current_proficiency = profile.skill_proficiency.get(skill_id, 0)
                    new_proficiency = min(100, max(0, current_proficiency + proficiency_change))

                    # 학습 완료 처리 (API 통합 호출)
                    result = learning_service.complete_learning(
                        notebook_id=session.notebook_id,
                        skill_proficiency={skill_id: new_proficiency},
                        learning_count_increment=skill_id,
                        stamps_increment=1
                    )

                    if result.get('success'):
                        st.info(f"📈 스킬 숙련도: {current_proficiency:.1f} → {new_proficiency:.1f} ({proficiency_change:+.1f})")
                        st.success(f"✨ 스탬프 획득! (총 {result.get('updated_stamps', 0)}개)")
                        st.success("✨ 추천 노트북이 갱신되었습니다")
                    else:
                        st.warning("학습 완료 처리 중 일부 오류가 발생했습니다.")
                else:
                    print(f"⚠️ 학습 완료 정보 누락: skill_id={skill_id}, feedback={st.session_state.writing_feedback is not None}, session={session}")

                st.session_state.proficiency_updated = True

            except Exception as e:
                st.error(f"프로필 업데이트 오류: {e}")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 대시보드로", use_container_width=True, type="primary"):
            # 리셋
            st.session_state.learning_session = None
            st.session_state.learning_content = None
            st.session_state.writing_feedback = None
            st.session_state.proficiency_updated = False
            st.switch_page("pages/dashboard.py")
    with col2:
        if st.button("🔄 다시 학습하기", use_container_width=True):
            # 세션 리셋
            st.session_state.learning_session = None
            st.session_state.learning_content = None
            st.session_state.writing_feedback = None
            st.session_state.proficiency_updated = False
            st.rerun()


# =============================================================================
# 메인
# =============================================================================

def main():
    init_session_state()

    # 학습 세션이 없으면 생성
    if st.session_state.learning_session is None:
        st.markdown("## 🚀 학습 준비 중...")

        with st.spinner("주제를 선정하고 학습 자료를 생성하는 중..."):
            # 대시보드에서 전달받은 노트북 ID 사용
            notebook_id = st.session_state.get("selected_notebook_id", "test-notebook-id")
            session = create_learning_session(notebook_id)

            if session:
                st.session_state.learning_session = session
                st.rerun()
            else:
                st.error("학습 세션을 생성할 수 없습니다.")
                if st.button("대시보드로 돌아가기"):
                    st.switch_page("pages/dashboard.py")
                return

    # 현재 단계에 따라 화면 표시
    session = st.session_state.learning_session

    if session.current_stage == LearningStage.CONCEPT:
        show_concept_stage()
    elif session.current_stage == LearningStage.QUIZ:
        show_quiz_stage()
    elif session.current_stage == LearningStage.WRITING:
        show_writing_stage()
    elif session.current_stage == LearningStage.COMPLETED:
        show_completion_stage()


def create_learning_session(notebook_id: str) -> LearningSession:
    """학습 세션 생성"""
    try:
        # 1. 프로필 로드
        profile_manager = ProfileManager()
        profile = profile_manager.load_profile()

        # 2. 노트북 정보 로드
        notebooks = profile_manager.load_notebooks()
        current_notebook = next((nb for nb in notebooks if nb.id == notebook_id), None)

        if not current_notebook:
            st.error("노트북을 찾을 수 없습니다.")
            return None

        # 3. 주제 선정: 추천 노트북 vs 사용자 노트북
        selector = TopicSelector()

        if current_notebook.is_recommended:
            # 추천 노트북: 적응형 주제 선정 (숙련도 기반)
            selected_skill = selector.select_topic(
                user_proficiency=profile.skill_proficiency,
                learning_count=profile.skill_learning_count,
                domain_filter="Grammar"
            )

            if not selected_skill:
                st.error("선택 가능한 주제가 없습니다.")
                return None

            st.success(f"📚 적응형 주제: {selector.get_skill_info(selected_skill)['name']}")

        else:
            # 사용자 노트북: 고정 스킬
            if not current_notebook.skill_id:
                st.error("노트북에 스킬 정보가 없습니다.")
                return None

            selected_skill = current_notebook.skill_id
            st.success(f"📚 선택한 주제: {selector.get_skill_info(selected_skill)['name']}")

        skill_info = selector.get_skill_info(selected_skill)

        # 스킬 ID 저장
        st.session_state.selected_skill_id = selected_skill

        # 4. 컨텐츠 생성 (사용자 관심사/목표 반영) - API 우선 + 폴백
        learning_service = get_learning_service()
        content = learning_service.generate_content(
            skill_id=selected_skill,
            skill_name=skill_info['name'],
            skill_description=skill_info.get('name', ''),
            user_cefr_level=profile.level.split('-')[0] if '-' in profile.level else profile.level,
            user_interests=profile.interests,  # 관심사 반영
            user_goals=profile.goals  # 목표 반영
        )

        st.session_state.learning_content = content

        # 5. 세션 생성
        session = LearningSession(
            session_id=str(uuid.uuid4()),
            notebook_id=notebook_id,
            topic=skill_info['name']
        )

        return session

    except Exception as e:
        st.error(f"세션 생성 오류: {e}")
        return None


if __name__ == "__main__":
    main()
