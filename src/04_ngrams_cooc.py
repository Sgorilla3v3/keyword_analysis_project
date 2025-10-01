import json
import pandas as pd
from pathlib import Path
from collections import Counter
from itertools import combinations
from utils.io import write_csv
from utils.log import get_logger
from utils.config import load_config

logger = get_logger(__name__)

def generate_ngrams(tokens, n):
    """토큰 리스트에서 n-gram 추출"""
    return ["_".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]

def build_cooccurrence(tokens_list, window_size=10):
    """
    토큰 리스트들에서 동시출현(co-occurrence) edge 집계
    - window_size 내에서 함께 등장하는 단어 쌍 카운트
    """
    cooc_counter = Counter()
    for tokens in tokens_list:
        for i in range(len(tokens)):
            window_tokens = tokens[i+1 : i+1+window_size]
            for t in window_tokens:
                if tokens[i] != t:
                    pair = tuple(sorted([tokens[i], t]))
                    cooc_counter[pair] += 1
    return cooc_counter

def ngrams_and_cooc(input_path, output_dir, ngram_min, ngram_max, window_size, min_cooc_count):
    """
    tokens.csv → n-gram + co-occurrence 추출 → 저장
    """
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    # tokens가 문자열이면 eval로 리스트 변환
    df["tokens"] = df["tokens"].apply(lambda x: eval(x) if isinstance(x, str) else [])

    # === 1. N-grams 추출 ===
    ngram_records = []
    for _, row in df.iterrows():
        tokens = row["tokens"]
        for n in range(ngram_min, ngram_max + 1):
            ngrams = generate_ngrams(tokens, n)
            for ng in ngrams:
                ngram_records.append({"id": row["id"], "ngram": ng})

    ngram_df = pd.DataFrame(ngram_records)

    # === 2. Co-occurrence 추출 ===
    tokens_list = df["tokens"].tolist()
    cooc_counter = build_cooccurrence(tokens_list, window_size=window_size)

    cooc_records = [
        {"source": a, "target": b, "weight": w}
        for (a, b), w in cooc_counter.items()
        if w >= min_cooc_count
    ]
    cooc_df = pd.DataFrame(cooc_records)

    # === 저장 ===
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(ngram_df, output_dir / "ngrams.csv")
    write_csv(cooc_df, output_dir / "cooc_edges.csv")

    logger.info(f"N-grams and co-occurrence saved to {output_dir}")
    return output_dir


if __name__ == "__main__":
    # config.yaml 불러오기
    config = load_config()
    ngram_min = config["features"]["ngram_min"]
    ngram_max = config["features"]["ngram_max"]
    window_size = config["features"]["window_size"]
    min_cooc_count = config["features"]["min_cooc_count"]

    # latest_run.json 읽기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run 01_load_clean.py → 02_tokenize.py first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    input_path = f"data/interim/{run_id}/tokens.csv"
    output_dir = f"data/processed/{run_id}"

    result_dir = ngrams_and_cooc(input_path, output_dir, ngram_min, ngram_max, window_size, min_cooc_count)
    print(f"✅ N-grams & Co-occurrence completed. run_id={run_id}, outputs in {result_dir}")
