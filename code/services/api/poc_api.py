# services/api/poc_api.py
"""
[Anaconda Prompt] uvicorn services.api.poc_api:app --port 8000
OpenAPI docs at http://localhost:8000/docs

The POC's primary interface is Streamlit, but this thin FastAPI service is
useful for scripting and for the Phase-5 PRE_CRIME monitor to call.
"""
import os
import psycopg2
from fastapi import FastAPI, HTTPException
from services.risk.engine import ThreeLayerRiskEngine

app = FastAPI(title="BTC-Intel POC API", version="0.1.0")
_engine = ThreeLayerRiskEngine()


def _conn():
    return psycopg2.connect(os.environ["POSTGRES_URI"])


@app.get("/poc/wallet/{address}")
def assess(address: str):
    conn = _conn()
    with conn.cursor() as cur:
        cur.execute("SELECT category, confidence, evidence, counterfactual FROM risk_decisions WHERE address=%s", (address,))
        row = cur.fetchone()
    if not row:
        raise HTTPException(404, "Address not yet assessed — run the pipeline first.")
    return {"address": address, "category": row[0], "confidence": row[1],
            "evidence": row[2], "counterfactual": row[3]}


@app.get("/poc/watchlist")
def watchlist():
    conn = _conn()
    with conn.cursor() as cur:
        cur.execute("""SELECT address, onion_domain, page_topic, dw_confidence, first_seen_dw
                       FROM pre_crime_watchlist WHERE monitoring_status='ACTIVE'
                       ORDER BY dw_confidence DESC""")
        rows = cur.fetchall()
    return [{"address": r[0], "onion_domain": r[1], "topic": r[2],
             "dw_confidence": r[3], "first_seen_dw": str(r[4])} for r in rows]
