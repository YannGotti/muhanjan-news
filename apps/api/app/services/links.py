import re

URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def extract_links(text: str | None) -> list[str]:
    if not text:
        return []
    return list(dict.fromkeys(URL_RE.findall(text)))
