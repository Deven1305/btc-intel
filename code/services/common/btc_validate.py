# services/common/btc_validate.py
"""
A string matching a regex shape is NOT necessarily a real address — the
regex only checks shape. Real addresses carry a checksum. Validating it
discards garbage. Base58Check for P2PKH/P2SH; bech32/bech32m for SegWit
and Taproot. Pure math, no network calls.
"""
import base58  # pip install base58


def _valid_bech32(addr: str) -> bool:
    """Minimal bech32/bech32m validation (BIP-173/BIP-350)."""
    CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    addr = addr.lower()
    if not (addr.startswith("bc1") and 14 <= len(addr) <= 90):
        return False
    hrp, sep, data = addr.partition("1")
    if not sep or any(c not in CHARSET for c in data):
        return False

    def polymod(values):
        gen = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
        chk = 1
        for v in values:
            b = chk >> 25
            chk = ((chk & 0x1ffffff) << 5) ^ v
            for i in range(5):
                chk ^= gen[i] if (b >> i) & 1 else 0
        return chk

    def hrp_expand(h):
        return [ord(c) >> 5 for c in h] + [0] + [ord(c) & 31 for c in h]

    vals = hrp_expand(hrp) + [CHARSET.find(c) for c in data]
    const = polymod(vals)
    return const in (1, 0x2bc830a3)  # bech32 (v0) or bech32m (v1)


def is_valid_btc_address(addr: str) -> bool:
    """True if addr passes the checksum for its apparent format."""
    if not addr:
        return False
    if addr.lower().startswith("bc1"):
        return _valid_bech32(addr)
    try:
        decoded = base58.b58decode_check(addr)
        return len(decoded) == 21  # 1 version byte + 20 hash bytes
    except Exception:
        return False


def classify_address_type(addr: str) -> str | None:
    """Return P2PKH / P2SH / BECH32 / BECH32M for a *validated* address, else None."""
    if not is_valid_btc_address(addr):
        return None
    if addr.lower().startswith("bc1p"):
        return "BECH32M"
    if addr.lower().startswith("bc1"):
        return "BECH32"
    if addr.startswith("1"):
        return "P2PKH"
    if addr.startswith("3"):
        return "P2SH"
    return None


if __name__ == "__main__":
    tests = [
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",   # real, valid (Genesis block address)
        "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfN0",   # corrupted checksum
        "bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq",  # valid bech32
        "not-an-address",
    ]
    for t in tests:
        print(t, "->", is_valid_btc_address(t), classify_address_type(t))
