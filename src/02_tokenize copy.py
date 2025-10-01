import json
import re
import pandas as pd
from pathlib import Path
from utils.io import write_csv
from utils.log import get_logger

logger = get_logger(__name__)

def simple_tokenize(text, min_len=2, to_lower=True):
    """
    간단한 토큰화: 공백 기준 분리 + 최소 길이 필터링
    """
    if not isinstance(text, str):
        return []
    if to_lower:
        text = text.lower()
    tokens = re.split(r"\s+", text.strip())
    return [t for t in tokens if len(t) >= min_len]

def tokenize_and_save(input_path, output_path, min_len=2):
    """
    cleaned.csv → 토큰화 → tokens.csv 저장
    """
    df = pd.read_csv(input_path, encoding="utf-8-sig")

    # 토큰화
    df["tokens"] = df["cleaned_text"].apply(lambda x: simple_tokenize(x, min_len=min_len))

    # 최소 칼럼만 저장 (id, tokens)
    tokens_df = df[["id", "tokens"]]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_csv(tokens_df, output_path)

    logger.info(f"Tokenized data saved to {output_path}, records={len(tokens_df)}")
    return output_path

if __name__ == "__main__":
    # latest_run.json 읽기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run 01_load_clean.py first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    input_path = f"data/interim/{run_id}/cleaned.csv"
    output_path = f"data/interim/{run_id}/tokens.csv"

    result = tokenize_and_save(input_path, output_path, min_len=2)
    print(f"✅ Tokenization completed. run_id={run_id}, saved to {result}")
