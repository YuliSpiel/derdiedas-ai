"""
문법 콘텐츠 HTML 파싱 및 구조화

Deutsch im Blick 문법 페이지를 파싱하여 구조화된 JSON 데이터로 변환
"""

import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class GrammarTopic:
    """문법 주제 데이터 구조"""
    id: str
    title: str
    cefr_level: str  # A1, A2, B1, B2, C1
    category: str  # verbs, nouns, adjectives, prepositions, etc.
    subcategory: str
    tags: List[str]
    difficulty_score: float  # 1.0-5.0
    estimated_time: int  # 분
    prerequisites: List[str]
    content: Dict[str, any]
    source_file: str


class GrammarContentParser:
    """문법 콘텐츠 파서"""

    # 카테고리 키워드 매핑
    CATEGORY_KEYWORDS = {
        'verbs': ['verb', 'verben', 'perfekt', 'präteritum', 'konjugation'],
        'nouns': ['nomen', 'noun', 'substantiv', 'plural'],
        'adjectives': ['adjektiv', 'adjective'],
        'articles': ['artikel', 'article', 'der', 'die', 'das'],
        'prepositions': ['präposition', 'preposition'],
        'pronouns': ['pronomen', 'pronoun'],
        'cases': ['kasus', 'case', 'nominativ', 'akkusativ', 'dativ', 'genitiv'],
        'conjunctions': ['konjunktion', 'conjunction'],
        'word_order': ['wortstellung', 'word order', 'syntax'],
        'vocabulary': ['wortschatz', 'vocabulary']
    }

    # CEFR 레벨 추정 키워드
    CEFR_KEYWORDS = {
        'A1': ['basic', 'introduction', 'simple', 'sein', 'haben', 'present tense'],
        'A2': ['regular', 'plural', 'perfect tense', 'modal verbs', 'personal pronoun'],
        'B1': ['past tense', 'conjunctions', 'relative clause', 'passive', 'subjunctive'],
        'B2': ['complex', 'advanced', 'indirect speech', 'subjunctive II'],
        'C1': ['sophisticated', 'nuanced', 'literary', 'formal']
    }

    def __init__(self, html_dir: str):
        self.html_dir = Path(html_dir)
        self.topics: List[GrammarTopic] = []

    def parse_all(self) -> List[GrammarTopic]:
        """모든 HTML 파일 파싱"""
        html_files = sorted(self.html_dir.glob("*.html"))
        print(f"📚 {len(html_files)}개 파일 파싱 시작...")

        for html_file in html_files:
            try:
                topic = self.parse_file(html_file)
                if topic:
                    self.topics.append(topic)
                    print(f"  ✓ {topic.id} ({topic.category})")
            except Exception as e:
                print(f"  ✗ {html_file.name}: {e}")

        print(f"\n✅ 총 {len(self.topics)}개 주제 파싱 완료")
        return self.topics

    def parse_file(self, file_path: Path) -> Optional[GrammarTopic]:
        """단일 HTML 파일 파싱"""
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # 제목 추출
        title_elem = soup.find('title')
        if not title_elem:
            return None

        title = title_elem.text.strip()
        # "– Grammar to Accompany Deutsch im Blick" 제거
        title = re.sub(r'\s*[–-]\s*Grammar to Accompany.*', '', title)
        title = title.strip()

        if not title or 'table of contents' in title.lower():
            return None

        # ID는 파일명에서 추출
        topic_id = file_path.stem

        # 본문 콘텐츠 추출
        content_div = soup.find('div', class_='entry-content') or soup.find('main')
        if not content_div:
            return None

        # 텍스트 내용 추출
        full_text = content_div.get_text().lower()

        # 카테고리 분류
        category = self._classify_category(title, full_text)
        subcategory = self._extract_subcategory(title)

        # CEFR 레벨 추정
        cefr_level = self._estimate_cefr_level(title, full_text, category)

        # 태그 추출
        tags = self._extract_tags(title, full_text)

        # 난이도 점수 계산
        difficulty = self._calculate_difficulty(cefr_level, category)

        # 예상 학습 시간
        estimated_time = self._estimate_time(full_text)

        # 콘텐츠 구조화
        content = self._extract_content(content_div)

        return GrammarTopic(
            id=topic_id,
            title=title,
            cefr_level=cefr_level,
            category=category,
            subcategory=subcategory,
            tags=tags,
            difficulty_score=difficulty,
            estimated_time=estimated_time,
            prerequisites=[],  # 나중에 수동으로 추가
            content=content,
            source_file=file_path.name
        )

    def _classify_category(self, title: str, text: str) -> str:
        """카테고리 분류"""
        title_lower = title.lower()

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in title_lower or keyword in text[:500]:
                    return category

        return 'other'

    def _extract_subcategory(self, title: str) -> str:
        """하위 카테고리 추출"""
        # 괄호 안의 내용 추출
        match = re.search(r'\((.*?)\)', title)
        if match:
            return match.group(1).strip()

        # 콜론 뒤의 내용
        if ':' in title:
            return title.split(':')[-1].strip()

        return ''

    def _estimate_cefr_level(self, title: str, text: str, category: str) -> str:
        """CEFR 레벨 추정"""
        title_lower = title.lower()

        # 키워드 기반 점수 계산
        scores = {level: 0 for level in self.CEFR_KEYWORDS.keys()}

        for level, keywords in self.CEFR_KEYWORDS.items():
            for keyword in keywords:
                if keyword in title_lower:
                    scores[level] += 3
                if keyword in text[:1000]:
                    scores[level] += 1

        # 카테고리별 기본 레벨
        category_defaults = {
            'articles': 'A1',
            'nouns': 'A1',
            'verbs': 'A2',
            'adjectives': 'A2',
            'prepositions': 'A2',
            'cases': 'B1',
            'conjunctions': 'B1',
            'pronouns': 'A2'
        }

        # 점수가 가장 높은 레벨 선택
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        # 기본값
        return category_defaults.get(category, 'A2')

    def _extract_tags(self, title: str, text: str) -> List[str]:
        """태그 추출"""
        tags = []

        # 제목에서 주요 단어 추출
        title_words = re.findall(r'\b[A-Za-zäöüÄÖÜß]{4,}\b', title)
        tags.extend(title_words[:3])

        # 특수 키워드
        special_keywords = ['endings', 'tense', 'case', 'gender', 'plural',
                          'conjugation', 'declension', 'irregular']
        for keyword in special_keywords:
            if keyword in text[:500]:
                tags.append(keyword)

        return list(set(tags))[:5]

    def _calculate_difficulty(self, cefr_level: str, category: str) -> float:
        """난이도 점수 계산 (1.0-5.0)"""
        base_scores = {
            'A1': 1.0,
            'A2': 2.0,
            'B1': 3.0,
            'B2': 4.0,
            'C1': 5.0
        }

        category_modifiers = {
            'articles': -0.2,
            'nouns': -0.1,
            'verbs': 0.2,
            'cases': 0.3,
            'conjunctions': 0.2,
            'word_order': 0.3
        }

        score = base_scores.get(cefr_level, 2.5)
        score += category_modifiers.get(category, 0)

        return round(max(1.0, min(5.0, score)), 1)

    def _estimate_time(self, text: str) -> int:
        """예상 학습 시간 계산 (분)"""
        word_count = len(text.split())

        # 단어 수 기반 시간 추정
        if word_count < 300:
            return 10
        elif word_count < 600:
            return 15
        elif word_count < 1000:
            return 20
        else:
            return 30

    def _extract_content(self, content_div) -> Dict:
        """콘텐츠 구조화"""
        # 제목들 추출
        headings = []
        for h in content_div.find_all(['h2', 'h3', 'h4']):
            headings.append({
                'level': h.name,
                'text': h.get_text().strip()
            })

        # 예제 문장 추출 (독일어 문장 패턴)
        examples = []
        for p in content_div.find_all('p'):
            text = p.get_text().strip()
            # 독일어 문장 패턴 (대문자 시작, 마침표 끝)
            if re.match(r'^[A-ZÄÖÜ].*[.!?]$', text) and len(text) < 200:
                examples.append(text)

        # 테이블 추출 (격변화표 등)
        tables = []
        for table in content_div.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                cells = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                if cells:
                    table_data.append(cells)
            if table_data:
                tables.append(table_data)

        return {
            'headings': headings[:10],
            'examples': examples[:20],
            'tables': tables[:5],
            'full_html': str(content_div)[:5000]  # 처음 5000자만
        }

    def save_to_json(self, output_file: str):
        """JSON 파일로 저장"""
        data = [asdict(topic) for topic in self.topics]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 데이터 저장 완료: {output_file}")
        print(f"   총 {len(self.topics)}개 주제")

    def save_summary(self, output_file: str):
        """요약 정보 저장"""
        summary = {
            'total_topics': len(self.topics),
            'by_category': {},
            'by_cefr_level': {},
            'topics': []
        }

        # 카테고리별 집계
        for topic in self.topics:
            summary['by_category'][topic.category] = \
                summary['by_category'].get(topic.category, 0) + 1
            summary['by_cefr_level'][topic.cefr_level] = \
                summary['by_cefr_level'].get(topic.cefr_level, 0) + 1

            summary['topics'].append({
                'id': topic.id,
                'title': topic.title,
                'category': topic.category,
                'cefr_level': topic.cefr_level,
                'difficulty': topic.difficulty_score,
                'time': topic.estimated_time
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"📊 요약 저장 완료: {output_file}")


def main():
    """메인 실행 함수"""
    # 경로 설정
    project_root = Path(__file__).parent.parent.parent
    html_dir = project_root / "notebooks" / "pressbook_html"
    output_dir = project_root / "data" / "grammar_content"

    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)

    # 파싱 실행
    parser = GrammarContentParser(html_dir)
    topics = parser.parse_all()

    # 결과 저장
    parser.save_to_json(output_dir / "grammar_topics.json")
    parser.save_summary(output_dir / "grammar_summary.json")

    # 통계 출력
    print("\n📈 통계:")
    print(f"  카테고리별:")
    category_counts = {}
    cefr_counts = {}
    for topic in topics:
        category_counts[topic.category] = category_counts.get(topic.category, 0) + 1
        cefr_counts[topic.cefr_level] = cefr_counts.get(topic.cefr_level, 0) + 1

    for cat, count in sorted(category_counts.items()):
        print(f"    {cat}: {count}개")

    print(f"\n  CEFR 레벨별:")
    for level in ['A1', 'A2', 'B1', 'B2', 'C1']:
        if level in cefr_counts:
            print(f"    {level}: {cefr_counts[level]}개")


if __name__ == "__main__":
    main()
