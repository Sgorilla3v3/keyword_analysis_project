import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import json

from utils.config import load_config
from utils.log import get_logger

logger = get_logger(__name__)

def visualize_with_dictionary(edges_path, dict_path, output_path, top_k=110, min_score=50):
    """
    cooc_edges.csv + word_dictionary.csv 기반 시각화
    - 중요 단어만 남기고 관계도를 그림
    - min_score: 사전에서 단어 필터링 기준
    """
    # 1) edge 데이터 로드
    edges_df = pd.read_csv(edges_path, encoding="utf-8-sig")
    logger.info(f"Loaded edges: {edges_df.shape}")

    # 2) word dictionary 로드
    dict_df = pd.read_csv(dict_path, encoding="utf-8-sig")
    logger.info(f"Loaded dictionary: {dict_df.shape}")

    # 3) 중요 단어 필터링
    important_words = dict_df[dict_df["score"] >= min_score]["word"].tolist()
    edges_df = edges_df[
        edges_df["source"].isin(important_words) &
        edges_df["target"].isin(important_words)
    ]
    logger.info(f"Filtered edges: {edges_df.shape}")

    # 4) top_k edge 추출
    edges_df = edges_df.sort_values("weight", ascending=False).head(top_k)

    # 5) 네트워크 생성
    G = nx.from_pandas_edgelist(edges_df, "source", "target", edge_attr="weight")

    # 6) 레이아웃
    pos = nx.spring_layout(G, k=0.5, seed=42)

    # (1) 엣지
    weights = [d["weight"] for _, _, d in G.edges(data=True)]
    max_w = max(weights) if weights else 1
    nx.draw_networkx_edges(
        G, pos,
        width=1,
        alpha=[0.2 + (w / max_w) * 0.8 for w in weights],
        edge_color="lightgray"
    )

    # (2) 노드: 투명 처리
    nx.draw_networkx_nodes(
        G, pos,
        node_size=1,      # 사실상 안보이게
        node_color="none",
        alpha=0.0
    )

    # (3) 라벨: score 기반 크기 조정 (정규화 방식)
    min_s, max_s = dict_df["score"].min(), dict_df["score"].max()
    score_dict = dict(zip(dict_df["word"], dict_df["score"]))
    
    for node in G.nodes():
        score = score_dict.get(node, 1)
        scaled = (score - min_s) / (max_s - min_s + 1e-9)
        font_size = int(6 + scaled * 10)  # 6 ~ 16pt 사이

        nx.draw_networkx_labels(
            G, pos,
            labels={node: node},
            font_size=font_size,  # score에 따라 글씨 크기
            font_family="Malgun Gothic"
        )

    plt.title(f"Word Network (Top {top_k} edges, score≥{min_score})", fontsize=14)
    plt.axis("off")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    logger.info(f"Graph saved: {output_path}")


if __name__ == "__main__":
    # latest_run.json 읽기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run previous steps first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    edges_path = f"data/processed/{run_id}/cooc_edges.csv"
    dict_path = f"data/processed/{run_id}/word_dictionary.csv"
    output_path = f"data/processed/{run_id}/cooc_network_dict.png"

    visualize_with_dictionary(edges_path, dict_path, output_path, top_k=110, min_score=50)
    print(f"✅ Visualization done. Output: {output_path}")
