import re


def get_hash_tags(performers: str):
    artists = re.sub(
        r"(\*|\/|\%|\$|\@|\.|№|\!|\?|\:|\;|\(|\)|\^|\=|\+|\"|\'|#)", "", performers
    )
    artists = artists.replace(" & ", ", ").replace("&", ", ")
    artists = re.sub(r"\—|\-", "_", artists)
    artists = artists.split(", ")
    tags = [("#" + a.replace(" ", "_")) for a in artists]
    return tags
