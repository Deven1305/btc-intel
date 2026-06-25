# services/content/dedup.py
"""
Deduplicate already-acquired pages via a SHA-256 content hash stored in
Redis, so the same archived/downloaded page is never processed twice.
Does no fetching of its own.
"""
import hashlib
import redis


class PageDeduplicator:
    def __init__(self, redis_client: redis.Redis, ttl_days: int = 30):
        self.r = redis_client
        self.ttl = ttl_days * 86400

    def seen_before(self, html: str) -> bool:
        h = hashlib.sha256(html.encode("utf-8", "ignore")).hexdigest()
        # SETNX returns False if key already existed -> we have seen this page
        is_new = self.r.set(f"pagehash:{h}", 1, nx=True, ex=self.ttl)
        return not is_new
