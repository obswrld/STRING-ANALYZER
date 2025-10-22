from datetime import datetime
import hashlib
from collections import Counter

def analyze_string(value: str):
    if not isinstance(value, str):
        raise TypeError("Value must be a string")

    cleaned_value = value.strip()
    lowercase_value = cleaned_value.lower()

    length = len(cleaned_value)
    is_palindrome = lowercase_value == lowercase_value[::-1]
    unique_characters = len(set(lowercase_value))
    word_count = len(cleaned_value.split())
    sha256_hash = hashlib.sha256(cleaned_value.encode()).hexdigest()
    character_frequency_map = dict(Counter(lowercase_value))

    properties = {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha256_hash,
        "character_frequency_map": character_frequency_map,
    }

    analyzed_data = {
        "id": sha256_hash,
        "value": cleaned_value,
        "properties": properties,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    return analyzed_data