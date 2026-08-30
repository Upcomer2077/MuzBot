import re


def prettify_incoming_query(text: str):
    """Clean and normalize the user's raw text query by stripping download keywords, punctuation, and extra spaces.

    Args:
        text: The raw search string received from the user.

    Returns:
        A cleaned, lowercase string optimized for searching in YouTube Music.
    """
    cleaned = text.lower()
    stop_words = r"\b(скачать|слушать|mp3|wav|flac|трек|песня|клип|музыка)\b"
    cleaned = re.sub(stop_words, "", cleaned)
    cleaned = re.sub(r"[^\w\s\-\'\.]", "", cleaned)
    cleaned = cleaned.replace("_", " ")

    return re.sub(r"\s+", " ", cleaned).strip()
