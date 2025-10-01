import json
import pandas as pd
from pathlib import Path
import argparse
from utils.io import write_csv
from utils.log import get_logger
from utils.config import load_config
import networkx as nx
import networkit as nk

logger = get_logger(__name__)

def compute_network_stats_full(input_path, output_path):
    """
    cooc_edges.csv → 고속 네트워크 지표 계산 (Networkit 기반)
    - degree
    - weighted_degree
    - betweenness (병렬)
    - closeness (병렬) 제거됨
    """

    df = pd.read_csv(input_path, encoding="utf-8-sig")
    logger.info(f"Loaded {len(df)} edges from {input_path}")

    # NetworkX → Networkit 변환
    G_nx = nx.Graph()
    for _, row in df.iterrows():
        G_nx.add_edge(row["source"], row["target"], weight=row["weight"])
    G = nk.nxadapter.nx2nk(G_nx, weightAttr="weight")

    # Degree / Weighted degree
    deg = nk.centrality.DegreeCentrality(G, normalized=False).run().scores()
    wdeg = nk.centrality.DegreeCentrality(G, normalized=False, outDeg=True).run().scores()

    # Betweenness (병렬, 근사 아님)
    bc = nk.centrality.Betweenness(G, normalized=True).run().scores()

    # Closeness 제거


    # 노드명 가져오기
    nodes = list(G_nx.nodes())

    stats = []
    for i, node in enumerate(nodes):
        stats.append({
            "word": node,
            "degree": deg[i],
            "weighted_degree": wdeg[i],
            "betweenness": round(bc[i], 5)
            #"closeness": round(cc[i], 5)
        })

    stats_df = pd.DataFrame(stats)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    write_csv(stats_df, output_path)

    logger.info(f"Node stats (full) saved to {output_path}, records={len(stats_df)}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute FULL network stats (degree, betweenness, closeness)")
    args = parser.parse_args()

    config = load_config()
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run until 04_ngrams_cooc.py first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    input_path = f"data/processed/{run_id}/cooc_edges.csv"
    output_path = f"data/processed/{run_id}/cooc_nodes_full.csv"

    result = compute_network_stats_full(input_path, output_path)
    print(f"✅ FULL Network stats computed. Output: {result}")
