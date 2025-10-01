import json
import pandas as pd
from pathlib import Path
from utils.io import write_csv
from utils.log import get_logger
from utils.config import load_config

logger = get_logger(__name__)

def rule_based_ner(input_path, dict_programs, output_path):
    """
    간단한 룰 기반 NER
    - 프로그램 리스트 사전을 활용하여 프로그램명 추출
    - 결과는 문서별 엔터티 리스트 형태로 저장
    """
    # 1) 데이터 로드
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    logger.info(f"Loaded cleaned/tokenized data: {df.shape}")

    # 2) 프로그램 리스트 로드
    program_list = pd.read_csv(dict_programs, encoding="utf-8-sig")["program_name"].tolist()
    logger.info(f"Loaded program dictionary: {len(program_list)} entries")

    # 3) 개체명 추출 (문서별 리스트)
    entities = []
    for i, row in df.iterrows():
        text = row.get("cleaned_text") or row.get("tokens")
        found = [p for p in program_list if p in str(text)]
        entities.append({
            "id": row.get("id", i),
            "entities": found if found else []
        })

    ent_df = pd.DataFrame(entities)

    # 4) 저장
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_csv(ent_df, output_path)
    logger.info(f"Entities saved to {output_path}, records={len(ent_df)}")

    return output_path


if __name__ == "__main__":
    # config 불러오기
    config = load_config()

    # latest_run.json 읽기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run previous steps first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    # 경로
    input_path = f"data/interim/{run_id}/cleaned.csv"      # 정제된 텍스트
    dict_programs = config["dictionaries"]["program_list"] # 프로그램 사전
    output_path = f"data/processed/{run_id}/entities.csv"  # 결과

    # 실행
    result = rule_based_ner(input_path, dict_programs, output_path)
    print(f"✅ NER completed: {result}")
