# parse_pipeline.py

from typing import List, Dict, Iterable, Optional
import pandas as pd

# --- 네가 이미 가지고 있는 함수가 있다고 가정 ---
# split_sentences(text: str) -> List[str]
# make_windows(sents: List[str], win: int, stride: int) -> List[Tuple[List[int], str]]
# 위의 make_windows는 [(문장인덱스리스트, 윈도우텍스트)] 형태로 반환하도록 구현되어 있어도 되고,
# 단순히 텍스트만 반환해도 아래 코드는 대응해 줄 버전을 포함한다.

def doc_to_instances(
    doc_id: str,
    text: str,
    doc_label: str,
    split_sentences,
    make_windows,
    wins: List[int] = [2, 3],
    stride: int = 1,
    min_tokens: int = 5,
    max_tokens: int = 120
) -> List[Dict]:
    """
    한 문서를 문장/윈도우 단위 인스턴스로 변환.
    - min/max_tokens: 너무 짧거나 긴 조각 필터링(노이즈/비정상 데이터 방지)
    """
    def _tok_len(t: str) -> int:
        return len(t.split())

    instances: List[Dict] = []
    sents = split_sentences(text)

    # 문장 단위 추가
    for i, s in enumerate(sents):
        if min_tokens <= _tok_len(s) <= max_tokens:
            instances.append({
                "doc_id": doc_id,
                "unit": "sent",
                "idx": i,
                "text": s,
                "label_doc": doc_label
            })

    # 윈도우 단위 추가 (2,3 문장 등)
    for w in wins:
        wins_out = make_windows(sents, win=w, stride=stride)
        # make_windows가 인덱스 포함 버전/텍스트만 버전 둘 다 지원
        for j, item in enumerate(wins_out):
            if isinstance(item, tuple) and len(item) == 2:
                idxs, wtext = item
            else:
                idxs, wtext = None, item  # 텍스트만 반환하는 구현일 때 대응
            if min_tokens <= _tok_len(wtext) <= max_tokens:
                instances.append({
                    "doc_id": doc_id,
                    "unit": f"win{w}",
                    "idx": j,
                    "text": wtext,
                    "label_doc": doc_label,
                    "span": idxs  # 인덱스 리스트(있을 경우)
                })

    return instances


def process_dataset_iter(
    records: Iterable[Dict],
    split_sentences,
    make_windows,
    text_key: str,
    label_key: str,
    id_key: Optional[str] = None,
    start_id: int = 0,
    wins: List[int] = [2,3],
    stride: int = 1,
    min_tokens: int = 5,
    max_tokens: int = 120,
    max_docs: Optional[int] = None
) -> pd.DataFrame:
    """
    HF datasets의 split(iterable) 또는 임의의 dict 반복자(records)를 받아
    파싱된 인스턴스 DataFrame으로 반환.
    """
    all_instances: List[Dict] = []
    for k, rec in enumerate(records):
        if max_docs is not None and k >= max_docs:
            break
        doc_id = rec[id_key] if id_key and id_key in rec else f"doc_{start_id + k}"
        text = rec[text_key]
        label = rec[label_key]
        insts = doc_to_instances(
            doc_id=doc_id,
            text=text,
            doc_label=label,
            split_sentences=split_sentences,
            make_windows=make_windows,
            wins=wins,
            stride=stride,
            min_tokens=min_tokens,
            max_tokens=max_tokens
        )
        all_instances.extend(insts)

    df = pd.DataFrame(all_instances)
    # 기본 정렬(원하는 키로)
    if {"doc_id","unit","idx"}.issubset(df.columns):
        df = df.sort_values(by=["doc_id","unit","idx"]).reset_index(drop=True)
    return df
