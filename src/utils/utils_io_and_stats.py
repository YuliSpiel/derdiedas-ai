# utils_io_and_stats.py

import os
import json
from typing import List, Dict, Iterable, Optional
from dataclasses import dataclass
from statistics import mean
from collections import Counter, defaultdict

import pandas as pd


# ---- 저장 유틸 ----
def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def save_parquet(df: pd.DataFrame, out_path: str):
    ensure_dir(os.path.dirname(out_path))
    df.to_parquet(out_path, index=False)
    print(f"✅ Saved Parquet: {out_path} | rows={len(df):,}")


def save_jsonl(records: List[Dict], out_path: str):
    ensure_dir(os.path.dirname(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"✅ Saved JSONL: {out_path} | rows={len(records):,}")


# ---- 통계/검증 출력 ----
def preview_df(df: pd.DataFrame, n: int = 5, cols: Optional[List[str]] = None):
    print("🧾 DataFrame preview")
    if cols:
        print(df[cols].head(n))
    else:
        print(df.head(n))


def describe_units(df: pd.DataFrame):
    print("\n📊 Unit counts")
    print(df["unit"].value_counts())

    print("\n📈 Avg length (tokens) per unit")
    lens = (
        df.assign(_len=df["text"].str.split().apply(len)).groupby("unit")["_len"].mean()
    )
    print(lens.round(2))


def check_empty_or_dup(df: pd.DataFrame):
    print("\n🧪 Empty text rows:", int((df["text"].str.strip() == "").sum()))
    if {"doc_id", "unit", "idx"}.issubset(df.columns):
        dups = df.duplicated(subset=["doc_id", "unit", "idx"]).sum()
        print("🧪 Duplicate (doc_id,unit,idx):", int(dups))
    else:
        print("🧪 Duplicate check skipped (missing keys)")


def label_distribution(df: pd.DataFrame, label_col: str = "label_doc"):
    if label_col not in df.columns:
        print("\n⚠️ Label column not found for distribution.")
        return
    print("\n🏷️ Label distribution")
    print(df[label_col].value_counts())
