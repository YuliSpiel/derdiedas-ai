# 문법 온톨로지 데이터

## 📁 디렉토리 구조

```
grammar_ontology/
├── README.md                    # 이 파일
├── grammar_ontology.json        # 전체 온톨로지 (GPT 생성 예정)
└── topics/                      # 주제별 개별 파일 (선택사항)
```

## 🎯 GPT에게 요청할 내용

상위 디렉토리의 `docs/GRAMMAR_ONTOLOGY_SPEC.md`를 참고하여
GPT에게 다음을 생성하도록 요청하세요:

1. **전체 온톨로지 파일** (`grammar_ontology.json`)
   - 69개 문법 주제의 체계적인 데이터
   - 각 주제별 20-30개 예제
   - 각 주제별 10-15개 연습 문제

2. **품질 기준**
   - CEFR 레벨 정확도
   - 실용적인 예제
   - 다양한 문제 유형
   - 명확한 설명

## 📊 기존 파싱 데이터 활용

`../grammar_content/grammar_topics.json` 파일에
Deutsch im Blick에서 파싱한 기본 데이터가 있습니다.

이를 기반으로 GPT가 다음을 보강하도록 하세요:
- 한국어 설명 추가
- 예제 문장 확장
- 연습 문제 생성
- 흔한 실수 패턴 추가

## ✅ 생성 완료 후

생성된 `grammar_ontology.json` 파일을 이 디렉토리에 저장하면
시스템이 자동으로 로드합니다.

```python
# 테스트
python -c "from src.models.grammar_ontology import GrammarOntologyLoader; \
loader = GrammarOntologyLoader(); \
topics = loader.load_all_topics(); \
print(f'로드됨: {len(topics)}개 주제')"
```
