"""
# CEFR(유럽 언어 공통 기준, Common European Framework of Reference for Languages) 기반
# 사용자 어학수준 평가 기능
#
# 작문 기반 적응형 레벨 테스트:
# - 5개의 작문 과제를 통해 사용자의 독일어 수준 평가
# - 답변에 따라 다음 질문 난이도를 조정하는 적응형 시스템
# - CEFR 라벨링된 코퍼스와의 유사도 비교를 통한 레벨 판정
# - A2~C1 각 레벨을 초반/중반/후반으로 세분화
#
# 데이터 출처:
# MERLIN German Corpus (CC BY-SA 4.0)
# Boyd, A., Hana, J., Nicolas, L., Meurers, D., Wisniewski, K., Abel, A.,
# Schöne, K., Stindlová, B., & Vettori, C. (2014).
# The MERLIN corpus: Learner language and the CEFR.
# In Proceedings of LREC'14 (pp. 1281-1288).
# https://huggingface.co/datasets/UniversalCEFR/merlin_de

"""

# 환경 설정 및 경고 비활성화
import warnings

warnings.filterwarnings("ignore")

import os
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import json

# 프로젝트 캐시 설정
project_cache = "./models_cache"
os.environ["HF_HOME"] = project_cache
print(f"✅ 프로젝트 캐시 활성화: {os.path.abspath(project_cache)}")

# Tokenizers 병렬 처리 경고 비활성화
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# 캐시 디렉토리 확인
cache_dir = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
print(f"📂 모델 저장 위치: {cache_dir}")

print("✅ 환경 설정 완료")


# =============================================================================
# 1. 데이터 구조 정의
# =============================================================================


class CEFRLevel(Enum):
    """CEFR 레벨 정의"""

    A2 = 1
    B1 = 2
    B2 = 3
    C1 = 4


class SubLevel(Enum):
    """세부 레벨 (초반/중반/후반)"""

    EARLY = "초반"
    MID = "중반"
    LATE = "후반"


@dataclass
class Question:
    """작문 과제 문항"""

    id: str
    level: CEFRLevel
    topic: str
    intent: str
    text: str


@dataclass
class DetailedFeedback:
    """GPT-4o mini 기반 상세 피드백"""

    grammar_accuracy: int  # 0-5
    grammar_comment: str
    syntax_complexity: int  # 0-5
    syntax_comment: str
    vocabulary_range: int  # 0-5
    vocabulary_comment: str
    fluency_cohesion: int  # 0-5
    fluency_comment: str
    task_relevance: int  # 0-5
    task_comment: str
    overall_comment: str
    strengths: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)


@dataclass
class UserResponse:
    """사용자 답변"""

    question_id: str
    text: str
    estimated_level: Optional[CEFRLevel] = None
    similarity_score: float = 0.0
    detailed_feedback: Optional[DetailedFeedback] = None


# =============================================================================
# 2. 질문 뱅크 정의
# =============================================================================

QUESTION_BANK = {
    CEFRLevel.A2: [
        Question(
            "A2-1",
            CEFRLevel.A2,
            "자기소개",
            "기본 정보 표현",
            "Wie heißt du, und woher kommst du?",
        ),
        Question(
            "A2-2",
            CEFRLevel.A2,
            "일상/취미",
            "선호 표현",
            "Was machst du gern in deiner Freizeit?",
        ),
        Question(
            "A2-3",
            CEFRLevel.A2,
            "가족/친구",
            "단순 묘사",
            "Erzähl mir etwas über deine Familie oder deine Freunde.",
        ),
        Question(
            "A2-4",
            CEFRLevel.A2,
            "일상 루틴",
            "시제·빈도 표현",
            "Wie sieht ein normaler Tag bei dir aus?",
        ),
        Question(
            "A2-5",
            CEFRLevel.A2,
            "음식/날씨",
            "감정 표현",
            "Was isst du am liebsten, wenn es kalt ist?",
        ),
    ],
    CEFRLevel.B1: [
        Question(
            "B1-1",
            CEFRLevel.B1,
            "학습 어려움",
            "이유·의견 제시",
            "Was findest du schwierig beim Deutschlernen? Warum?",
        ),
        Question(
            "B1-2",
            CEFRLevel.B1,
            "여행 경험",
            "과거 서술",
            "Erzähl mir von einer schönen Reise, die du gemacht hast.",
        ),
        Question(
            "B1-3",
            CEFRLevel.B1,
            "취미 이유",
            "추상적 설명",
            "Warum ist dein Hobby wichtig für dich?",
        ),
        Question(
            "B1-4",
            CEFRLevel.B1,
            "인간관계",
            "비교·감정",
            "Wie beschreibst du eine gute Freundschaft?",
        ),
        Question(
            "B1-5",
            CEFRLevel.B1,
            "생활환경",
            "장단점 서술",
            "Was gefällt dir an deiner Stadt, und was nicht?",
        ),
    ],
    CEFRLevel.B2: [
        Question(
            "B2-1",
            CEFRLevel.B2,
            "미래 계획",
            "가치관·계획",
            "Wie stellst du dir dein Leben in fünf Jahren vor?",
        ),
        Question(
            "B2-2",
            CEFRLevel.B2,
            "사회적 주제",
            "의견 제시",
            "Findest du, dass Technologie unser Leben besser oder schlechter macht? Warum?",
        ),
        Question(
            "B2-3",
            CEFRLevel.B2,
            "문화/예술",
            "견해 설명",
            "Welche Rolle spielt Musik oder Kunst in deinem Leben?",
        ),
        Question(
            "B2-4",
            CEFRLevel.B2,
            "학습 전략",
            "자기 성찰",
            "Was machst du, wenn du etwas Neues lernen möchtest?",
        ),
        Question(
            "B2-5",
            CEFRLevel.B2,
            "일·진로",
            "목표 설명",
            "Welche Arbeit würdest du gern machen, und warum?",
        ),
    ],
    CEFRLevel.C1: [
        Question(
            "C1-1",
            CEFRLevel.C1,
            "사회 문제",
            "논증",
            "Manche sagen, dass soziale Medien die Gesellschaft verändern. Was denkst du darüber?",
        ),
        Question(
            "C1-2",
            CEFRLevel.C1,
            "문화 비교",
            "분석",
            "Wie unterscheiden sich deiner Meinung nach die koreanische und die deutsche Kultur?",
        ),
        Question(
            "C1-3",
            CEFRLevel.C1,
            "가정/추론",
            "가정법",
            "Wenn du die Möglichkeit hättest, überall zu leben, wo würdest du wohnen – und warum?",
        ),
        Question(
            "C1-4",
            CEFRLevel.C1,
            "인생 철학",
            "자기 통찰",
            'Was bedeutet "Glück" für dich persönlich?',
        ),
        Question(
            "C1-5",
            CEFRLevel.C1,
            "비판적 평가",
            "견해 논증",
            "Findest du, dass Erfolg wichtiger als Zufriedenheit ist? Begründe deine Meinung.",
        ),
    ],
}


# 첫 질문은 항상 A2-1
INITIAL_QUESTION = QUESTION_BANK[CEFRLevel.A2][0]


# =============================================================================
# 3. CEFR 라벨링된 코퍼스 로드 및 임베딩
# =============================================================================


class CEFRCorpusLoader:
    """CEFR 라벨링된 독일어 코퍼스 로더"""

    def __init__(self):
        self.corpus_data = None
        self.embeddings = None
        self.model = None
        self.tokenizer = None

    def load_corpus(self):
        """
        MERLIN 독일어 코퍼스 로드

        MERLIN (Multilingual platform for European Reference Levels: Interlanguage Exploration)
        Source: https://huggingface.co/datasets/UniversalCEFR/merlin_de
        License: CC BY-SA 4.0

        Citation:
        Boyd, A., et al. (2014). The MERLIN corpus: Learner language and the CEFR.
        In Proceedings of LREC'14 (pp. 1281-1288).
        """
        from datasets import load_dataset
        import os
        from pathlib import Path

        # 프로젝트 루트에 캐시 디렉토리 설정
        project_root = Path(__file__).parent.parent.parent

        # notebooks/models_cache 경로 우선 사용 (기존 캐시가 있을 수 있음)
        notebooks_cache = project_root / "notebooks" / "models_cache" / "datasets"
        root_cache = project_root / "models_cache" / "datasets"

        # notebooks에 캐시가 있으면 그것 사용, 없으면 root 사용
        if notebooks_cache.exists():
            cache_dir = notebooks_cache
        else:
            cache_dir = root_cache
            cache_dir.mkdir(parents=True, exist_ok=True)

        print("📚 CEFR 라벨링된 독일어 코퍼스 로딩 중...")
        print("📄 MERLIN Corpus (CC BY-SA 4.0) - Boyd et al. (2014)")
        print(f"💾 캐시 경로: {cache_dir}")

        dataset = load_dataset(
            "UniversalCEFR/merlin_de",
            trust_remote_code=True,
            cache_dir=str(cache_dir)
        )

        # 데이터 구조 확인 및 정리
        self.corpus_data = {
            "A2": [],
            "B1": [],
            "B2": [],
            "C1": [],
        }

        # 데이터셋에서 각 레벨별로 텍스트 추출
        print("🔍 데이터셋 구조 확인 중...")
        sample_processed = False

        for split in dataset.keys():
            print(f"  Split: {split}")
            for item in dataset[split]:
                # 첫 번째 아이템으로 구조 확인
                if not sample_processed:
                    print(f"  📋 데이터 구조 샘플: {list(item.keys())}")
                    print(f"  📝 첫 번째 아이템 예시: {item}")
                    sample_processed = True

                # 다양한 필드명 시도
                level = None
                text = None

                # 레벨 필드 찾기
                for level_key in ["cefr", "CEFR", "level", "Level", "label"]:
                    if level_key in item:
                        level = str(item[level_key]).upper().strip()
                        break

                # 텍스트 필드 찾기
                for text_key in ["text", "Text", "sentence", "content"]:
                    if text_key in item:
                        text = str(item[text_key]).strip()
                        break

                # 레벨 정규화 (A2, B1, B2, C1만 추출)
                if level and text:
                    # "A2-1" -> "A2", "B1+" -> "B1" 등 정규화
                    for target_level in ["A2", "B1", "B2", "C1"]:
                        if target_level in level:
                            self.corpus_data[target_level].append(text)
                            break

        # 통계 출력
        print("\n📊 코퍼스 통계:")
        total = 0
        for level, texts in self.corpus_data.items():
            count = len(texts)
            total += count
            print(f"  {level}: {count}개 문장")

        print(f"  총합: {total}개 문장")

        # 데이터가 없으면 경고
        if total == 0:
            print("⚠️  경고: 코퍼스 데이터를 로드하지 못했습니다!")
            print("⚠️  샘플 데이터로 대체합니다.")
            self._load_sample_corpus()

        return self.corpus_data

    def _load_sample_corpus(self):
        """샘플 코퍼스 데이터 (데이터셋 로드 실패 시 대체용)"""
        print("📝 샘플 독일어 문장 로딩 중...")

        self.corpus_data = {
            "A2": [
                "Ich heiße Maria und komme aus Korea.",
                "Mein Hobby ist Musik hören.",
                "Ich wohne in Seoul mit meiner Familie.",
                "Am Wochenende gehe ich gern spazieren.",
                "Ich trinke gern Kaffee am Morgen.",
            ] * 100,  # 500개로 복제
            "B1": [
                "Ich finde Deutschlernen interessant, weil die Grammatik logisch ist.",
                "Letztes Jahr habe ich Deutschland besucht und viele neue Leute kennengelernt.",
                "Mein Hobby macht mir Spaß, weil ich dabei entspannen kann.",
                "Eine gute Freundschaft bedeutet für mich Vertrauen und gegenseitiges Verständnis.",
                "An meiner Stadt gefällt mir die gute Infrastruktur, aber sie ist manchmal zu laut.",
            ] * 100,
            "B2": [
                "In fünf Jahren möchte ich ein eigenes Unternehmen gründen und internationale Erfahrungen sammeln.",
                "Technologie macht unser Leben effizienter, aber wir sollten auf die Balance zwischen Online und Offline achten.",
                "Musik spielt eine wichtige Rolle in meinem Leben, weil sie meine Emotionen ausdrücken kann.",
                "Wenn ich etwas Neues lernen möchte, recherchiere ich zuerst online und probiere dann praktisch aus.",
                "Ich würde gern als Designer arbeiten, weil ich kreativ sein und Menschen helfen möchte.",
            ] * 100,
            "C1": [
                "Soziale Medien haben die Gesellschaft grundlegend verändert, indem sie neue Kommunikationsformen ermöglichen, aber auch Polarisierung fördern können.",
                "Die koreanische und deutsche Kultur unterscheiden sich in der Arbeitsethik und im Umgang mit Hierarchien, wobei beide Stärken und Schwächen haben.",
                "Wenn ich überall leben könnte, würde ich eine Stadt mit kultureller Vielfalt und guter Lebensqualität wählen, da dies persönliches Wachstum fördert.",
                "Glück bedeutet für mich die Fähigkeit, im gegenwärtigen Moment zufrieden zu sein, unabhängig von äußeren Umständen.",
                "Erfolg und Zufriedenheit schließen sich nicht aus, aber Zufriedenheit ist nachhaltiger, da sie von inneren Werten abhängt.",
            ] * 100,
        }

    def load_embedder(self):
        """독일어 문장 임베딩 모델 로드"""
        from sentence_transformers import SentenceTransformer

        print("\n🤖 독일어 임베딩 모델 로딩 중...")
        # 독일어에 특화된 문장 임베딩 모델
        self.model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )
        print("✅ 임베딩 모델 로딩 완료")
        return self.model

    def create_corpus_embeddings(self):
        """코퍼스의 모든 문장에 대한 임베딩 생성"""
        if self.corpus_data is None:
            self.load_corpus()
        if self.model is None:
            self.load_embedder()

        print("\n🔄 코퍼스 임베딩 생성 중...")
        self.embeddings = {}

        for level, texts in self.corpus_data.items():
            if texts:
                # 각 레벨별 샘플링 (너무 많으면 시간 소요)
                sample_size = min(500, len(texts))
                sampled_texts = np.random.choice(texts, sample_size, replace=False)

                print(f"  {level}: {len(sampled_texts)}개 문장 임베딩 중...")
                self.embeddings[level] = self.model.encode(
                    sampled_texts, show_progress_bar=True
                )

        print("✅ 코퍼스 임베딩 생성 완료")
        return self.embeddings


# =============================================================================
# 4. 유사도 기반 레벨 판정
# =============================================================================


class LevelEstimator:
    """사용자 답변의 레벨 추정"""

    def __init__(self, corpus_loader: CEFRCorpusLoader):
        self.corpus_loader = corpus_loader
        self.model = corpus_loader.model
        self.embeddings = corpus_loader.embeddings

    def estimate_level(self, user_text: str) -> Tuple[CEFRLevel, SubLevel, float]:
        """
        사용자 답변의 레벨 추정

        Returns:
            (CEFRLevel, SubLevel, confidence_score)
        """
        # 사용자 텍스트 임베딩
        user_embedding = self.model.encode([user_text])[0]

        # 각 레벨별 유사도 계산
        level_scores = {}
        for level_str, level_embeddings in self.embeddings.items():
            # 코사인 유사도 계산
            similarities = np.dot(level_embeddings, user_embedding) / (
                np.linalg.norm(level_embeddings, axis=1)
                * np.linalg.norm(user_embedding)
            )

            # 상위 10% 평균 유사도 사용
            top_k = max(10, int(len(similarities) * 0.1))
            top_similarities = np.partition(similarities, -top_k)[-top_k:]
            avg_similarity = np.mean(top_similarities)

            level_scores[level_str] = avg_similarity

        # 가장 높은 유사도를 가진 레벨 선택
        best_level_str = max(level_scores, key=level_scores.get)
        confidence = level_scores[best_level_str]

        # 문자열을 CEFRLevel enum으로 변환
        level_map = {
            "A2": CEFRLevel.A2,
            "B1": CEFRLevel.B1,
            "B2": CEFRLevel.B2,
            "C1": CEFRLevel.C1,
        }
        best_level = level_map[best_level_str]

        # 서브레벨 추정 (인접 레벨과의 점수 차이로 판단)
        sub_level = self._estimate_sublevel(level_scores, best_level_str)

        return best_level, sub_level, confidence

    def _estimate_sublevel(
        self, level_scores: Dict[str, float], current_level: str
    ) -> SubLevel:
        """서브레벨(초반/중반/후반) 추정"""
        level_order = ["A2", "B1", "B2", "C1"]
        current_idx = level_order.index(current_level)

        current_score = level_scores[current_level]

        # 이전 레벨과 다음 레벨의 점수
        prev_score = (
            level_scores[level_order[current_idx - 1]] if current_idx > 0 else 0
        )
        next_score = (
            level_scores[level_order[current_idx + 1]]
            if current_idx < len(level_order) - 1
            else 0
        )

        # 점수 차이로 서브레벨 판정
        gap_to_prev = current_score - prev_score
        gap_to_next = current_score - next_score

        if gap_to_prev < 0.05:  # 이전 레벨과 매우 가까움
            return SubLevel.EARLY
        elif gap_to_next < 0.05:  # 다음 레벨과 매우 가까움
            return SubLevel.LATE
        else:
            return SubLevel.MID


# =============================================================================
# 5. 적응형 질문 선택 알고리즘
# =============================================================================


class AdaptiveQuestionSelector:
    """사용자 답변에 따라 다음 질문을 선택하는 알고리즘"""

    def __init__(self, question_bank: Dict[CEFRLevel, List[Question]]):
        self.question_bank = question_bank
        self.used_questions = set()

    def select_next_question(
        self,
        current_question_num: int,
        estimated_level: CEFRLevel,
        response_history: List[UserResponse],
    ) -> Question:
        """
        다음 질문 선택

        Args:
            current_question_num: 현재 질문 번호 (1-4, 0은 get_current_question에서 처리)
            estimated_level: 방금 추정된 레벨
            response_history: 이전 답변 히스토리

        Returns:
            다음 질문
        """
        print(f"\n🎲 DEBUG: select_next_question() 호출")
        print(f"   current_question_num: {current_question_num}")
        print(f"   estimated_level: {estimated_level.name}")
        print(f"   used_questions: {self.used_questions}")

        # 이전 답변들의 평균 레벨 계산
        avg_level_value = np.mean(
            [resp.estimated_level.value for resp in response_history]
        )
        print(f"   평균 레벨 값: {avg_level_value:.2f}")

        # 목표 레벨 결정
        if current_question_num == 1:
            # 두 번째 질문: 첫 답변 기준으로 조정
            if estimated_level.value <= 1.5:  # A2 수준
                target_level = CEFRLevel.B1
            elif estimated_level.value <= 2.5:  # B1 수준
                target_level = CEFRLevel.B1
            else:
                target_level = CEFRLevel.B2
        else:
            # 세 번째 질문부터: 평균을 기준으로 적응형 선택
            if avg_level_value < 2.0:
                target_level = CEFRLevel.B1
            elif avg_level_value < 3.0:
                target_level = CEFRLevel.B2
            else:
                target_level = CEFRLevel.C1

        print(f"   목표 레벨: {target_level.name}")

        # 해당 레벨에서 사용하지 않은 질문 선택
        available_questions = [
            q
            for q in self.question_bank[target_level]
            if q.id not in self.used_questions
        ]
        print(f"   목표 레벨에서 사용 가능한 질문: {[q.id for q in available_questions]}")

        if not available_questions:
            # 사용 가능한 질문이 없으면 다른 레벨에서 선택
            print(f"   ⚠️  목표 레벨에 사용 가능한 질문이 없음, 다른 레벨 탐색 중...")
            for level in [CEFRLevel.B1, CEFRLevel.B2, CEFRLevel.C1, CEFRLevel.A2]:
                available_questions = [
                    q
                    for q in self.question_bank[level]
                    if q.id not in self.used_questions
                ]
                if available_questions:
                    print(f"   → {level.name}에서 {len(available_questions)}개 질문 발견")
                    break

        # 랜덤하게 하나 선택
        selected_question = np.random.choice(available_questions)
        self.used_questions.add(selected_question.id)
        print(f"   ✅ 선택된 질문: {selected_question.id}")

        return selected_question


# =============================================================================
# 6. GPT-4o mini 기반 상세 피드백
# =============================================================================


class AIFeedbackGenerator:
    """OpenAI GPT-4o mini를 활용한 상세 피드백 생성"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️  OPENAI_API_KEY가 설정되지 않았습니다. AI 피드백 기능이 비활성화됩니다.")
            self.enabled = False
        else:
            self.enabled = True

    def generate_feedback(
        self, questions: List[Question], responses: List[UserResponse]
    ) -> DetailedFeedback:
        """5개의 질문-답변 쌍을 종합 분석하여 상세 피드백 생성"""
        if not self.enabled:
            return self._get_fallback_feedback()

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            # 프롬프트 구성
            prompt = self._build_evaluation_prompt(questions, responses)

            # GPT-4o mini 호출
            print("\n🤖 AI 피드백 생성 중...")
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 독일어 교육 전문가입니다. CEFR 기준에 따라 독일어 작문을 평가하고 상세한 피드백을 제공합니다.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
            )

            # 응답 파싱
            result = json.loads(response.choices[0].message.content)
            print("✅ AI 피드백 생성 완료")

            return DetailedFeedback(
                grammar_accuracy=result.get("grammar_accuracy", 3),
                grammar_comment=result.get("grammar_comment", ""),
                syntax_complexity=result.get("syntax_complexity", 3),
                syntax_comment=result.get("syntax_comment", ""),
                vocabulary_range=result.get("vocabulary_range", 3),
                vocabulary_comment=result.get("vocabulary_comment", ""),
                fluency_cohesion=result.get("fluency_cohesion", 3),
                fluency_comment=result.get("fluency_comment", ""),
                task_relevance=result.get("task_relevance", 3),
                task_comment=result.get("task_comment", ""),
                overall_comment=result.get("overall_comment", ""),
                strengths=result.get("strengths", []),
                improvements=result.get("improvements", []),
            )

        except Exception as e:
            print(f"⚠️  AI 피드백 생성 실패: {e}")
            return self._get_fallback_feedback()

    def _build_evaluation_prompt(
        self, questions: List[Question], responses: List[UserResponse]
    ) -> str:
        """평가 프롬프트 구성"""
        qa_pairs = []
        for i, (q, r) in enumerate(zip(questions, responses), 1):
            qa_pairs.append(f"""
**질문 {i}:** {q.text}
**답변 {i}:** {r.text}
**추정 레벨:** {r.estimated_level.name}
""")

        prompt = f"""
다음은 독일어 레벨 테스트에서 학습자가 작성한 5개의 답변입니다.
각 답변을 분석하고, 아래 5가지 기준에 따라 0-5점으로 평가한 후 상세한 피드백을 제공해 주세요.

{''.join(qa_pairs)}

## 평가 기준

### 1. 문법 정확도 (grammar_accuracy: 0-5)
- 관사·성·수·격 일치 (der/die/das, ein/eine, den/dem/des 등)
- 전치사 지배 (zu/bei/in/nach + Dativ/Akkusativ)
- 동사 자리 (V2 어순, 종속절 V-final)
- 분리동사 위치 (aufstehen → steht...auf)
- 최상급 형태 (am schönsten, die beste)
- 시간-방법-장소 어순

### 2. 구문 복잡도 (syntax_complexity: 0-5)
- 종속절 사용 (weil, dass, wenn, ob, Relativsatz)
- 부사절, 등위/종속 접속사
- 평균 문장 길이 및 절의 개수
- 다양한 문장 구조

### 3. 어휘 범위 (vocabulary_range: 0-5)
- 추상 명사 및 전문 용어 사용 ("Bereich", "Koordination", "Motivation")
- 동의어 활용 및 어휘 다양성
- 단어 반복률 (같은 단어의 과도한 사용)

### 4. 유창성/응집성 (fluency_cohesion: 0-5)
- 담화 표지 사용 ("dann", "deshalb", "außerdem", "trotzdem")
- 시간·원인·결과 연결의 자연스러움
- 문장 간 논리적 흐름
- 불필요한 단절이나 문장 파편 여부

### 5. 과제 적합성 (task_relevance: 0-5)
- 질문 의도 충족 (요구된 정보 포함 여부)
- 주제 이탈 여부
- 답변의 완성도

## 응답 형식 (JSON)

다음 형식으로 응답해 주세요:

{{
  "grammar_accuracy": <0-5 점수>,
  "grammar_comment": "<문법 관련 상세 설명 및 예시>",
  "syntax_complexity": <0-5 점수>,
  "syntax_comment": "<구문 복잡도 관련 설명>",
  "vocabulary_range": <0-5 점수>,
  "vocabulary_comment": "<어휘 범위 관련 설명>",
  "fluency_cohesion": <0-5 점수>,
  "fluency_comment": "<유창성/응집성 관련 설명>",
  "task_relevance": <0-5 점수>,
  "task_comment": "<과제 적합성 관련 설명>",
  "overall_comment": "<전체적인 종합 평가 및 레벨 판정 근거>",
  "strengths": ["강점1", "강점2", "강점3"],
  "improvements": ["개선점1", "개선점2", "개선점3"]
}}

**중요:** 반드시 한국어로 피드백을 작성하되, 독일어 예시는 독일어로 표기해 주세요.
**중요:** 응답은 반드시 유효한 JSON 형식이어야 합니다.
"""
        return prompt

    def _get_fallback_feedback(self) -> DetailedFeedback:
        """API 실패 시 기본 피드백"""
        return DetailedFeedback(
            grammar_accuracy=3,
            grammar_comment="AI 피드백을 생성할 수 없습니다.",
            syntax_complexity=3,
            syntax_comment="AI 피드백을 생성할 수 없습니다.",
            vocabulary_range=3,
            vocabulary_comment="AI 피드백을 생성할 수 없습니다.",
            fluency_cohesion=3,
            fluency_comment="AI 피드백을 생성할 수 없습니다.",
            task_relevance=3,
            task_comment="AI 피드백을 생성할 수 없습니다.",
            overall_comment="OpenAI API 키가 설정되지 않아 AI 피드백을 생성할 수 없습니다.",
            strengths=[],
            improvements=[],
        )


# =============================================================================
# 7. 최종 레벨 판정
# =============================================================================


class FinalLevelAssessor:
    """5개 답변을 종합하여 최종 레벨 판정"""

    @staticmethod
    def assess_final_level(
        responses: List[UserResponse],
    ) -> Tuple[CEFRLevel, SubLevel, Dict]:
        """
        최종 레벨 판정

        Args:
            responses: 5개의 사용자 답변

        Returns:
            (최종 CEFRLevel, SubLevel, 상세 분석 결과)
        """
        # 각 레벨별 빈도 계산
        level_counts = {level: 0 for level in CEFRLevel}
        for resp in responses:
            level_counts[resp.estimated_level] += 1

        # 평균 레벨 계산
        avg_level_value = np.mean([resp.estimated_level.value for resp in responses])

        # 가장 빈번한 레벨
        most_frequent_level = max(level_counts, key=level_counts.get)

        # 평균 점수를 기반으로 최종 레벨 결정
        if avg_level_value < 1.5:
            final_level = CEFRLevel.A2
        elif avg_level_value < 2.5:
            final_level = CEFRLevel.B1
        elif avg_level_value < 3.5:
            final_level = CEFRLevel.B2
        else:
            final_level = CEFRLevel.C1

        # 서브레벨 결정
        decimal_part = avg_level_value - int(avg_level_value)
        if decimal_part < 0.33:
            sub_level = SubLevel.EARLY
        elif decimal_part < 0.67:
            sub_level = SubLevel.MID
        else:
            sub_level = SubLevel.LATE

        # 상세 분석
        analysis = {
            "average_level_value": avg_level_value,
            "level_distribution": {
                level.name: count for level, count in level_counts.items()
            },
            "most_frequent_level": most_frequent_level.name,
            "average_confidence": np.mean(
                [resp.similarity_score for resp in responses]
            ),
            "response_scores": [
                {
                    "question": resp.question_id,
                    "level": resp.estimated_level.name,
                    "confidence": resp.similarity_score,
                }
                for resp in responses
            ],
        }

        return final_level, sub_level, analysis


# =============================================================================
# 7. 레벨 테스트 세션 관리
# =============================================================================


class LevelTestSession:
    """레벨 테스트 전체 세션 관리"""

    def __init__(self):
        self.corpus_loader = CEFRCorpusLoader()
        self.level_estimator = None
        self.question_selector = AdaptiveQuestionSelector(QUESTION_BANK)
        self.ai_feedback_generator = AIFeedbackGenerator()
        self.responses: List[UserResponse] = []
        self.is_initialized = False
        self._cached_question: Optional[Question] = None  # 캐싱된 현재 질문
        self._asked_questions: List[Question] = []  # 출제된 질문들 기록

    def initialize(self):
        """세션 초기화 (코퍼스 로드 및 임베딩 생성)"""
        if not self.is_initialized:
            print("\n" + "=" * 60)
            print("🎯 독일어 레벨 테스트 초기화 중...")
            print("=" * 60)

            self.corpus_loader.load_corpus()
            self.corpus_loader.load_embedder()
            self.corpus_loader.create_corpus_embeddings()

            self.level_estimator = LevelEstimator(self.corpus_loader)
            self.is_initialized = True

            print("\n✅ 레벨 테스트 준비 완료!")
            print("=" * 60 + "\n")

    def get_current_question(self) -> Question:
        """현재 질문 가져오기 (캐싱 사용)"""
        num_responses = len(self.responses)

        print(f"\n🔍 DEBUG: get_current_question() 호출")
        print(f"   responses 개수: {num_responses}")
        print(f"   cached_question: {self._cached_question.id if self._cached_question else None}")

        # 캐시가 있는지 확인
        if self._cached_question is not None:
            # 캐시된 질문이 이미 used_questions에 있는지 확인
            if self._cached_question.id in self.question_selector.used_questions:
                # 이미 사용된 질문이라면 새 질문 필요
                already_answered = any(
                    resp.question_id == self._cached_question.id
                    for resp in self.responses
                )
                if already_answered:
                    print(f"   ⚠️  캐시된 질문 {self._cached_question.id}은 이미 답변됨 → 새 질문 필요")
                    self._cached_question = None
                else:
                    print(f"   → 캐시된 질문 반환 (아직 답변 안함): {self._cached_question.id}")
                    return self._cached_question
            else:
                print(f"   → 캐시된 질문 반환: {self._cached_question.id}")
                return self._cached_question

        # 새로운 질문 선택
        print(f"   → 새로운 질문 선택 필요")

        if num_responses == 0:
            # 첫 질문
            print(f"   → 첫 질문 선택: {INITIAL_QUESTION.id}")
            self._cached_question = INITIAL_QUESTION
            # 첫 질문도 used_questions에 추가
            self.question_selector.used_questions.add(INITIAL_QUESTION.id)
        else:
            # 이전 답변 기반으로 다음 질문 선택
            last_response = self.responses[-1]
            next_question = self.question_selector.select_next_question(
                num_responses,  # 현재까지 답변한 개수
                last_response.estimated_level,
                self.responses
            )
            print(f"   → 새 질문 선택: {next_question.id}")
            self._cached_question = next_question

        return self._cached_question

    def submit_response(self, user_text: str):
        """사용자 답변 제출 및 평가"""
        print(f"\n📝 DEBUG: submit_response() 호출")
        print(f"   제출 전 responses 개수: {len(self.responses)}")

        current_question = self.get_current_question()
        print(f"   현재 질문: {current_question.id}")

        # 출제된 질문 기록
        if current_question not in self._asked_questions:
            self._asked_questions.append(current_question)

        # 레벨 추정
        estimated_level, sub_level, confidence = self.level_estimator.estimate_level(
            user_text
        )

        # 답변 저장
        response = UserResponse(
            question_id=current_question.id,
            text=user_text,
            estimated_level=estimated_level,
            similarity_score=confidence,
        )
        self.responses.append(response)
        print(f"   답변 저장 완료: {current_question.id}")
        print(f"   제출 후 responses 개수: {len(self.responses)}")
        print(f"   사용된 질문들: {self.question_selector.used_questions}")

        print(f"\n📊 추정 레벨: {estimated_level.name}-{sub_level.value}")
        print(f"💯 신뢰도: {confidence:.2%}\n")

    def is_complete(self) -> bool:
        """테스트 완료 여부"""
        return len(self.responses) >= 5

    def get_final_result(self) -> Dict:
        """최종 결과 반환 (코사인 유사도 + AI 피드백)"""
        if not self.is_complete():
            raise ValueError("테스트가 아직 완료되지 않았습니다.")

        # 1. 코사인 유사도 기반 레벨 판정
        final_level, sub_level, analysis = FinalLevelAssessor.assess_final_level(
            self.responses
        )

        # 2. AI 피드백 생성 (5개 질문-답변 쌍 종합 분석)
        ai_feedback = self.ai_feedback_generator.generate_feedback(
            self._asked_questions, self.responses
        )

        return {
            "final_level": final_level.name,
            "sub_level": sub_level.value,
            "display_level": f"{final_level.name}-{sub_level.value}",
            "analysis": analysis,
            "ai_feedback": ai_feedback,
        }
