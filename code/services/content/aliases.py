# services/content/aliases.py
"""
Extract vendor/seller handles from HTML text you already have. Operates on
text already in hand — does no fetching of its own.
"""
import re
from bs4 import BeautifulSoup

# Vendor handles usually appear next to labels like "Vendor:", "Seller:", "by".
ALIAS_LABEL_RE = re.compile(
    r"(?:vendor|seller|user(?:name)?|by|shop|store)\s*[:\-]?\s*([A-Za-z0-9_\-\.]{3,32})",
    re.IGNORECASE,
)


def extract_aliases(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ")
    aliases: set[str] = set()
    for m in ALIAS_LABEL_RE.finditer(text):
        handle = m.group(1).strip()
        # Skip generic words that are not real handles
        if handle.lower() not in ("the", "and", "for", "with", "online"):
            aliases.add(handle)
    return sorted(aliases)


if __name__ == "__main__":
    sample = "<p>Vendor: DarkDealer42 - trusted seller since 2021</p>"
    print(extract_aliases(sample))
