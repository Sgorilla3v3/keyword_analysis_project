import subprocess
import sys
import argparse

# 실행 단계 정의
STEPS = [
    ("01_load_clean.py", []),
    ("02_tokenize.py", []),
    ("03_keywords_tfidf.py", []),
    ("04_ngrams_cooc.py", []),
    ("04b_network_stats.py", ["--mode", "fast"]),   # fast 모드 기본
    ("04a1_word_dictionary.py", []),
    ("04a2_visualize_with_dictionary.py", [])
]

def run_step(step, args):
    """단일 스텝 실행"""
    script, extra_args = step
    cmd = [sys.executable, f"src/{script}"] + extra_args
    print(f"\n=== Running {script} ===")
    print(" ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ Step failed: {script}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run keyword analysis pipeline")
    parser.add_argument("--full", action="store_true",
                        help="Use full network stats (04c) instead of fast mode")
    args = parser.parse_args()

    steps = STEPS.copy()

    if args.full:
        # 04c_networkit_stats_full.py 사용
        steps[4] = ("04c_networkit_stats_full.py", [])

    for step in steps:
        run_step(step, args)

    print("\n✅ Pipeline completed successfully!")
