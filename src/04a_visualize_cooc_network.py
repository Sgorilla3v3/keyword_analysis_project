import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from utils.config import load_config
from sklearn.feature_extraction.text import CountVectorizer

def visualize_cooc_network(input_path, top_k=100, output_path=None):
    """
    cooc_edges.csv → 네트워크 그래프 시각화
    - input_path: cooc_edges.csv 경로
    - top_k: weight 기준 상위 N개 엣지 사용 (100 고정 추천)
    - output_path: 저장할 PNG 파일 경로
    """

    # 1. 데이터 불러오기
    df = pd.read_csv(input_path, encoding="utf-8-sig")

    # weight 기준 상위 N개만 사용
    df = df.sort_values("weight", ascending=False).head(top_k)

    # 2. 네트워크 생성
    G = nx.Graph()
    for _, row in df.iterrows():
        G.add_edge(row["source"], row["target"], weight=row["weight"])

    # 3. 레이아웃 (weight 반영 → 자주 등장하는 단어는 가까이)
    pos = nx.spring_layout(G, k=0.5, seed=42, weight="weight")

    # 4. 시각화
    plt.figure(figsize=(12, 8))

    # (1) 엣지: weight를 투명도에 반영 → 선은 얇게, 강한 관계는 진하게
    edges = nx.get_edge_attributes(G, "weight")
    max_w = max(edges.values()) if edges else 1
    nx.draw_networkx_edges(
        G, pos,
        width=1,
        alpha=[0.2 + (w / max_w) * 0.8 for w in edges.values()],
        edge_color="gray"
    )

    # (2) 노드: degree 기반 크기
    nx.draw_networkx_nodes(
        G, pos,
        node_size=0,
        node_color="none",
        alpha=0.0
    )

    # (3) 라벨: degree 기반 글씨 크기 조정
    node_degree = dict(G.degree())
    for node, (x, y) in pos.items():
        plt.text(
            x, y, s=node,
            fontsize=8 + 0.5 * node_degree.get(node, 0),  # degree 기반 크기
            ha="center", va="center",
            fontfamily="Malgun Gothic"  # 한글 깨짐 방지
        )

    plt.title(f"Word Co-occurrence Network (Top {top_k} edges)", fontsize=14)
    plt.axis("off")

    # 5. 저장 또는 출력
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"✅ Graph saved to {output_path}")
    else:
        plt.show()

def generate_ngrams(texts, ngram_min, ngram_max):
    vectorizer = CountVectorizer(ngram_range=(ngram_min, ngram_max)).fit(texts)
    return vectorizer.get_feature_names_out()

if __name__ == "__main__":
    # 1) config 불러오기 (co-occurrence 관련 파라미터만 사용)
    config = load_config()
    ngram_min = config["features"]["ngram_min"]
    ngram_max = config["features"]["ngram_max"]
    window_size = 15 # 관계성은 세밀하게 측정하고 많은 토큰을 이미지에 담기위해 윈도우를 코드에서 고정함
    min_cooc_count = config["features"]["min_cooc_count"]

    # 2) latest_run.json 읽기
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run 01_load_clean.py → 02_tokenize.py → 04_ngrams_cooc.py first.")

    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    # 3) 경로 (원하는 위치 고정)
    input_path = f"data/processed/{run_id}/cooc_edges.csv"
    output_path = f"data/processed/{run_id}/cooc_network.png"

    # 4) 실행 (top_k=100 고정)
    visualize_cooc_network(input_path, top_k=100, output_path=output_path)

