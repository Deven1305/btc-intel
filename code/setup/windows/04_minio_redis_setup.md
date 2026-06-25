# setup/windows/04_minio_redis_setup.md

## Important update: MinIO's open-source edition has been discontinued

Before answering "why an object store at all" (your item 6), there's a
fact check that changes the recommendation: **MinIO's free/open-source
Community Edition is no longer a safe choice for a new project as of
June 2026.** Timeline, confirmed from multiple independent sources:

- Dec 3, 2025 — MinIO put the open-source repo into "maintenance mode":
  no new features, no Docker images, no RPM/DEB packages.
- Feb 12, 2026 — the GitHub repo was marked "THIS REPOSITORY IS NO LONGER
  MAINTAINED" and archived.
- Pre-compiled binaries for the Windows single-binary install this
  project's original design relied on were discontinued; the only
  remaining path for the free edition is building from Go source yourself,
  with no guaranteed security patches going forward.
- MinIO's own guidance redirects everyone to **AIStor**, their commercial
  product — entry-tier pricing reported in the tens of thousands of
  dollars per year, with a free tier that requires a license file and is
  scoped to a single node.

This means a core assumption behind the original Section 4C/6.8 design —
"self-hosted, free, S3-compatible, single binary, no ops" — is no longer
true for MinIO specifically. The architecture's reasoning about *why you'd
want* an S3-compatible store is still sound; the specific product
recommendation needs to change.

## Honest answer to "do I even need an object store on a single laptop?"

Walking through your question directly, with the MinIO situation factored in:

- **Versioning / lifecycle automation (`mc ilm`, 90-day auto-delete)**: a
  genuinely nice feature, but a five-line Python script using `os.stat()` to
  check file age and `os.remove()` on anything older than 90 days does the
  same job for a single-laptop POC. You lose nothing meaningful by not
  having `mc ilm` here.
- **At-rest encryption (`mc encrypt set sse-s3`)**: nice for genuinely
  sensitive data at rest, but for a POC where the underlying data is
  already-acquired archive content (not live-crawled dark web pages — see
  README "Dark web data"), this is a smaller concern than it would be for
  a 24/7 production crawler's output.
  Windows BitLocker (free, built into Windows Pro, full-disk encryption)
  covers the "data at rest is encrypted" requirement without needing an
  application-layer feature at all.
- **Migration path toward a production S3 bucket later (File B)**: this
  was MinIO's strongest selling point — same API now, zero rewrite later.
  Given MinIO Community is no longer being maintained, this argument no
  longer favors MinIO specifically. It DOES still favor *picking something
  S3-API-compatible* in general, so a future swap to real AWS S3 stays
  cheap.

**The honest answer: for this single-laptop POC, a plain folder + a small
Python helper would work fine, and is what this build uses by default.**
This isn't a downgrade in capability for what the POC actually needs — see
`services/content/local_object_store.py` below.

If you want to keep the original S3-compatible-API property (useful if you
already know File B will target real cloud S3 later, and you'd rather not
touch this code again when that happens), the current credible
self-hosted S3-compatible alternatives as of June 2026 are **Garage**
(simplest, "anti-complexity" design philosophy, good fit for a
single-node POC) or **SeaweedFS**. Either would slot into the same
`services/content/object_store.py` interface shown below if you want it
later — the rest of this codebase only calls `put_object` /
`get_object` / `delete_object`, never anything MinIO-specific, so swapping
the backend later is a small, contained change.

---

## What this build actually uses: a plain local folder

[Windows: nothing to install — this is pure Python, already in `requirements.txt`]

See `services/content/local_object_store.py`. It implements the same
three operations (`put_object`, `get_object`, `delete_object`) a real
S3-compatible client would, backed by a folder on disk
(`%USERPROFILE%\btc-intel-data\archive\` by default, configurable via
`.env`), with the same 90-day-retention behavior as the original `mc ilm`
lifecycle rule, implemented as a small cleanup function you run
periodically (or schedule via Windows Task Scheduler if you want it
automatic).

This is what `archive_key` in `dark_web_records` (see `schema/001_init.sql`)
refers to: a key into this local store, not a MinIO bucket key. The
column name is unchanged from the original schema so the rest of the
pipeline (and a future swap to Garage/SeaweedFS/real S3) doesn't need to
change.

---

## Redis setup (unaffected by the MinIO situation — still the right choice)

Redis itself is fine and current; only MinIO's licensing changed. Redis
doesn't ship a first-party Windows build, so the simplest path on Windows
is the official Docker image (you already have Docker if you set up the
VirtualBox VM's Splash container in `01_virtualbox_vm_setup.md`, but Redis
itself runs natively on the host, not inside that VM — Docker Desktop for
Windows runs containers directly on the host).

[Windows cmd/PowerShell — requires Docker Desktop for Windows, a separate
free download from https://www.docker.com/products/docker-desktop/ if you
don't already have it]
```
docker run -d --name btcintel-redis -p 6379:6379 redis:7-alpine
```

Verify:
```
docker exec -it btcintel-redis redis-cli ping
```
Expect: `PONG`.

To stop/start it later:
```
docker stop btcintel-redis
docker start btcintel-redis
```

## Update `.env`

```
REDIS_URL=redis://localhost:6379/0
LOCAL_ARCHIVE_PATH=C:\Users\<you>\btc-intel-data\archive
```
