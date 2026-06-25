# setup/windows/06_resource_budget.md

Re-derived Section 4D for your two actual machines instead of a
16-32 GB college server. Both your laptop (24 GB) and desktop (32 GB) are
single-user Windows machines running everything natively on the host
except the optional Tor/Splash VM.

## Per-component baseline RAM usage (idle/light query load)

| Component | Idle RAM | Under load | Notes |
|---|---|---|---|
| PostgreSQL 16 | ~150-250 MB | 500 MB-1 GB | `shared_buffers` default is conservative; fine as-is for this dataset size |
| Neo4j Community (JVM heap) | ~500 MB-1 GB | 2-4 GB | JVM heap is configurable in `neo4j.conf` (`server.memory.heap.max_size`) — see budget rows below |
| Redis (Docker) | ~10-50 MB | ~100-300 MB | Trivially light for page-hash dedup use |
| VirtualBox VM (if running) | 0 (off) | 4096 MB allocated | Only running during archive/Tor work; shut down otherwise — see `01_virtualbox_vm_setup.md` |
| Streamlit dashboard | ~150 MB | 300-500 MB | Python/Streamlit process itself |
| Python: NetworkX clustering | varies heavily | **see below** | The one item that needs real budgeting — see "Graph size budget" |
| Ollama (qwen2.5:7b, CPU) | 0 (not loaded) | ~5-6 GB while generating | Only when actively generating a brief — unloads after; see `ollama_backend.py` |

## 24 GB laptop budget (the tight one — be honest about what's tight)

| Scenario | Components running | Approx total RAM | Headroom |
|---|---|---|---|
| Normal demo (no VM) | Postgres + Neo4j + Redis + Streamlit + Python (graph in memory) | ~6-9 GB baseline + graph size (below) | OK if graph stays moderate |
| Demo + generating a brief via Ollama | Above + Ollama loaded | +5-6 GB → ~11-15 GB | Still fits in 24 GB, but don't ALSO run the VM at the same time |
| Demo + VM running (Tor/Splash) | Above + 4 GB VM | +4 GB → ~15-19 GB | Getting tight if you're also mid-graph-expansion; shut the VM down before the live demo segment |

**Honest call on the original design's "hold a 1-2M-node graph in memory"
idea:** on 24 GB, holding a multi-million-node NetworkX graph alongside
Postgres+Neo4j+Streamlit is genuinely tight — NetworkX's per-node/edge
Python object overhead means a graph with attributes (satoshi amounts,
txids, timestamps on every edge, as `expand.py` stores) can run into
several GB at the 1-2M-node scale the original design's Section 7.1
estimate implies for a full 50-seed/3-hop expansion.

**What to reduce, concretely, if you hit memory pressure on the 24 GB
machine:**
- Fewer seeds per expansion run: `--limit-seeds 20` instead of 50 (see
  `scripts/expand_graph.py`'s CLI flag — directly reduces graph size
  roughly linearly).
- Fewer hops: 2 hops instead of 3 cuts node count by roughly an
  order of magnitude based on the original design's own hop-by-hop growth
  numbers (Section 14.4: hop 1 → 4,263 nodes, hop 2 → 43,165, hop 3 →
  254,620 — each hop is roughly a 6-10x multiplier in this dataset).
- Sample the graph: keep only edges above a minimum satoshi value when
  building the in-memory NetworkX graph for clustering/taint, dropping
  dust-level edges that rarely change a classification anyway (the risk
  engine's `MIN_FRACTION = 0.05` dust threshold in `services/blockchain/
  taint.py` already discards these from taint propagation — you can apply
  the same filter earlier, at graph-construction time, to save memory too).

For a demo specifically (not a full research run), 20 seeds / 2 hops is
plenty to show every mechanism (taint propagation, clustering, PRE_CRIME)
working correctly, and keeps the whole pipeline comfortably inside 24 GB
with room to also run Ollama or the VM.

## 32 GB desktop budget (comfortable)

Same components, same baseline costs — the extra 8 GB mostly buys you
headroom to run the VM, Ollama, AND a larger 50-seed/3-hop graph
expansion simultaneously without the careful sequencing the laptop needs.
A full 50-seed/3-hop run (~250k nodes per the original design's own
sample numbers) plus Neo4j plus the dashboard plus Ollama generating a
brief should fit with several GB to spare.

## Neo4j heap sizing (apply on whichever machine)

[Inside `%NEO4J_HOME%\conf\neo4j.conf`]
```
server.memory.heap.initial_size=1G
server.memory.heap.max_size=3G      # 24 GB laptop
# server.memory.heap.max_size=4G    # 32 GB desktop — uncomment instead, comment the line above
```
Restart the Neo4j service after changing this file (see
`03_neo4j_setup.md` Step 6 for service restart commands).

## CPU note

Both machines have the same CPU (i7-13620H, same chip in laptop and
desktop form factor here), so there's no CPU-side difference between them
— RAM is the only axis that differs. NetworkX clustering and the
Bayesian risk engine are single-threaded Python; BigQuery does its heavy
lifting server-side (you're not CPU-bound waiting on it); Ollama CPU
inference uses available cores automatically. Nothing here needs explicit
CPU tuning on either machine.
