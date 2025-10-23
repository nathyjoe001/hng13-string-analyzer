import hashlib
from collections import Counter

def analyze_string(value: str):
    value_stripped = value.strip()
    hash_value = hashlib.sha256(value_stripped.encode()).hexdigest()
    is_palindrome = value_stripped.lower() == value_stripped[::-1].lower()
    unique_chars = len(set(value_stripped))
    words = value_stripped.split()
    char_freq = dict(Counter(value_stripped))

    return {
        "length": len(value_stripped),
        "is_palindrome": is_palindrome,
        "unique_characters": unique_chars,
        "word_count": len(words),
        "sha256_hash": hash_value,
        "character_frequency_map": char_freq
    }
