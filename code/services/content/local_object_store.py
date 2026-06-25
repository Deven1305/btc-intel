# services/content/local_object_store.py
"""
Replaces MinIO for this build. MinIO's open-source Community Edition was
archived by its maintainers in Feb 2026 (see setup/windows/04_minio_redis_
setup.md for the full timeline and sourcing) — the project now only ships
a paid AIStor product. Re-deriving Section 4C/6.8's object-storage layer
for June 2026, the honest answer for a single-laptop POC is a plain local
folder, which is what this module implements.

Same three operations a real S3-compatible client offers, so swapping in
a self-hosted alternative (Garage, SeaweedFS) or real AWS S3 later only
means rewriting this one file — nothing else in the pipeline calls
anything MinIO/S3-specific directly.
"""
import os
import time
from pathlib import Path

DEFAULT_ROOT = Path(os.path.expanduser("~")) / "btc-intel-data" / "archive"
RETENTION_DAYS = 90        # mirrors the original design's 90-day mc ilm lifecycle rule


class LocalObjectStore:
    def __init__(self, root: str | None = None):
        self.root = Path(root or os.getenv("LOCAL_ARCHIVE_PATH", DEFAULT_ROOT))
        self.root.mkdir(parents=True, exist_ok=True)

    def _path_for(self, key: str) -> Path:
        # keys may contain '/'-style separators; keep them as subfolders
        safe = key.replace("..", "_")
        p = self.root / safe
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def put_object(self, key: str, data: bytes | str) -> str:
        p = self._path_for(key)
        mode = "wb" if isinstance(data, bytes) else "w"
        with open(p, mode, encoding=None if isinstance(data, bytes) else "utf-8") as f:
            f.write(data)
        return key

    def get_object(self, key: str) -> bytes:
        with open(self._path_for(key), "rb") as f:
            return f.read()

    def delete_object(self, key: str) -> None:
        p = self._path_for(key)
        if p.exists():
            p.unlink()

    def enforce_retention(self, days: int = RETENTION_DAYS) -> int:
        """Delete anything older than `days`. Run this periodically (cron-equivalent:
        Windows Task Scheduler) — this is the local-folder version of the original
        design's `mc ilm` 90-day auto-delete lifecycle rule."""
        cutoff = time.time() - days * 86400
        removed = 0
        for p in self.root.rglob("*"):
            if p.is_file() and p.stat().st_mtime < cutoff:
                p.unlink()
                removed += 1
        return removed


if __name__ == "__main__":
    store = LocalObjectStore()
    key = store.put_object("test/example.html", "<html>hello</html>")
    print("stored:", key)
    print("read back:", store.get_object(key)[:20])
    print("removed by retention sweep:", store.enforce_retention(days=90))
