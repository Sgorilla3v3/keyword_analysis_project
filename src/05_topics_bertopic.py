import json
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from utils.config import load_config
from utils.io import write_csv
from utils.log import get_logger

logger = get_logger(__name__)

def run_lda(docs, num_topics=8, max_features=3000):
    vectorizer = CountVectorizer(max_df=0.95, min_df=5, max_features=max_features)
    dtm = vectorizer.fit_transform(docs)
    lda = LatentDirichletAllocation(n_components=num_topics, random_state=42)
    lda.fit(dtm)
    return lda, vectorizer, dtm

if __name__ == "__main__":
    # config & run_id
    config = load_config()
    latest_run_file = Path("data/interim/latest_run.json")
    if not latest_run_file.exists():
        raise RuntimeError("❌ latest_run.json not found. Please run until 02_tokenize.py first.")
    with open(latest_run_file, "r", encoding="utf-8") as f:
        latest = json.load(f)
        run_id = latest["run_id"]

    input_path = f"data/interim/{run_id}/cleaned.csv"
    output_dir = Path(f"data/processed/{run_id}")
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path, encoding="utf-8")
    docs = df["cleaned_text"].astype(str).tolist()

    lda, vectorizer, dtm = run_lda(
        docs,
        num_topics=config["topic_modeling"]["num_topics"],
        max_features=config["topic_modeling"]["max_features"]
    )

    # 토픽별 키워드 저장
    topic_words = []
    for idx, topic in enumerate(lda.components_):
        terms = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[:-11:-1]]
        topic_words.append({"topic": idx, "top_words": ", ".join(terms)})
    write_csv(pd.DataFrame(topic_words), output_dir / "topics_topwords.csv")

    # 문서별 토픽 할당 저장
    doc_topics = lda.transform(dtm).argmax(axis=1)
    df["topic"] = doc_topics
    write_csv(df[["id","date", "topic"]], output_dir / "topics.csv")

    logger.info(f"Topics saved to {output_dir}")
    print(f"✅ Topics computed. Outputs in {output_dir}")
