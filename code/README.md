# BTC-Intel — POC README

A Bitcoin-wallet criminal-intelligence POC: combines OFAC/sanctions seed
data, blockchain graph analysis, and a Bayesian risk engine to classify
Bitcoin addresses as `BLACKLISTED` / `WATCHLISTED` / `PRE_CRIME_WATCHLIST`
/ `CLEAN`. Re-derived from the original architecture document for two
single-user Windows machines (a 24 GB laptop and a 32 GB desktop) instead
of a bare-metal Ubuntu college server.

**One thing this build does NOT include, on purpose:** a live dark-web
crawler or multi-search-engine .onion discovery system. Everything else —
OFAC/UN/community blacklist ingestion, BigQuery graph expansion,
clustering, taint propagation, the Bayesian risk engine, the PRE_CRIME
watchlist mechanism, the Streamlit dashboard, and pluggable LLM narration
(Gemini/Ollama/Hugging Face) — is implemented in full, runnable code. See
"Dark web data" below for what's here instead and why.

---

## 0. Dark web data: what's here instead of a live crawler

This build does not crawl the open dark web. What it does instead:

- **`scripts/ingest_archive.py`** runs the full content-extraction pipeline
  (address regex + checksum validation, PGP fingerprint extraction,
  context/topic classification, alias extraction) against **HTML files
  you already have on disk** — already-acquired archive content you have
  independent, legitimate access to.
- The Tor/Splash stack in `setup/windows/01_virtualbox_vm_setup.md` is
  included for completeness and because the VM-isolation pattern it
  demonstrates is good practice, but nothing in this repo invokes it to
  fetch live `.onion` content.

### Where to get archive content to ingest

- **DUTA-10K** (Al Nabki et al., 2019) — the standard academic darknet-text
  corpus referenced by the original architecture doc. Important
  correction: DUTA-10K is **request-based, "academic research purposes
  only," granted directly by the paper's authors** — there is no public
  download link. Several published papers reproducing DUTA-10K also note
  that the dataset itself ships as a list of manually-tagged `.onion`
  links rather than the full page content, meaning recipients have
  historically had to re-fetch the linked pages themselves to get text —
  so even with access granted, treat this as a multi-step, multi-week
  process: (1) find the current corresponding author's contact info from
  the paper ("DUTA-10K: A Parallel Corpus for Deep Learning and Cross-
  Lingual Embeddings" / the ToRank paper, Al Nabki et al.), (2) email
  requesting access for your stated academic purpose, (3) expect this to
  take real calendar time to hear back — start this well before any demo
  date, ideally weeks in advance, since you're depending on another
  researcher's response time and there's no published SLA. There is no
  guarantee of access; treat it as a stretch goal, not the primary path.
- **Elliptic dataset** (Kaggle): https://www.kaggle.com/datasets/ellipticco/elliptic-data-set
  — this is the labeled Bitcoin **transaction graph** (203,769 nodes,
  234,355 edges, ~4,500 labeled illicit / ~42,000 labeled licit), used
  here for `services/eval/harness.py`'s baseline reproduction, not for
  dark-web text content. Free Kaggle account required, no special request
  process.
- **Gwern's archive**: Gwern Branwen has published writeups and partial
  archives related to darknet markets (e.g. the "Darknet Market Archives"
  project) at https://gwern.net/dnm-archive — review the specific
  licensing/usage terms on that page for whatever subset you use, since
  terms can vary by sub-archive.
- **Your own legitimately-acquired content**: if you have independent,
  legitimate access to any other already-downloaded `.html`/`.htm` files
  you're licensed to analyze, point `ingest_archive.py --input-dir` at
  them directly.

---

## 1. Setup, in order

1. `setup/windows/01_virtualbox_vm_setup.md` — VirtualBox + Ubuntu Server
   VM (only needed if you want the Tor/Splash stack at all; **skip this
   entirely** if you're only using `ingest_archive.py`).
2. `setup/windows/02_postgresql_setup.md` — PostgreSQL 16, from zero.
3. `setup/windows/03_neo4j_setup.md` — Neo4j **Community** Edition
   (standalone zip, not Neo4j Desktop — see that file for why).
4. `setup/windows/04_minio_redis_setup.md` — **important correction**:
   MinIO's open-source edition was discontinued in Feb 2026; this build
   uses a plain local folder instead (`services/content/
   local_object_store.py`), plus Redis via Docker.
5. `setup/windows/05_bigquery_costs.md` — corrected free-tier/billing
   facts (the original "$300 credit = free tier" framing conflated two
   different mechanisms — see that file for the actual distinction).
6. `setup/windows/06_resource_budget.md` — RAM/CPU/disk budget for both
   your 24 GB and 32 GB machines, with honest guidance on what to reduce
   if the 24 GB laptop gets tight.
7. `setup/windows/07_package_gotchas.md` — `pyzbar`, `pytesseract`,
   `PGPy`/`PGPy13` Windows/Python-version-specific install notes.

Then:
```
[Anaconda Prompt] setup\windows\day1_setup_windows.ps1
```
(Optional, only if using the Tor/Splash VM:)
```
[Inside Ubuntu VM] bash setup/linux_vm/day1_setup_vm.sh
```

---

## 2. Datasets referenced in this project

**For full click-by-click signup/download steps, see
`setup/windows/08_dataset_downloads.md`.** Summary:

| Dataset | URL | Access |
|---|---|---|
| OFAC SDN list | https://www.treasury.gov/ofac/downloads/sdn.xml | Free, no signup |
| OFAC mirror (0xB10C) | https://github.com/0xB10C/ofac-sanctioned-digital-currency-addresses | Free, no signup |
| UN Consolidated Sanctions List | https://scsanctions.un.org/resources/xml/en/consolidated.xml | Free, no signup |
| Chainabuse | https://www.chainabuse.com/ | Free API key, **10 calls/month limit** (corrected — not a daily quota) |
| MistTrack | https://misttrack.io/ | **Corrected: no longer free** — paid Standard/Compliance plan or x402 pay-per-call. Optional, skip if you don't want to pay. |
| CryptoScamDB | https://api.cryptoscamdb.org/v1/addresses | Free, no signup |
| SlowMist blockchain-blacklist | https://github.com/slowmist/blockchain-blacklist | Free, no signup |
| Elliptic dataset | https://www.kaggle.com/datasets/ellipticco/elliptic-data-set | Free Kaggle account |
| DUTA-10K | Contact paper authors (Al Nabki et al.) directly — no public link | Academic request, no guarantee, plan for weeks of lead time |
| Gwern's Darknet Market Archives | https://gwern.net/dnm-archive | Review per-archive license terms |
| BigQuery `crypto_bitcoin` public dataset | Built into BigQuery — `bigquery-public-data.crypto_bitcoin` | Free via Sandbox, no card (see `05_bigquery_costs.md`) |
| WalletExplorer (service labels) | https://www.walletexplorer.com/ | Free, no signup (scraped per `services/seeds/walletexplorer.py`) |

---

## 3. Demo-data checklist

Before leaving for a demo:
```
[Anaconda Prompt] python scripts/demo_checklist.py
```
This checks `seed_addresses`, `service_labels`, `dark_web_records`,
`pre_crime_watchlist`, `graph_cache`, `risk_decisions`, and
`evaluation_results` all have non-trivial row counts, and tells you
exactly which script to run if any are empty.

---

## 4. Full day-1 run sequence

```
[Windows cmd/PowerShell]  setup\windows\day1_setup_windows.ps1
    -> creates venv, installs requirements, copies .env.example -> .env (EDIT IT),
       loads schema, runs collect_seeds.py, launches the dashboard

[Anaconda Prompt]  python scripts/ingest_archive.py --input-dir <path to your archive HTML>
[Anaconda Prompt]  python scripts/expand_graph.py --hops 2 --seeds-from-db --limit-seeds 20
[Anaconda Prompt]  python scripts/demo_shared_wallet.py
[Anaconda Prompt]  python scripts/run_eval.py
[Anaconda Prompt]  python scripts/demo_checklist.py
[Anaconda Prompt]  streamlit run dashboard/app.py --server.port 8501
```

---

## 5. Demo scenarios (updated from the original Section 15.1)

| # | What to show | What it proves | Expected output |
|---|--------------|----------------|-----------------|
| 1 | Paste a known OFAC address. | Phase 1 ground truth + Layer-1 fast path. | **BLACKLISTED**, confidence 1.0, evidence `OFAC_SDN`; counterfactual "N/A — deterministic." |
| 2 | Paste an address 1 hop from an OFAC seed. | Taint propagation. | **WATCHLISTED**, evidence `TAINT_HOP_1` with the BTC amount. |
| 3 | Paste a dark-web PAYMENT-context address with zero on-chain history. | **The core novel contribution.** | **PRE_CRIME_WATCHLIST**, evidence `DARK_WEB_PAYMENT` + onion domain + topic; appears in the live table. |
| 4 | Paste a known exchange hot-wallet address. | False-positive protection (taint barrier). | **CLEAN**, evidence `EXCHANGE_VERIFIED`; taint stops at the exchange. |
| 5 | Show two addresses linked by the same PGP fingerprint. | PGP entity linking (`services/content/pgp_extract.py`). | Both resolve to one entity; `PGP_CRIMINAL_LINK` evidence shown. |
| 6 | Show the precision/recall table: BTC-Intel vs naive single-hop OFAC taint. | The system beats the baseline. | Table where BTC-Intel recall > naive recall at comparable precision. |
| 7 | Click "Generate Investigation Brief" on a BLACKLISTED address. | The grounded LLM layer — **now backend-selectable** (sidebar toggle: Gemini / Ollama / Hugging Face), not Claude-only as in the original design. | A 4-section brief citing only the computed evidence sources, generated by whichever backend you picked. |
| 8 | Walk through the dark-web ingestion approach. | **Updated from the original's crawler-coverage walkthrough.** | Explain that `ingest_archive.py` processes already-acquired archive content rather than live-crawling — show the extraction pipeline (regex → checksum → context classification → PGP/alias extraction) running against sample files. |

---

## 6. What changed vs. the original architecture document, and why

| Area | Original | This build | Why |
|---|---|---|---|
| Hypervisor | KVM/libvirt on bare-metal Ubuntu | VirtualBox on Windows | No bare-metal host available; VirtualBox gives the same VM-isolation property (see `01_virtualbox_vm_setup.md`) |
| Dark web data acquisition | Live multi-engine `.onion` crawler | `ingest_archive.py` against already-acquired archive content | See "Dark web data" section above |
| LLM narration | Anthropic Claude API only | Pluggable: Gemini (default, free) / Ollama (offline) / Hugging Face (free hosted) | No paid API key available; `services/llm/brief.py` abstracts the backend |
| Object storage | MinIO | Plain local folder (`services/content/local_object_store.py`) | MinIO's open-source edition was discontinued Feb 2026 — see `04_minio_redis_setup.md` for sourcing and the honest "do you even need an object store" analysis |
| BigQuery cost framing | "$300 credit = the free tier" | Two distinct mechanisms (Sandbox vs. billing-enabled free tier) clearly separated | See `05_bigquery_costs.md` |
| Graph expansion caching | Re-queries BigQuery every run | **Gap I found:** added `graph_cache` table + cache-check in `expand.py` | Prevents re-burning the 1 TiB/month free-tier allowance on repeat demos |
| PGPy version | `PGPy==0.6.0` | `PGPy13==0.6.1rc1` | **Gap I found:** original PGPy breaks on Python 3.13+ (removed `imghdr` stdlib module); PGPy13 is the maintained fork that fixes this |
| Neo4j install path | Implied Neo4j Desktop or generic install | Standalone Community zip, explicitly NOT Neo4j Desktop | **Gap I found:** Neo4j Desktop bundles Enterprise Developer edition, not Community, which the architecture doc's Section 4 specifically requires |
| Chainabuse rate limit | Assumed 100 requests/day | Corrected to 10 calls/month (the real current free-tier limit) | **Gap I found:** the original figure was wrong; this changes how often you can safely refresh seeds |
| MistTrack pricing | Assumed free, 100 queries/day | Corrected: no longer free — paid plan or x402 pay-per-call required; module made fully optional | **Gap I found:** MistTrack's free tier was discontinued; the pipeline no longer depends on it |
| Resource budget | One table for a 16-32 GB server | Separate tables for your 24 GB and 32 GB machines, with explicit "what to reduce if tight" guidance | Section 4D didn't map directly to either of your machines |

---

## 7. Repository layout

```
btc-intel/
├── services/
│   ├── common/          btc_patterns.py, btc_validate.py, coinjoin.py
│   ├── seeds/            ofac.py, ofac_mirror.py, un.py, chainabuse.py,
│   │                     cryptoscamdb.py, slowmist.py, misttrack.py,
│   │                     walletexplorer.py, store.py
│   ├── content/          pgp_extract.py, context.py, aliases.py, dedup.py,
│   │                     local_object_store.py
│   ├── blockchain/       expand.py, cluster.py, change_heuristic.py,
│   │                     optimal_change.py, voting.py, taproot.py,
│   │                     services.py, taint.py, addr_reuse.py, run_voting.py
│   ├── risk/             engine.py, train_anomaly.py, explain.py
│   ├── watchlist/        precrime.py
│   ├── llm/              brief.py, gemini_backend.py, ollama_backend.py,
│   │                     huggingface_backend.py
│   ├── graph/            onion_graph.py
│   ├── eval/             harness.py
│   └── api/              poc_api.py
├── dashboard/app.py
├── scripts/              collect_seeds.py, ingest_archive.py, expand_graph.py,
│                         run_eval.py, demo_shared_wallet.py, demo_checklist.py
├── schema/001_init.sql
├── setup/windows/        01-07 ..., day1_setup_windows.ps1
├── setup/linux_vm/       day1_setup_vm.sh
├── requirements.txt
├── .env.example
└── README.md
```
