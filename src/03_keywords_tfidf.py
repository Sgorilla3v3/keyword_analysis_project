import json
import pandas as pd
from pathlib import Path
from utils.io import write_csv
from utils.log import get_logger
from utils.config import load_config
from sklearn.feature_extraction.text import TfidfVectorizer

logger = get_logger(__name__)

def keywords_tfidf(input_path, output_path, topk=50, max_features=3000):
    """
    tokens.csv → TF-IDF 상위 키워드 추출 → keywords_top.csv 저장
    """
    df = pd.read_csv(input_path, encoding="utf-8-sig")

    # tokens 컬럼을 문자열로 변환 (TF-IDF 입력용)
    df["doc_str"] = (
        df["tokens"].astype(str)
        .str.replace("[", " ")
        .str.replace("]", " ")
        .str.replace(",", " ")
    )

    # TF-IDF 계산 (config 값 반영)
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(df["doc_str"])
    terms = vectorizer.get_feature_names_out()

    # 각 문서별 상위 topk 키워드 추출
    top_keywords = []
    for idx, row in enumerate(tfidf_matrix):
        row_data = row.toarray().flatten()
        top_indices = row_data.argsort()[-topk:][::-1]
        keywords = [terms[i] for i in top_indices if row_data[i] > 0]
        top_keywords.append(" ".join(keywords))

    df["keywords"] = top_keywords

    # id, keywords만 저장
    keywords_df = df[["id", "keywords"]]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_csv(keywords_df, output_path)

    logger.info(
        f"Keywords saved to {output_path}, records={len(keywords_df)}, "
        f"topk={topk}, max_features={max_features}"
    )
    return output_path


if __name__ == "__main__":
    # config.yaml 불러오기
    config = load_config()
    topk = config["features"]["topk"]
    max_features = config["topic_modeling"]["max_features"]

    # latest_run.json 읽기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run 01_load_clean.py and 02_tokenize.py first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    input_path = f"data/interim/{run_id}/tokens.csv"
    output_path = f"data/processed/{run_id}/keywords_top.csv"

    result = keywords_tfidf(input_path, output_path, topk=topk, max_features=max_features)
    print(f"✅ Keywords TF-IDF completed. run_id={run_id}, saved to {result}")
