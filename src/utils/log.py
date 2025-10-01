import logging
from pathlib import Path

def get_logger(name: str, log_file: str = None):
    """로거 생성"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:  # 중복 핸들러 방지
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

        # 콘솔 출력
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # 파일 로그
        if log_file:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(formatter)
            logger.addHandler(fh)

    return logger
