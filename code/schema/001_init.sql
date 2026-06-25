-- schema/001_init.sql  — BTC-Intel POC schema (PostgreSQL 16)

-- ── Seeds: confirmed criminal addresses from authoritative sources ──────────
CREATE TABLE seed_addresses (
    address       TEXT PRIMARY KEY,
    entity_name   TEXT,
    source        TEXT NOT NULL,          -- OFAC_SDN | UN_SANCTIONS | CHAINABUSE | ...
    confidence    FLOAT NOT NULL,         -- 1.0 OFAC/UN, 0.6 community
    category      TEXT DEFAULT 'BLACKLISTED',
    fetched_at    TIMESTAMPTZ DEFAULT NOW(),
    expires_at    TIMESTAMPTZ             -- community reports may expire
);
CREATE INDEX idx_seed_source ON seed_addresses(source);

-- ── Service labels: exchanges/pools used as TAINT BARRIERS (not criminals) ──
CREATE TABLE service_labels (
    address       TEXT PRIMARY KEY,
    service_name  TEXT,
    label_type    TEXT NOT NULL,          -- EXCHANGE | MINING_POOL | MIXER
    confidence    FLOAT NOT NULL,
    fetched_at    TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_service_type ON service_labels(label_type);

-- ── Dark web records: everything extracted from already-acquired pages ─────
-- (populated by scripts/ingest_archive.py from local/licensed archive HTML,
--  NOT by a live crawler — see README "Dark web data" section)
CREATE TABLE dark_web_records (
    id               SERIAL PRIMARY KEY,
    address          TEXT NOT NULL,
    address_type     TEXT,                -- P2PKH | P2SH | BECH32 | BECH32M
    context_type     TEXT,                -- PAYMENT | VICTIM_REPORT | AMBIGUOUS
    context_window   TEXT,                -- ~500 chars surrounding the address
    confidence       FLOAT,
    page_topic       TEXT,                -- DRUG | WEAPON | FRAUD | UNKNOWN
    onion_domain     TEXT,
    page_url         TEXT,
    archive_key      TEXT,                -- MinIO key or local archive filename
    pgp_fingerprints TEXT[],
    aliases          TEXT[],
    first_seen       TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_dw_address ON dark_web_records(address);
CREATE INDEX idx_dw_domain  ON dark_web_records(onion_domain);
CREATE INDEX idx_dw_context ON dark_web_records(context_type);

-- ── PRE_CRIME watchlist: DW addresses with zero on-chain history ────────────
CREATE TABLE pre_crime_watchlist (
    address             TEXT PRIMARY KEY,
    onion_domain        TEXT NOT NULL,
    page_url            TEXT NOT NULL,
    page_topic          TEXT,
    dw_confidence       FLOAT NOT NULL,
    pgp_fingerprints    TEXT[],
    first_seen_dw       TIMESTAMPTZ NOT NULL,
    monitoring_status   TEXT DEFAULT 'ACTIVE',   -- ACTIVE | TRIGGERED | EXPIRED
    first_tx_hash       TEXT,
    first_tx_at         TIMESTAMPTZ,
    dw_to_first_tx_days INTEGER
);
CREATE INDEX idx_precrime_status ON pre_crime_watchlist(monitoring_status);

-- ── Taint scores per address (output of Phase 3) ────────────────────────────
CREATE TABLE taint_scores (
    address      TEXT PRIMARY KEY,
    taint_hop1   FLOAT DEFAULT 0,
    taint_hop2   FLOAT DEFAULT 0,
    taint_hop3   FLOAT DEFAULT 0,
    method       TEXT,                    -- AMOUNT_WEIGHTED | LABEL_PROP | PPR | ENSEMBLE
    computed_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── Address clusters (CIO + multi-heuristic voting results) ─────────────────
CREATE TABLE address_clusters (
    address       TEXT PRIMARY KEY,
    cluster_root  TEXT NOT NULL,
    confidence    FLOAT,
    merge_reason  TEXT,                   -- CIO | SCRIPT_CHANGE | OPTIMAL_CHANGE | ADDR_REUSE
    cluster_status TEXT DEFAULT 'RESOLVED' -- RESOLVED | CLUSTERING_UNRESOLVED (Taproot)
);
CREATE INDEX idx_cluster_root ON address_clusters(cluster_root);

-- ── Risk decisions: final output for each assessed address ──────────────────
CREATE TABLE risk_decisions (
    address        TEXT PRIMARY KEY,
    category       TEXT NOT NULL,         -- BLACKLISTED | WATCHLISTED | PRE_CRIME_WATCHLIST | CLEAN
    confidence     FLOAT NOT NULL,
    evidence       JSONB,                 -- full evidence chain
    counterfactual TEXT,
    contradictions JSONB,
    brief          TEXT,                  -- LLM-generated narrative (Gemini/Ollama/HF)
    assessed_at    TIMESTAMPTZ DEFAULT NOW(),
    last_updated   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_risk_category ON risk_decisions(category);

-- ── Crawl queue: kept for schema completeness / future use ──────────────────
-- NOTE: this POC does not run a live crawler against it (see README). The
-- table is retained because dark_web_records.archive_key references the
-- same "page" concept, and a future production system (File B) may resume
-- using it for real queueing.
CREATE TABLE crawl_queue (
    id           SERIAL PRIMARY KEY,
    url          TEXT UNIQUE,
    onion_domain TEXT,
    priority     INTEGER DEFAULT 5,       -- higher = sooner
    depth        INTEGER DEFAULT 0,
    status       TEXT DEFAULT 'PENDING',  -- PENDING | DONE | DEAD
    last_attempt TIMESTAMPTZ,
    attempts     INTEGER DEFAULT 0
);
CREATE INDEX idx_queue_status ON crawl_queue(status, priority DESC);

-- ── Reassessment queue: addresses to re-evaluate after a new seed arrives ────
CREATE TABLE reassessment_queue (
    address    TEXT PRIMARY KEY,
    reason     TEXT,
    queued_at  TIMESTAMPTZ DEFAULT NOW(),
    processed  BOOLEAN DEFAULT FALSE
);

-- ── Evaluation results: precision/recall vs baseline ────────────────────────
CREATE TABLE evaluation_results (
    run_id     TEXT,
    run_at     TIMESTAMPTZ DEFAULT NOW(),
    dataset    TEXT,
    precision  FLOAT, recall FLOAT, f1 FLOAT, fpr FLOAT,
    tp_count   INTEGER, fp_count INTEGER, tn_count INTEGER, fn_count INTEGER,
    notes      TEXT
);

-- ── Audit log: IMMUTABLE (no UPDATE/DELETE for the app role) ────────────────
CREATE TABLE audit_log (
    id          BIGSERIAL PRIMARY KEY,
    action      TEXT NOT NULL,
    address     TEXT,
    actor       TEXT DEFAULT 'SYSTEM',
    result_hash TEXT,                     -- SHA-256 of the decision (tamper detection)
    details     JSONB,
    timestamp   TIMESTAMPTZ DEFAULT NOW()
);
REVOKE UPDATE, DELETE ON audit_log FROM btcintel;   -- immutable by design

-- ── Graph cache: NEW TABLE (not in the original schema) ─────────────────────
-- Gap I found: the original GraphExpander re-queried BigQuery on every run,
-- even for an identical hop expansion already paid for in free-tier quota.
-- This table lets services/blockchain/expand.py cache a hop-expansion result
-- keyed by a hash of (sorted seeds, max_hops), so re-running the dashboard or
-- re-demoing the same seeds never re-burns BigQuery's 1 TiB/month allowance.
CREATE TABLE graph_cache (
    cache_key   TEXT PRIMARY KEY,
    seeds       TEXT[] NOT NULL,
    max_hops    INTEGER NOT NULL,
    graph_json  JSONB NOT NULL,
    cached_at   TIMESTAMPTZ DEFAULT NOW()
);
