# analyzer/utils.py
from collections import Counter
import hashlib

def analyze_string(value: str) -> dict:
    if value is None:
        raise ValueError("value required")
    length = len(value)
    is_pal = value.lower() == value.lower()[::-1]
    unique_chars = len(set(value))
    word_count = len(value.split())
    sha = hashlib.sha256(value.encode()).hexdigest()
    freq_map = dict(Counter(value))
    return {
        "length": length,
        "is_palindrome": is_pal,
        "unique_characters": unique_chars,
        "word_count": word_count,
        "sha256_hash": sha,
        "character_frequency_map": freq_map,
    }
