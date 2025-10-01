from utils.config import load_config
from utils.io import read_json, write_csv
from utils.log import get_logger
import pandas as pd
import re
from pathlib import Path
import hashlib
import json

logger = get_logger(__name__)

def clean_text(text):
    """텍스트 전처리: URL/특수문자/엔터 제거"""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"http\S+|www\S+", "", text)  # URL 제거
    text = re.sub(r"[^\w\s]", " ", text)        # 특수문자 제거
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"\s+", " ", text)            # 공백 정리
    return text.strip()

def make_id(row):
    """title, url, blogger 조합으로 고유 해시 ID 생성"""
    raw = f"{row['title']}|{row['url']}|{row['blogger']}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()

def load_and_clean(input_path, output_dir, min_doc_length):
    """JSON 로드 → 텍스트 클리닝 → cleaned.csv + id_map.csv 저장"""
    raw_data = read_json(input_path)
    df = pd.DataFrame(raw_data)

    # 고유 ID 생성
    df["id"] = df.apply(make_id, axis=1)

    # title + content 합성 후 클리닝
    df["full_text"] = df["title"].fillna("").astype(str) + " " + df["content"].fillna("").astype(str)
    df["cleaned_text"] = df["full_text"].apply(clean_text)

    # 길이 필터
    df = df[df["cleaned_text"].str.len() >= min_doc_length]

    # 저장 디렉토리 생성
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 분석 최소 데이터셋 (cleaned.csv)
    cleaned = df[["id", "date", "cleaned_text"]]
    write_csv(cleaned, output_dir / "cleaned.csv")

    # 메타데이터 매핑 (id_map.csv)
    id_map = df[["id", "title", "url", "blogger"]]
    write_csv(id_map, output_dir / "id_map.csv")

    logger.info(f"Saved cleaned data to {output_dir}, records={len(df)}")
    return output_dir

if __name__ == "__main__":
    config = load_config()
    run_id = config["run"]["run_id"]

    input_path = config["input"]["json_file"]
    output_dir = f"data/interim/{run_id}"
    min_doc_length = config["cleaning"]["min_doc_length"]

    result_dir = load_and_clean(input_path, output_dir, min_doc_length)

    # latest_run.json 기록
    latest_run_file = Path("data/interim/latest_run.json")
    with open(latest_run_file, "w", encoding="utf-8") as f:
        json.dump({"run_id": run_id}, f, ensure_ascii=False, indent=2)

    print(f"✅ Completed run_id={run_id}, outputs in {result_dir}")
