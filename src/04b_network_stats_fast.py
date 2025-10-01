import json
import pandas as pd
import networkx as nx
from pathlib import Path
import argparse
from utils.io import write_csv
from utils.log import get_logger
from utils.config import load_config

logger = get_logger(__name__)

def compute_network_stats_fast(input_path, output_path):
    """
    cooc_edges.csv → 빠른 네트워크 지표 계산
    - degree
    - weighted_degree
    """

    df = pd.read_csv(input_path, encoding="utf-8-sig")
    logger.info(f"Loaded {len(df)} edges from {input_path}")

    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["source"], row["target"], weight=row["weight"])

    degree_dict = dict(G.degree())
    weighted_degree_dict = dict(G.degree(weight="weight"))

    stats = []
    for node in G.nodes():
        stats.append({
            "word": node,
            "degree": degree_dict.get(node, 0),
            "weighted_degree": weighted_degree_dict.get(node, 0)
        })

    stats_df = pd.DataFrame(stats)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_csv(stats_df, output_path)

    logger.info(f"Node stats (fast) saved to {output_path}, records={len(stats_df)}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute FAST network stats (degree only)")
    args = parser.parse_args()

    config = load_config()
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run until 04_ngrams_cooc.py first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    input_path = f"data/processed/{run_id}/cooc_edges.csv"
    output_path = f"data/processed/{run_id}/cooc_nodes_fast.csv"

    result = compute_network_stats_fast(input_path, output_path)
    print(f"✅ FAST Network stats computed. Output: {result}")
