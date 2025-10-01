import json
import pandas as pd
from pathlib import Path
from jinja2 import Template
from utils.log import get_logger
from utils.config import load_config

logger = get_logger(__name__)

def build_dashboard(run_id, output_path):
    """
    간단한 HTML 대시보드 생성
    - keywords, entities, word_dictionary 등 주요 결과를 요약해서 보여줌
    """
    # 1) 데이터 로드
    base_dir = Path(f"data/processed/{run_id}")
    files = {
        "keywords": base_dir / "keywords_top.csv",
        "entities": base_dir / "entities.csv",
        "word_dict": base_dir / "word_dictionary.csv",
    }

    data = {}
    for key, path in files.items():
        if path.exists():
            df = pd.read_csv(path, encoding="utf-8-sig")
            data[key] = df.head(20).to_html(index=False)
            logger.info(f"Loaded {key}: {df.shape}")
        else:
            data[key] = f"<p>No {key} file found.</p>"

    # 2) HTML 템플릿 (Jinja2)
    template = Template("""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Keyword Analysis Dashboard (Run {{ run_id }})</title>
        <style>
            body { font-family: sans-serif; margin: 20px; }
            h1 { color: #2c3e50; }
            table { border-collapse: collapse; margin-bottom: 30px; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 6px; font-size: 13px; }
            th { background-color: #f4f4f4; }
        </style>
    </head>
    <body>
        <h1>Keyword Analysis Dashboard</h1>
        <p><b>Run ID:</b> {{ run_id }}</p>

        <h2>Top Keywords</h2>
        {{ keywords | safe }}

        <h2>Entities</h2>
        {{ entities | safe }}

        <h2>Word Dictionary (Top 20)</h2>
        {{ word_dict | safe }}
    </body>
    </html>
    """)

    html = template.render(run_id=run_id, **data)

    # 3) 저장
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info(f"Dashboard saved: {output_path}")
    return output_path


if __name__ == "__main__":
    # config 불러오기
    config = load_config()

    # latest_run.json 불러오기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run previous steps first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    output_path = f"outputs/runs/{run_id}/dashboard/dash.html"

    result = build_dashboard(run_id, output_path)
    print(f"✅ Dashboard built: {result}")
