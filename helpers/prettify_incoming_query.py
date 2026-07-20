import re


def prettify_incoming_query(text: str):
    cleaned = text.lower()
    stop_words = r"\b(скачать|слушать|mp3|wav|flac|трек|песня|клип|музыка)\b"
    cleaned = re.sub(stop_words, "", cleaned)
    cleaned = re.sub(r"[^\w\s\-\']", "", cleaned)
    cleaned = cleaned.replace("_", " ")

    return re.sub(r"\s+", " ", cleaned).strip()
