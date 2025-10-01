import pandas as pd
from pathlib import Path
import json
from utils.io import write_csv
from utils.log import get_logger

logger = get_logger(__name__)

def build_word_dictionary(nodes_path, ngram_path, output_path):
    """
    노드 지표(cooc_nodes_fast.csv) + ngram 결과를 합쳐 워드 사전 생성
    """
    # 1) 노드 지표 불러오기
    nodes_df = pd.read_csv(nodes_path, encoding="utf-8-sig")
    logger.info(f"Loaded node stats: {nodes_df.shape}")

    # 2) ngram 불러오기
    ngram_df = pd.read_csv(ngram_path, encoding="utf-8-sig")
    logger.info(f"Loaded ngrams: {ngram_df.shape}")

    # 3) ngram 분리 → 단어별 빈도 count
    ngram_df["tokens"] = ngram_df["ngram"].str.split("_")
    all_tokens = ngram_df["tokens"].explode()
    token_freq = all_tokens.value_counts().reset_index()
    token_freq.columns = ["word", "ngram_freq"]

    # 4) 노드 지표 + ngram 빈도 병합
    merged = pd.merge(nodes_df, token_freq, on="word", how="outer").fillna(0)

    # 5) 점수 계산 (단순 가중치 예시)
    merged["score"] = (
        merged["degree"] * 1.0 +
        merged["weighted_degree"] * 0.5 +
        merged["betweenness"] * 100 +
        merged["ngram_freq"] * 2.0
    )

    # 6) 저장
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_csv(merged, output_path)
    logger.info(f"Word dictionary saved: {output_path}, records={len(merged)}")

    return output_path


if __name__ == "__main__":
    # latest_run.json 불러오기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run previous steps first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    # 경로 설정
    nodes_path = f"data/processed/{run_id}/cooc_nodes_full.csv"
    ngram_path = f"data/processed/{run_id}/ngrams.csv"
    output_path = f"data/processed/{run_id}/word_dictionary.csv"

    # 실행
    result = build_word_dictionary(nodes_path, ngram_path, output_path)
    print(f"✅ Word dictionary built: {result}")
