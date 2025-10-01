import re

URL_RE = re.compile(r'https?://\S+')
EMOJI_RE = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)

def basic_clean(text: str, remove_urls=True, remove_emojis=True, to_lower=True) -> str:
    if not isinstance(text, str):
        return ""
    if remove_urls:
        text = URL_RE.sub(" ", text)
    if remove_emojis:
        text = EMOJI_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if to_lower:
        text = text.lower()
    return text

clean_text = basic_clean