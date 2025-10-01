import json
import pandas as pd
from pathlib import Path
from kiwipiepy import Kiwi
from utils.io import write_csv
from utils.log import get_logger
from utils.config import load_config

logger = get_logger(__name__)

def morph_tokenize(text, kiwi, pos_keep, min_len=1, stopwords=None):
    """
    형태소 분석 기반 토큰화
    - 지정된 품사(pos_keep)만 추출
    - stopwords 제거
    - min_len 이상인 토큰만 남김
    """
    tokens = []
    for word, pos, _, _ in kiwi.tokenize(text):
        if pos in pos_keep and len(word) >= min_len:
            if stopwords and word in stopwords:
                continue
            tokens.append(word)
    return tokens

def load_stopwords(path="dicts/stopwords.txt"):
    """불용어 사전 로드"""
    try:
        with open(path, encoding="utf-8") as f:
            return set(w.strip() for w in f if w.strip())
    except FileNotFoundError:
        logger.warning(f"Stopwords file not found at {path}. Using empty list.")
        return set()

def tokenize_and_save(input_path, output_path, pos_keep, min_len, stopwords):
    """
    cleaned.csv → 형태소 분석 기반 토큰화 → tokens.csv 저장
    """
    kiwi = Kiwi()
    df = pd.read_csv(input_path, encoding="utf-8-sig")

    # 형태소 분석기 기반 토큰화
    df["tokens"] = df["cleaned_text"].apply(
        lambda x: morph_tokenize(x, kiwi, pos_keep, min_len=min_len, stopwords=stopwords)
    )

    # id, tokens만 저장
    tokens_df = df[["id", "tokens"]]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_csv(tokens_df, output_path)

    logger.info(f"Tokenized data saved to {output_path}, records={len(tokens_df)}")
    return output_path


if __name__ == "__main__":
    # config.yaml 불러오기
    config = load_config()
    pos_keep = config["tokenization"]["pos_keep"]   # e.g., ["NNG", "NNP", "SL"]
    min_len = config["tokenization"]["min_token_len"]
    stopwords = load_stopwords(config["dictionaries"]["stopwords"])

    # latest_run.json 읽기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run 01_load_clean.py first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    input_path = f"data/interim/{run_id}/cleaned.csv"
    output_path = f"data/interim/{run_id}/tokens.csv"

    result = tokenize_and_save(input_path, output_path, pos_keep, min_len, stopwords)
    print(f"✅ Tokenization (morphological) completed. run_id={run_id}, saved to {result}")
