# services/seeds/store.py
"""
Persist seeds idempotently. ON CONFLICT keeps the HIGHEST-confidence source
if an address appears in more than one list (e.g. both OFAC and a community
report).
"""
import psycopg2
import psycopg2.extras


def store_criminal_seeds(conn, seeds: list[dict]) -> int:
    if not seeds:
        return 0
    rows = [(s["address"], s.get("entity_name"), s["source"], s["confidence"],
             s.get("category", "BLACKLISTED"), s["fetched_at"]) for s in seeds]
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, """
            INSERT INTO seed_addresses
                (address, entity_name, source, confidence, category, fetched_at)
            VALUES %s
            ON CONFLICT (address) DO UPDATE
              SET entity_name = EXCLUDED.entity_name,
                  source      = EXCLUDED.source,
                  category    = EXCLUDED.category,
                  confidence  = GREATEST(seed_addresses.confidence, EXCLUDED.confidence),
                  fetched_at  = EXCLUDED.fetched_at
        """, rows)
    conn.commit()
    return len(rows)


def store_service_labels(conn, labels: list[dict]) -> int:
    if not labels:
        return 0
    rows = [(l["address"], l.get("service_name"), l["label_type"],
             l["confidence"], l["fetched_at"]) for l in labels]
    with conn.cursor() as cur:
        psycopg2.extras.execute_values(cur, """
            INSERT INTO service_labels
                (address, service_name, label_type, confidence, fetched_at)
            VALUES %s
            ON CONFLICT (address) DO UPDATE
              SET service_name = EXCLUDED.service_name,
                  label_type   = EXCLUDED.label_type
        """, rows)
    conn.commit()
    return len(rows)
