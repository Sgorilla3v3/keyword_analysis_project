from pathlib import Path
import yaml
from datetime import datetime

# 프로젝트 루트 (src/utils → src → project root)
BASE_DIR = Path(__file__).resolve().parents[2]

def create_run_id() -> str:
    """실행 시점 기준 고유 run_id 생성 (YYYYMMDD_HHMMSS)"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def load_config(config_path: str = None) -> dict:
    """
    config.yaml 불러오기 (항상 프로젝트 루트 기준).
    실행 위치에 관계없이 동작.
    """
    if config_path is None:
        config_path = BASE_DIR / "configs" / "config.yaml"

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {config_path}")

    # run_id 자동 생성
    if "run" not in config:
        config["run"] = {}
    if not config["run"].get("run_id"):
        config["run"]["run_id"] = create_run_id()

    return config
