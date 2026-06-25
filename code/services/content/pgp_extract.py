# services/content/pgp_extract.py
"""
Extract PGP fingerprints from HTML text you already have on disk (e.g. an
archived DUTA-10K/Gwern page, or any other already-downloaded document).
This module does no fetching of its own.

Why PGP fingerprints matter: a PGP fingerprint is a 40-hex-character
identifier derived cryptographically from a public key, unique for
practical purposes to one key. If vendor "X" on one page and vendor "Y" on
another both publish the same fingerprint, they are — with cryptographic
certainty — the same operator. No fuzzy matching, no probability.
"""
import re
import pgpy  # pip install PGPy13 (package name on PyPI is "PGPy13", but it still
              # imports as `pgpy` — the original PGPy 0.6.0 release breaks on
              # Python 3.13+ due to a removed stdlib module; PGPy13 is the
              # maintained drop-in fork that fixes this, see requirements.txt)

PGP_BLOCK = re.compile(
    r"-----BEGIN PGP PUBLIC KEY BLOCK-----.*?-----END PGP PUBLIC KEY BLOCK-----",
    re.DOTALL,
)
PGP_FP_BARE = re.compile(r"\b([0-9A-Fa-f]{40})\b")  # a 40-hex token (possible fingerprint)


def extract_pgp_fingerprints(html: str) -> list[str]:
    fps: set[str] = set()
    # 1) Full key blocks -> derive the canonical fingerprint
    for block in PGP_BLOCK.findall(html):
        try:
            key, _ = pgpy.PGPKey.from_blob(block)
            fps.add(str(key.fingerprint).upper().replace(" ", ""))
        except Exception:
            pass
    # 2) Bare 40-hex fingerprints printed on the page
    for cand in PGP_FP_BARE.findall(html):
        fps.add(cand.upper())
    return sorted(fps)


if __name__ == "__main__":
    sample = "Contact me, fingerprint: 1A2B3C4D5E6F7890ABCDEF1234567890ABCDEF12"
    print(extract_pgp_fingerprints(sample))
