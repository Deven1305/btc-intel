# dashboard/app.py
"""
[Anaconda Prompt] streamlit run dashboard/app.py --server.port 8501
Then open http://localhost:8501 in a browser on the same Windows machine.

Streamlit gives a fully browser-accessible analyst UI in ~150 lines of
Python. Change from the original design: the brief-generation button now
calls the pluggable generate_brief() abstraction (Gemini / Ollama /
Hugging Face) instead of a Claude-only call, with a sidebar toggle to pick
the backend live, no code edit needed.
"""
import os
import streamlit as st
import psycopg2
import pandas as pd

from services.risk.engine import ThreeLayerRiskEngine
from services.llm.brief import generate_brief

st.set_page_config(page_title="BTC-Intel POC", page_icon=":link:", layout="wide")
st.title("BTC-Intel — Is This Bitcoin Wallet Criminal?")
st.caption("POC running on a local Windows machine - 100% free data sources")

ICONS = {"BLACKLISTED": "[BLACKLISTED]", "WATCHLISTED": "[WATCHLISTED]",
         "PRE_CRIME_WATCHLIST": "[PRE_CRIME]", "CLEAN": "[CLEAN]"}

# ── sidebar: pluggable LLM backend toggle ───────────────────────────────────
st.sidebar.header("Settings")
backend_choice = st.sidebar.selectbox(
    "Brief-generation backend",
    options=["gemini", "ollama", "huggingface"],
    index=["gemini", "ollama", "huggingface"].index(os.getenv("BTC_LLM_BACKEND", "gemini")),
    help=("gemini: free tier, needs internet + GEMINI_API_KEY. "
          "ollama: fully offline, needs `ollama serve` running locally. "
          "huggingface: free hosted inference, needs internet + HF_TOKEN."),
)
st.sidebar.caption(f"Briefs will be generated using **{backend_choice}**.")


@st.cache_resource
def get_conn():
    return psycopg2.connect(os.environ["POSTGRES_URI"])


def load_signals(conn, address: str) -> dict:
    """Gather all stored signals for an address from the database."""
    sig = {"address": address}
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM seed_addresses WHERE address=%s AND source='OFAC_SDN'", (address,))
        sig["ofac_confirmed"] = cur.fetchone() is not None
        cur.execute("SELECT 1 FROM service_labels WHERE address=%s AND label_type='EXCHANGE'", (address,))
        sig["exchange_verified"] = cur.fetchone() is not None
        cur.execute("""SELECT MAX(confidence) FROM dark_web_records
                       WHERE address=%s AND context_type='PAYMENT'""", (address,))
        row = cur.fetchone()
        sig["dark_web_payment_confidence"] = float(row[0]) if row and row[0] else 0.0
        cur.execute("""SELECT 1 FROM dark_web_records
                       WHERE address=%s AND context_type='VICTIM_REPORT'""", (address,))
        sig["victim_context"] = cur.fetchone() is not None
        cur.execute("SELECT taint_hop1, taint_hop2, taint_hop3 FROM taint_scores WHERE address=%s", (address,))
        t = cur.fetchone()
        if t:
            sig["taint_hop1"], sig["taint_hop2"], sig["taint_hop3"] = float(t[0]), float(t[1]), float(t[2])
        cur.execute("SELECT 1 FROM pre_crime_watchlist WHERE address=%s AND monitoring_status='ACTIVE'", (address,))
        sig["pre_crime_watchlist"] = cur.fetchone() is not None
    return sig


# ── 1. Address lookup ────────────────────────────────────────────────────────
conn = get_conn()
address = st.text_input("Enter a Bitcoin address",
                        placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")

if st.button("Assess Risk", type="primary") and address:
    with st.spinner("Running 3-layer risk engine..."):
        signals = load_signals(conn, address)
        decision = ThreeLayerRiskEngine().classify(address, signals)
        st.session_state["decision"] = decision

if "decision" in st.session_state:
    d = st.session_state["decision"]
    # 2. risk score + category
    c1, c2 = st.columns([1, 1])
    c1.markdown(f"## {ICONS.get(d.category, '[UNKNOWN]')} {d.category}")
    c2.metric("Confidence", f"{d.final_score:.1%}")

    # 3. evidence chain with contribution arrows
    left, right = st.columns(2)
    with left:
        st.subheader("Evidence Chain")
        if d.evidence:
            for ev in d.evidence:
                lr = float(ev.get("lr", 1.0))
                arrow = "UP" if lr > 1 else "DOWN"
                st.write(f"[{arrow}] **{ev['source']}** — {ev.get('detail', '')}")
                st.caption(f"   contribution: {ev.get('contribution', 'n/a')}  (LR {lr})")
        else:
            st.info("No evidence signals triggered.")
        if d.contradictions:
            st.warning("Contradictions: " + "; ".join(
                c if isinstance(c, str) else c.get("reason", "") for c in d.contradictions))

    # 4. counterfactual display
    with right:
        st.subheader("Counterfactual")
        st.info(d.counterfactual)
        st.subheader("Sources Checked")
        st.write(", ".join(d.sources_checked))

    # 6. brief generation button — pluggable backend
    if d.category != "CLEAN" and st.button(f"Generate Investigation Brief ({backend_choice})"):
        with st.spinner(f"{backend_choice} narrating the computed findings..."):
            try:
                st.markdown(generate_brief(d, backend=backend_choice))
            except Exception as e:
                st.error(f"Brief generation failed with backend '{backend_choice}': {e}")

# ── 5. PRE_CRIME live table ──────────────────────────────────────────────────
st.divider()
st.subheader("PRE_CRIME_WATCHLIST — Zero On-Chain History")
st.caption("No commercial system can flag these: they have never transacted. "
           "BTC-Intel flagged them from dark-web payment context alone.")
pc = pd.read_sql("""SELECT address, onion_domain, page_topic, dw_confidence,
                           first_seen_dw, monitoring_status
                    FROM pre_crime_watchlist ORDER BY dw_confidence DESC LIMIT 100""", conn)
st.dataframe(pc, use_container_width=True)

# ── 7. Evaluation metrics ─────────────────────────────────────────────────────
st.divider()
st.subheader("Evaluation vs Baseline")
ev = pd.read_sql("""SELECT dataset, precision, recall, f1, fpr, run_at
                    FROM evaluation_results ORDER BY run_at DESC LIMIT 5""", conn)
st.dataframe(ev, use_container_width=True)
