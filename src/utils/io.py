import json
import os
from pathlib import Path
import pandas as pd

def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def load_json(path: str | Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def read_json(file_path: str):
    """JSON 파일 읽기"""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(obj, path: str | Path) -> None:
    ensure_dir(Path(path).parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def write_csv(df: pd.DataFrame, file_path: str):
    """CSV 저장 (UTF-8-SIG)"""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")
    return str(file_path)

def write_excel(df: pd.DataFrame, path: str | Path) -> None:
    ensure_dir(Path(path).parent)
    df.to_excel(path, index=False)

def concat_text(row, fields):
    return " ".join([str(row.get(f, "")) for f in fields if f in row and row.get(f)]).strip()

def read_csv(path):
    """CSV 파일 읽기 (utf-8-sig 기본)"""
    return pd.read_csv(path, encoding="utf-8-sig")

def write_csv(df, path):
    """CSV 파일 저장"""
    df.to_csv(path, index=False, encoding="utf-8-sig")