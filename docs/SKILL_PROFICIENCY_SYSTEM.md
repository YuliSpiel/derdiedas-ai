# 스킬 숙련도 추적 시스템

## 개요

사용자의 문법 온톨로지 기반 스킬별 숙련도를 추적하고 시각화하는 시스템입니다.

## 주요 기능

### 1. 레벨 테스트 시 초기 평가
- **시점**: 레벨 테스트 완료 후 자동 실행
- **평가 범위**: 사용자의 판정 CEFR 레벨 이하 스킬만 평가
  - 예: B1 판정 시 → A1, A2, B1 스킬만 평가
- **평가 방법**: GPT-4o mini를 사용한 LLM 기반 분석
  - 5개 작문 샘플 종합 분석
  - 각 스킬별 0-100 점수 부여
  - 스킬 사용 여부 확인 및 정확도 평가

### 2. 프로필 저장
- **저장 위치**: `data/user_profile.json`
- **데이터 구조**:
  ```json
  {
    "skill_proficiency": {
      "G.ART.DEF.NOM": 75,
      "G.V.TENSE.PRES": 80,
      "G.NOUN.GENDER.BASICS": 65,
      ...
    }
  }
  ```

### 3. 학습 리포트 페이지
- **경로**: `pages/learning_report.py`
- **접근 방법**: 대시보드 하단 "📈 학습 리포트 보기" 버튼
- **기능**:
  - 카테고리별 스킬 그룹핑 (관사, 동사, 형용사 등)
  - CEFR 레벨 및 카테고리 필터링
  - 가로 막대 프로그레스 바로 숙련도 시각화
  - 평균 숙련도 및 카테고리별 통계

## 구현된 파일

### 1. 데이터 모델
**파일**: `src/models/user_profile.py`

```python
@dataclass
class UserProfile:
    skill_proficiency: Dict[str, float] = field(default_factory=dict)
```

- `to_dict()`: 숙련도 데이터 직렬화
- `from_dict()`: 숙련도 데이터 역직렬화
- `update_level_from_test()`: 레벨 + 숙련도 동시 업데이트

### 2. 숙련도 평가기
**파일**: `src/level_test/skill_proficiency_assessor.py`

```python
class SkillProficiencyAssessor:
    def assess_proficiency(
        self,
        user_level: str,
        writing_samples: List[str],
        model: str = "gpt-4o-mini"
    ) -> Dict[str, float]:
```

**주요 메서드**:
- `_load_skills()`: 온톨로지 데이터 로드
- `_get_skills_up_to_level()`: 사용자 레벨 이하 스킬 필터링
- `_create_assessment_prompt()`: LLM 평가 프롬프트 생성
- `assess_proficiency()`: 실제 평가 실행

### 3. 레벨 테스트 통합
**파일**: `src/level_test/CEFR_Eval.py`

```python
class LevelTestSession:
    def get_final_result(self) -> Dict:
        # ...
        # 3. 스킬별 숙련도 평가
        skill_proficiency = assessor.assess_proficiency(
            user_level=final_level.name,
            writing_samples=writing_samples
        )

        return {
            "skill_proficiency": skill_proficiency,
            # ...
        }
```

### 4. UI 페이지
**파일**: `pages/level_test.py`

- 레벨 테스트 결과 페이지에서 자동 저장
- 저장 성공 시 스킬 개수 표시

**파일**: `pages/learning_report.py`

- 스킬 숙련도 시각화 페이지
- 카테고리별 그룹핑
- 필터링 기능 (CEFR 레벨, 카테고리)
- 프로그레스 바로 직관적 표시

**파일**: `pages/dashboard.py`

- 학습 리포트 페이지 링크 추가

## 평가 프롬프트 구조

```
## 학습자 작문 샘플:
1. [문장 1]
2. [문장 2]
...

## 평가 대상 문법 스킬:
[
  {
    "id": "G.ART.DEF.NOM",
    "title_ko": "정관사 - 주격",
    "cefr_level": "A1",
    ...
  }
]

## 평가 지침:
1. 각 스킬의 정확한 사용 여부 분석
2. 0-100 점수 부여
   - 0-30: 거의 사용 안함/심각한 오류
   - 31-50: 기본 이해, 자주 실수
   - 51-70: 대체로 정확, 가끔 실수
   - 71-85: 안정적 사용
   - 86-100: 완벽 숙달
3. 사용하지 않은 스킬은 제외

## 출력:
{
  "proficiency": {
    "G.ART.DEF.NOM": 75,
    ...
  }
}
```

## 데이터 흐름

```
레벨 테스트 완료
    ↓
5개 작문 샘플 수집
    ↓
CEFR 레벨 판정 (예: B1)
    ↓
B1 이하 스킬만 필터링 (A1, A2, B1)
    ↓
LLM 평가 실행 (GPT-4o-mini)
    ↓
스킬별 점수 (0-100) 반환
    ↓
user_profile.json에 저장
    ↓
학습 리포트 페이지에서 시각화
```

## 향후 확장 가능성

### 1. 학습 사이클 후 업데이트
- 노트북 학습 완료 시 관련 스킬 숙련도 업데이트
- 연습 문제 정답률 기반 점수 조정
- 시간에 따른 숙련도 변화 추적

### 2. 추천 시스템
- 낮은 숙련도 스킬 우선 학습 추천
- 선행 스킬 충족 여부 확인
- 사용자 레벨에 맞는 난이도 조절

### 3. 시각화 개선
- 시간별 숙련도 변화 그래프
- 레이더 차트로 카테고리별 비교
- 강점/약점 분석 리포트

### 4. 게임화 요소
- 스킬 마스터리 뱃지
- 숙련도 향상 알림
- 학습 목표 설정 및 달성 추적

## 필수 환경 변수

```bash
OPENAI_API_KEY=your_api_key_here
```

## 테스트 방법

```bash
# 1. 레벨 테스트 완료
streamlit run app.py
# → 레벨 테스트 페이지 이동
# → 5개 질문 답변
# → 결과 확인 (스킬 숙련도 저장 메시지)

# 2. 학습 리포트 확인
# → 대시보드에서 "학습 리포트 보기" 클릭
# → 카테고리별 숙련도 확인
# → 필터링 테스트

# 3. 데이터 확인
cat data/user_profile.json
# → skill_proficiency 필드 존재 확인
```

## 의존성

- `openai>=1.0.0`: GPT API 사용
- `streamlit>=1.28.0`: UI 페이지
- `python-dotenv>=1.0.0`: 환경 변수 관리

## 주의사항

1. **온톨로지 데이터 필수**: `data/grammar_ontology/grammar_ontology.json` 파일 필요
2. **API 비용**: 레벨 테스트당 1회 GPT-4o-mini API 호출 발생
3. **평가 시간**: 스킬 개수에 따라 5-10초 소요
4. **에러 핸들링**: 평가 실패 시 빈 딕셔너리 반환 (시스템은 정상 작동)

## 문의 및 개선

스킬 숙련도 시스템 관련 문의사항이나 개선 제안은 이슈로 등록해 주세요.
