# setup/windows/08_dataset_downloads.md

Stepwise, click-by-click download/signup instructions for every dataset
and API referenced anywhere in this project. Verified current as of June
2026 — re-check each URL before a demo since signup flows and free-tier
terms can change without notice (two of the sources below — MistTrack and
Chainabuse — already changed their terms since the original architecture
document was written; this guide reflects the corrected, current reality).

---

## 1. OFAC SDN List (free, no signup)

This is the U.S. Treasury's primary sanctions list, parsed by
`services/seeds/ofac.py`.

[Windows browser]
1. Go to https://www.treasury.gov/ofac/downloads/sdn.xml
2. The XML downloads/opens directly — no account, no click-through
   agreement.

You don't actually need to manually download this file at all — `services/
seeds/ofac.py` fetches it directly over HTTPS every time you run
`scripts/collect_seeds.py`. This section is here so you know where the
data comes from and can sanity-check it by eye if you ever want to.

[Windows cmd/PowerShell — optional manual check, not required for the pipeline]
```
curl https://www.treasury.gov/ofac/downloads/sdn.xml -o sdn_check.xml
```

## 2. OFAC mirror — 0xB10C (free, no signup)

A clean, community-maintained re-publication of the same OFAC crypto
addresses, used as the automatic fallback in `services/seeds/
ofac_mirror.py` if the primary XML parse ever fails (e.g. if OFAC changes
its schema).

[Windows browser]
1. Go to https://github.com/0xB10C/ofac-sanctioned-digital-currency-addresses
2. You can browse `sanctioned_addresses_XBT.txt` directly in the repo to
   see the raw list, or just let `services/seeds/ofac_mirror.py` fetch it
   automatically — no download needed.

## 3. UN Consolidated Sanctions List (free, no signup)

[Windows browser]
1. Go to https://scsanctions.un.org/resources/xml/en/consolidated.xml
2. Same as OFAC — this is fetched automatically by `services/seeds/un.py`.
   No account needed.

## 4. Chainabuse (free API key — IMPORTANT: 10 calls/month limit)

**Correction vs. the original architecture doc:** the free Chainabuse key
is limited to **10 calls/month** (each call returns up to 50 reports —
roughly 500 reports/month total), not a generous daily quota. Budget your
calls; don't run this in a loop or a scheduled job.

[Windows browser]
1. Go to https://www.chainabuse.com/ and click **Sign Up** (top right).
2. Create a free account (email + password, or sign in with Google).
3. Verify your email if prompted (check your inbox for a confirmation link).
4. Once logged in, click your profile icon (top right) → **View Profile**.
5. Go to **Settings** → find the **API key** section.
6. Click to generate your API key. Copy it — you won't be able to see the
   full key again later in most setups like this, so store it now.

[Windows cmd/PowerShell — add to .env, not committed to git]
```
notepad .env
```
Add or edit this line:
```
CHAINABUSE_KEY=paste-your-key-here
```

Test it manually before relying on it in the pipeline (this uses 1 of
your 10 monthly calls, so don't run this repeatedly):
```
python services/seeds/chainabuse.py
```

## 5. MistTrack (CORRECTION: no longer free — paid plan or pay-per-call required)

**Important correction vs. the original architecture doc:** as of June
2026, MistTrack's OpenAPI requires either (a) an active **Standard or
Compliance paid subscription plan**, or (b) per-call payment via the
**x402 protocol** using USDC on an EVM chain — there is no longer a free
tier with a daily quota. This module (`services/seeds/misttrack.py`) is
entirely **optional** in this build — `scripts/collect_seeds.py` does not
call it by default, and the pipeline works fully without it.

**If you want to use it anyway** (e.g. you already have or are willing to
get a paid plan):

[Windows browser]
1. Go to https://dashboard.misttrack.io/
2. Log in with your email address and a verification code sent to that
   email (no separate password — MistTrack uses passwordless email-code
   login).
3. From the dashboard, find **Plans/Billing** and purchase the **Standard
   Plan** (this is a paid subscription — check current pricing on the
   dashboard before committing).
4. Once subscribed, go to https://dashboard.misttrack.io/apikeys and
   create an API key.

[Windows cmd/PowerShell — add to .env]
```
MISTTRACK_API_KEY=paste-your-key-here
```

**If you'd rather not pay:** skip this entirely. Nothing else in the
pipeline depends on it.

## 6. CryptoScamDB (free, no signup — public JSON API)

[Windows browser — optional manual check]
1. Go to https://api.cryptoscamdb.org/v1/addresses in a browser — this
   returns raw JSON directly, no login.

`services/seeds/cryptoscamdb.py` fetches this automatically. Nothing to
configure.

## 7. SlowMist blockchain-blacklist (free, GitHub clone or direct fetch)

[Windows browser — optional, to browse the data by eye]
1. Go to https://github.com/slowmist/blockchain-blacklist
2. Click the green **Code** button → **Download ZIP** if you want a local
   copy, or just let `services/seeds/slowmist.py` fetch
   `blacklist.json` directly via HTTPS — no clone needed for the pipeline
   to work.

[Windows cmd/PowerShell — optional, if you prefer a local git clone]
```
git clone https://github.com/slowmist/blockchain-blacklist.git
```

## 8. WalletExplorer (free, no signup — scraped HTML)

No account needed. `services/seeds/walletexplorer.py` fetches service
pages (e.g. `https://www.walletexplorer.com/wallet/Binance.com`) directly.
Nothing to set up.

## 9. Elliptic Dataset (free Kaggle account — detailed steps)

This is the labeled Bitcoin transaction graph used in
`services/eval/harness.py` for baseline comparison (203,769 nodes,
234,355 edges; ~4,500 labeled illicit, ~42,000 labeled licit).

### Step 9a — Create a free Kaggle account

[Windows browser]
1. Go to https://www.kaggle.com/
2. Click **Register** (top right).
3. Sign up with email, or use a Google/Microsoft account — either is fine,
   no payment info required at any point for this.
4. Verify your email if prompted.

### Step 9b — Generate your API token

[Windows browser]
1. Click your profile picture (top right) → **Settings**.
2. Scroll to the **API** section.
3. Click **Create New Token** (older UI: "Create New API Token").
   This downloads a file named `kaggle.json` — usually into your
   `Downloads` folder.

### Step 9c — Install the Kaggle CLI and place the token

[Anaconda Prompt]
```
pip install kaggle
```

[Windows cmd/PowerShell]
The Windows location for the token is different from Mac/Linux — it goes
in your user profile folder, NOT `~/.kaggle`:
```
mkdir %USERPROFILE%\.kaggle
move %USERPROFILE%\Downloads\kaggle.json %USERPROFILE%\.kaggle\kaggle.json
```

Verify it's recognized:
```
kaggle datasets list
```
If you see a list of dataset names print out, the token is working. If
you get an authentication error, double check the file is at exactly
`C:\Users\<your-username>\.kaggle\kaggle.json`.

### Step 9d — Download the Elliptic dataset

[Anaconda Prompt — run from your project root, e.g. C:\btc-intel]
```
kaggle datasets download -d ellipticco/elliptic-data-set
```
This downloads `elliptic-data-set.zip` into your current folder.

[Windows cmd/PowerShell]
```
mkdir data\elliptic
tar -xf elliptic-data-set.zip -C data\elliptic
```
(Windows 10/11 ship `tar` built in, so no separate unzip tool is needed.
If `tar` isn't recognized, right-click the zip in File Explorer → Extract
All → choose `data\elliptic` as the destination instead.)

You should now have three CSVs inside `data\elliptic\`:
`elliptic_txs_features.csv`, `elliptic_txs_classes.csv`,
`elliptic_txs_edgelist.csv`. These map to Elliptic's published schema —
166 features per transaction node, a 3-class label (1 = illicit,
2 = licit, "unknown" = unlabeled), and the directed edge list between
transactions.

## 10. DUTA-10K (academic request — no public download link)

**Set expectations correctly:** there is no URL to click here. DUTA-10K
(Al Nabki, Fidalgo, et al.) is distributed only on direct request from
the paper's original authors, for stated academic research purposes, and
multiple downstream papers note that what's actually distributed is a set
of manually-tagged `.onion` **links/categories**, not full scraped page
content — meaning even with access granted, you would still need to
re-fetch the linked pages yourself to get text to feed into
`scripts/ingest_archive.py`.

[Manual process — no terminal commands apply here]
1. Find the paper: "DUTA-10K: A Parallel Corpus for Deep Learning and
   Cross-Lingual Embeddings" or the related "ToRank" paper by the same
   author group (M.W. Al Nabki, E. Fidalgo, E. Alegre, et al., University
   of León).
2. Locate the current corresponding author's institutional email from
   the paper itself (search the paper title on Google Scholar or the
   publisher's site to find the PDF, which lists author affiliations and
   contact emails).
3. Email them directly: state your academic/research purpose plainly,
   mention your institution (K.J. Somaiya College of Engineering), and
   ask for access to the DUTA-10K dataset for non-commercial research.
4. **Budget real calendar time for this.** There's no published SLA — you
   are depending on another researcher's personal response time, and
   there's no guarantee of a yes. Start this process weeks before any
   demo date if you want any chance of having it in hand in time. Treat
   it as a stretch goal, not something to plan a demo around.
5. If/when you receive access, whatever format they send (likely a
   spreadsheet or text file of tagged URLs, per the note above) — you
   would still need your own legitimate means of retrieving the linked
   page content before it can be fed into `ingest_archive.py`.

## 11. Gwern's Darknet Market Archives (free, but check per-archive terms)

[Windows browser]
1. Go to https://gwern.net/dnm-archive
2. This page is itself the index — read it directly for current links to
   specific archived sub-collections and their individual licensing/usage
   notes (terms can differ by sub-archive, so check the specific one you
   want before treating it as freely redistributable).
3. Download whichever specific files the page links to, in whatever
   format they're offered (this varies by sub-collection — Gwern's own
   page is the authoritative, current source for exact format/size per
   archive, so there isn't a single fixed set of steps that covers every
   sub-collection uniformly).

## 12. BigQuery `crypto_bitcoin` public dataset (free, no card — Sandbox)

Already covered in full in `setup/windows/05_bigquery_costs.md` — short
version:

[Windows browser]
1. Go to https://console.cloud.google.com/
2. Sign in with any Google account.
3. Create a new project (top bar → project dropdown → **New Project**).
   Give it any name (e.g. `btc-intel-poc`).
4. In the search bar, type **BigQuery** and open it. The Sandbox activates
   automatically — no billing account, no card.
5. In the BigQuery console, you can directly query
   `bigquery-public-data.crypto_bitcoin.transactions` (and `.inputs`,
   `.outputs`) without any extra setup — it's a public dataset.

[Windows cmd/PowerShell — for the Python client used in `services/
blockchain/expand.py`]
1. In the Cloud Console, go to **IAM & Admin** → **Service Accounts**.
2. Create a service account, grant it the **BigQuery User** role.
3. Create a JSON key for it (Service Account → Keys → Add Key → Create
   New Key → JSON) — this downloads a `.json` credentials file.
4. Save it somewhere stable, e.g. `C:\btc-intel\gcp-service-account.json`.
5. In `.env`:
```
GOOGLE_APPLICATION_CREDENTIALS=C:\btc-intel\gcp-service-account.json
BIGQUERY_PROJECT_ID=btc-intel-poc
```

---

## Summary table

| Source | Cost | Signup needed | Notes |
|---|---|---|---|
| OFAC SDN | Free | No | Auto-fetched |
| OFAC mirror | Free | No | Fallback only |
| UN Sanctions | Free | No | Auto-fetched |
| Chainabuse | Free | Yes | 10 calls/month limit |
| MistTrack | Paid (or pay-per-call) | Yes | Optional, skip if you don't want to pay |
| CryptoScamDB | Free | No | Auto-fetched |
| SlowMist | Free | No | Auto-fetched |
| WalletExplorer | Free | No | Scraped, no account |
| Elliptic (Kaggle) | Free | Yes (Kaggle account) | Standard Kaggle API flow |
| DUTA-10K | Free, but request-based | Yes (email request) | No guarantee, plan for weeks of lead time |
| Gwern's archive | Free | No | Check per-sub-archive terms |
| BigQuery crypto_bitcoin | Free (Sandbox) | Yes (Google account) | No card needed |
