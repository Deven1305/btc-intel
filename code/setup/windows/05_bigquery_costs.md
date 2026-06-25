# setup/windows/05_bigquery_costs.md

Verified against current Google Cloud documentation (last checked June
2026 — re-check https://cloud.google.com/bigquery/pricing and
https://docs.cloud.google.com/bigquery/docs/sandbox yourself before a demo,
since these terms can change).

## Is the "1 TiB query processing free per month" claim still accurate?

**Yes, still accurate as of June 2026, with one important nuance the
original design's wording blurred.** There are actually **two separate
free mechanisms**, not one:

1. **BigQuery Sandbox** — no billing account, no credit card, ever. You
   sign in with a plain Google account and get the same limits as #2
   below (10 GiB storage, 1 TiB query processing/month), but with extra
   restrictions: all tables/views/partitions auto-expire after **60
   days**, and you can't use streaming inserts, DML (UPDATE/DELETE), or
   the Data Transfer Service.
2. **BigQuery free usage tier** — requires a **billing account** attached
   to the project (meaning you've entered a credit card at some point),
   but is otherwise a **permanent, recurring monthly allowance**: 10 GiB
   storage + 1 TiB query processing, free, every month, indefinitely, with
   no 60-day table expiration and full feature support (DML, streaming,
   etc.).

## Is this the same thing as the "$300/90-day new-customer credit"?

**No — these are two different mechanisms with different terms, and
conflating them (as informal explanations often do) is exactly the trap
your question anticipated:**

| | BigQuery free tier (#2 above) | $300/90-day GCP credit |
|---|---|---|
| Requires billing account/card | Yes | Yes |
| Expires | **Never** — recurring monthly allowance | **Yes** — 90 days after signup, or when the $300 is spent, whichever comes first |
| Scope | BigQuery query processing + storage specifically | Any Google Cloud product |
| What happens after it's gone | Nothing — the BigQuery free tier keeps renewing every month forever | You're on pay-as-you-go for everything unless you stay under other specific free allowances |

The $300 credit is a generous bonus for your first 90 days, but the thing
that actually matters for a project that might be re-run/re-demoed months
apart is the **permanent monthly BigQuery free tier**, not the credit.

## Does this project need a billing account / credit card at all?

**It depends on which path you pick, and this is the one place where the
original design's "needs no credit card" claim needs a caveat:**

- If you use the **BigQuery Sandbox** (no card, ever): you get the same
  1 TiB/month query allowance, **but every table you create — including
  any cached/expanded graph data you write back to BigQuery itself —
  auto-deletes after 60 days.** Since this project caches expansion
  results to **PostgreSQL** (see `services/blockchain/expand.py`'s
  `graph_cache` table — a Gap I found vs. the original design, explained
  there), not back into BigQuery tables, the 60-day auto-expiry mostly
  doesn't bite you: your cache lives in Postgres on your own machine
  indefinitely, and you're only ever reading from BigQuery's public
  `crypto_bitcoin` dataset (which isn't yours to expire) and writing your
  own *query results* into your local Postgres cache, not into new
  BigQuery tables.
- So: **the Sandbox (zero card, zero billing account) is sufficient for
  this project's actual usage pattern**, precisely because the caching
  fix routes saved data to Postgres instead of back into BigQuery. This
  is a meaningfully different/better answer than "you'll need a card
  eventually" — you don't, given how this build uses BigQuery (read public
  data, cache results locally).
- The one reason you'd attach a billing account anyway: if you ever want
  data to persist past 60 days **inside BigQuery itself** (e.g. you want
  to keep an intermediate table in BigQuery rather than exporting it), or
  you want DML/streaming features the Sandbox blocks. Neither applies to
  the pipeline as built here.

## Does a 50-seed, 3-hop expansion (~310 GB, per Section 14.4's sample
output) stay inside either mechanism?

**Yes, comfortably**, under either the Sandbox or the billing-enabled free
tier — both offer the same 1 TiB (≈1024 GB)/month query-processing
allowance, and ~310 GB is well under that, leaving headroom for a second
or even third full re-run in the same calendar month if your demo needs
it. The real risk isn't the allowance size — it's **re-running the same
expansion repeatedly without caching**, which is exactly what
`services/blockchain/expand.py`'s `graph_cache` table fix prevents (see
that file's docstring and `schema/001_init.sql`'s `graph_cache` table for
the implementation, listed under "Gap I found" in the README).

## How to actually save/export results so you don't re-burn the allowance

Already implemented: `GraphExpander.expand()` in
`services/blockchain/expand.py` hashes `(sorted(seeds), max_hops)` into a
cache key, checks `graph_cache` in Postgres before calling BigQuery at
all, and only queries BigQuery on an actual cache miss. Re-running the
dashboard, re-demoing the same seed list, or restarting your laptop never
re-triggers a BigQuery query for an expansion you've already paid
free-tier quota for once — it's a pure Postgres read instead.

## Bottom line for your setup instructions

Use the **BigQuery Sandbox**: sign in to https://console.cloud.google.com
with a plain Google account, create a project, open BigQuery — the
Sandbox activates automatically, no card needed at any point. This is
sufficient for everything `expand_graph.py` does in this build.
