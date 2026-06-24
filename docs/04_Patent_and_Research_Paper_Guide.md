# BTC-Intel: Patent Filing & Research Paper Publication Guide
## Complete Step-by-Step Strategy for IP Protection and Academic Recognition

> **Document Purpose:** This document is the complete guide for protecting BTC-Intel's intellectual property through patents and establishing academic credibility through peer-reviewed publication. It covers what to file, when to file, how to structure claims, which venues to target, and what every section of your paper/patent must contain — written specifically for BTC-Intel's novel contributions as identified in the research gap analysis.

---

## Table of Contents

1. [Strategic Overview: Patent vs. Paper vs. Both](#1-strategic-overview)
2. [What You Can Patent (Claim-Ready Analysis)](#2-what-you-can-patent)
3. [What You Cannot Patent (Prior Art Blockers)](#3-what-you-cannot-patent)
4. [Patent Filing: Step-by-Step Process](#4-patent-filing-step-by-step)
5. [Patent Claims: Drafted Templates for BTC-Intel](#5-patent-claims-drafted-templates)
6. [Prior Art Search: Where to Look and What to Look For](#6-prior-art-search)
7. [Research Paper: Target Venues and Selection Strategy](#7-research-paper-venues)
8. [Research Paper: Complete Structure and Section-by-Section Guide](#8-research-paper-structure)
9. [Abstract Templates for BTC-Intel](#9-abstract-templates)
10. [Evidence and Evaluation: What Numbers You Must Have](#10-evidence-and-evaluation)
11. [Avoiding Common Rejection Reasons](#11-avoiding-common-rejection-reasons)
12. [Timeline: When to File Patent vs. When to Submit Paper](#12-timeline)
13. [Budget and Resource Planning](#13-budget-and-resource-planning)
14. [The arXiv Preprint Strategy: Establishing Priority Without Delay](#14-arxiv-preprint-strategy)
15. [Checklist: Patent Ready / Paper Ready](#15-checklists)

---

## 1. Strategic Overview: Patent vs. Paper vs. Both

This is the single most important strategic decision and it must be made before you write one word of either document. Getting the order wrong can permanently destroy your ability to patent.

### The Conflict Between Patents and Papers

A published research paper is **prior art** against your own patent. In most patent jurisdictions:
- **USA:** You have a 12-month grace period after your own publication to file a patent (35 U.S.C. § 102(b)(1)(A))
- **Europe (EPO):** There is NO grace period. Publishing your paper before filing your European patent application destroys novelty. Any public disclosure, including a conference talk, an arXiv preprint, or a university seminar presentation, bars European patent protection permanently.
- **India, China, Japan:** No grace period. Same as Europe.

**The correct sequence for BTC-Intel (maximising both patent and paper value):**

```
Step 1:  File provisional patent application (USA) — TODAY
Step 2:  File arXiv preprint — within 1 week of provisional filing
Step 3:  Submit paper to conference — within 2 weeks
Step 4:  File full non-provisional patent (USA) — within 12 months of provisional
Step 5:  File PCT application (international) — within 12 months of provisional
Step 6:  Paper published at conference — typically 4–8 months after submission
```

**Why provisional patent first:**
A US provisional patent application costs $320 (micro-entity, which you qualify for as an individual/university researcher). It establishes your priority date — the legal filing date used to determine who invented something first. It does not get examined and does not become public. You then have 12 months to file the full non-provisional application while your priority date is already secured.

**Why arXiv immediately after provisional:**
arXiv establishes a public timestamp for your work. If another researcher independently publishes similar work after your arXiv date but before your conference paper appears, your arXiv date is evidence of prior art against their work. This protects your academic priority even while the patent is pending.

### When You Should File ONLY a Paper (Not a Patent)

If any of the following are true, skip the patent:
- The core technique relies on publicly available datasets (Elliptic, OFAC XML) and standard algorithms (Random Forest, PageRank) — these cannot be patented
- Your primary audience is academic and you want maximum impact/citations (patents don't get cited in papers the same way)
- You lack funds for full patent prosecution ($5,000–$15,000 for professional attorneys)
- Your institution has a technology transfer office that will claim ownership of any patent filed using their resources — negotiate first

### When You Should File ONLY a Patent (Not a Paper)

If any of the following are true, skip the academic paper initially:
- You are building a commercial product and don't want to reveal your full methodology to competitors
- The techniques have immediate commercial value (exchange integrations, compliance tools) that you want to monetise before competitors can copy them
- The system has law enforcement deployment that requires confidentiality

### BTC-Intel Recommendation: File Both, In This Order

BTC-Intel has genuine novel contributions (PRE_CRIME_WATCHLIST mechanism, shared-wallet onion graph edge, provenance-aware Bayesian fusion) that are both patentable AND publishable. The correct strategy is to file the provisional patent application this week, then proceed with the academic paper. This secures IP rights while building academic credibility simultaneously.

---

## 2. What You Can Patent (Claim-Ready Analysis)

Based on the research gap analysis (Document 03), the following components of BTC-Intel have sufficient novelty and non-obviousness to support patent claims:

---

### Patentable Claim 1 — PRE_CRIME_WATCHLIST Mechanism ⭐ PRIORITY

**Novelty basis:**
No existing patent or published paper claims pre-transaction risk scoring based on dark web payment context. Chainalysis US10977655B2 explicitly requires an existing transaction before taint can be applied. This creates a clear gap in the prior art.

**Non-obviousness argument:**
The combination of: (a) classifying dark web page content as "payment context," (b) extracting addresses from payment-context pages, and (c) assigning a pre-transaction risk score with monitored status is not an obvious extension of existing systems. The non-obvious element is the insight that an address listed in a payment context carries risk before any transaction — existing systems treat all zero-history addresses as equivalently risk-neutral.

**Risk factors:**
- TRM Labs, Chainalysis, and Elliptic have active patent filing programs. A comprehensive search of USPTO PAIR for their recently filed (but not yet published) applications is essential before asserting this is clear
- Patent applications are confidential for 18 months after filing — competitors may have pending applications you cannot see yet

---

### Patentable Claim 2 — Shared-Wallet Edge Type in Onion Graphs ⭐ HIGH VALUE

**Novelty basis:**
Biryukov 2014 and Spitters 2014 build onion graphs using hyperlinks and topic similarity. The specific edge type "two onion domains share a payment-context Bitcoin address" does not appear in any prior art. The combination of a financial instrument (Bitcoin address) as an edge weight between two network infrastructure nodes (onion domains) is novel in both the blockchain analytics literature and the dark web measurement literature.

**Non-obviousness argument:**
An expert in blockchain analytics might combine Bitcoin address clustering with dark web OSINT, but would not obviously arrive at representing the shared address as an edge in a dark web infrastructure graph — because this requires expertise in both onion graph construction (a network measurement domain) and blockchain address clustering (a cryptography/forensics domain). Cross-domain combinations are typically non-obvious.

---

### Patentable Claim 3 — Provenance-Aware Bayesian Evidence Fusion ⭐ CLEAN

**Novelty basis:**
The specific mechanism of tracking a "provenance chain" for each evidence signal and deduplicating based on the chain to prevent circular double-counting in a blockchain risk engine is not in any published patent or paper. The circular dependency problem (OFAC → Chainalysis → OFAC) is known but the algorithmic solution (provenance chain tracking in a Bayesian update engine) is not.

**Non-obviousness argument:**
Bayesian fusion for risk scoring is known. Provenance tracking is known (in citation systems, bibliography graphs). The combination — applying provenance tracking to prevent circular evidence in a Bayesian risk scoring engine — is non-obvious because it requires recognising that evidence sources in commercial blockchain intelligence have hidden dependency structures that are not documented publicly.

---

### Patentable Claim 4 — Amount Correlation Validation (Weaker, but possible)

**Novelty basis:**
Cross-referencing the price from a dark web listing with the first on-chain transaction amount to the same address as corroborating evidence for a completed criminal transaction is not in any prior art.

**Risk:** This may be considered obvious to a person skilled in the art once they have the listing price and the on-chain data. The combination is novel but the non-obviousness argument is weaker than Claims 1–3. File as a dependent claim of Claim 1 rather than an independent claim.

---

## 3. What You Cannot Patent (Prior Art Blockers)

Do not waste time or money attempting to patent these elements. They are blocked by clear prior art:

| Element | Prior Art Blocker | Citation |
|---------|------------------|----------|
| CIO clustering | Meiklejohn et al. 2013 (public disclosure) | [Meiklejohn2013] |
| Taint propagation | Chainalysis US10977655B2 (issued patent) | [Chainalysis_Patent] |
| Change address heuristic | Meiklejohn et al. 2013 | [Meiklejohn2013] |
| Dark web crawler for BTC addresses | Ron & Shamir 2013, multiple publications | [Ron2013] |
| Graph-based risk propagation | Nerino 2021 and numerous others | [Nerino2021] |
| Behavioral feature extraction on blockchain | Peled 2021, Weber 2019 | [Peled2021, Weber2019] |
| Isolation Forest anomaly detection | Public algorithm (Liu et al. 2008) | [Liu2008] |
| Random Forest classification | Public algorithm | N/A |
| SHAP explainability | Lundberg & Lee 2017 | [Lundberg2017] |
| Risk score for blockchain address | Too broad — Chainalysis patent covers | [Chainalysis_Patent] |

**Critical warning:** Do not draft claims that read on (overlap with) Chainalysis US10977655B2. If your claim could describe the Chainalysis taint propagation system, it will be rejected as anticipated by prior art. Your claims must be specifically targeted at the off-chain/pre-transaction elements that Chainalysis's patent explicitly does not cover.

---

## 4. Patent Filing: Step-by-Step Process

### Phase 1: Before Filing (1–2 Weeks)

**Step 1.1 — Document the Invention (Inventor's Notebook)**

Create a dated, witnessed document that describes the invention in detail. This is your legal evidence of the invention date. It must include:
- Clear description of what the invention does (not how it works — that comes in the application)
- Date of conception (when you first had the idea)
- Date of reduction to practice (when it first worked — your POC demonstration date)
- Signature of two witnesses who understand the description and sign with date

Use a bound notebook with numbered pages, not loose paper. PDF with SHA-256 hash and timestamp via a notary or trusted timestamping service (e.g., DigiStamp) also works for digital records.

**Step 1.2 — Prior Art Search**

Search these five sources minimum:

```
1. USPTO Patent Full-Text Database (patents.google.com)
   Search queries:
   - "cryptocurrency" AND "dark web" AND "risk score"
   - "blockchain" AND "pre-transaction" AND "intelligence"
   - "bitcoin" AND "onion" AND "address clustering"
   - "cryptocurrency address" AND "Bayesian" AND "evidence"
   - Assignee: Chainalysis Inc.
   - Assignee: TRM Labs Inc.
   - Assignee: Elliptic Enterprises Ltd.

2. EPO Espacenet (worldwide.espacenet.com)
   Same search queries as USPTO

3. WIPO PATENTSCOPE (patentscope.wipo.int)
   Search for PCT applications — filed 18 months before publication,
   so recent applications won't appear yet

4. Google Scholar
   Search for academic papers that describe similar systems
   (these constitute non-patent prior art)

5. arXiv cs.CR and cs.SI categories
   Search recent preprints (blockchain + dark web + risk scoring)
```

**What you're looking for:**
Any document that, alone, describes ALL elements of your claim. A single document doesn't need to describe everything perfectly — patent examiners will combine multiple references under obviousness — but a single clear document describing your PRE_CRIME_WATCHLIST mechanism would be a fatal prior art hit.

**Step 1.3 — Decide: Self-File or Attorney?**

| Option | Cost | Quality | Recommended For |
|--------|------|---------|----------------|
| Pro se (self-file) | $320 provisional + $800 non-provisional (micro entity) | Lower — claims may be weaker | If you are certain of strong novelty and have budget constraints |
| Patent agent (no law degree) | $3,000–$6,000 total | Good | Recommended for most technical inventors |
| Patent attorney (law degree + technical background) | $8,000–$15,000 total | Highest | If you expect licensing income or litigation |

**Recommendation for BTC-Intel:** Use a patent agent with blockchain/software background. The cost is manageable (~$4,000) and the claim quality improvement over pro se is significant. Search for agents registered with the USPTO who have a CS background: www.usptoagents.com

---

### Phase 2: Provisional Patent Application (Week 2)

**Form to file:** USPTO Form PTO/SB/16 (or file via EFS-Web / Patent Center)

**What a provisional must contain:**

A provisional application establishes your priority date but is never examined. It becomes your specification for the full application. Write it as if it IS the full application — because it effectively is.

**Required sections in your provisional:**

```
1. Title
   Keep short and non-revealing:
   "System and Method for Pre-Transaction Risk Assessment of
    Cryptocurrency Addresses Using Off-Chain Contextual Intelligence"

2. Field of the Invention
   "This invention relates to cryptocurrency transaction monitoring,
    and more particularly to systems that assign risk classifications
    to cryptocurrency addresses prior to their participation in
    on-chain transactions using contextual intelligence derived from
    off-chain sources."

3. Background
   - What problem exists (criminals using cryptocurrency; existing systems
     only flag AFTER suspicious transactions)
   - What prior solutions exist and why they are insufficient
   - Cite Chainalysis patent and note it requires existing transactions
   - DO NOT describe your invention in the Background section

4. Brief Summary of the Invention
   One paragraph, very high level, covering all independent claims

5. Detailed Description of Preferred Embodiments
   This is the bulk of the document. Describe EVERY component in detail.
   Include code fragments, flowcharts, system diagrams.
   The more detail here, the stronger your later non-provisional.
   IMPORTANT: Describe alternative embodiments too
   ("In an alternative embodiment, the Bayesian fusion engine may...")
   This broadens your protection.

6. Claims (optional in provisional, but include them anyway)
   Draft your claims now. They can be refined in the non-provisional.

7. Abstract (250 words maximum)

8. Drawings
   Include system architecture diagrams, flowcharts for each algorithm,
   database schema. Label every element with a reference numeral.
   Drawings must be USPTO-compliant (black ink, specific line weights).
```

**Filing procedure:**
- Go to: https://www.uspto.gov/patents/apply
- Create an account on Patent Center
- File under "Provisional Patent Application"
- Pay $320 (micro-entity rate — you qualify if no prior patents and income < 3× US median)
- Keep the Application Number (looks like 63/XXX,XXX) — this is your priority date reference

---

### Phase 3: Full Non-Provisional Application (Within 12 Months)

The non-provisional converts your provisional into an examined application. The claims in the non-provisional are what get examined and ultimately define the scope of your patent.

**Key structural difference from provisional:**
The non-provisional's claims must be precisely drafted. Independent claims should be as broad as possible while being novel over the prior art. Dependent claims add specificity.

**Claim structure for non-provisional:**
```
Independent Claim 1 (broadest — covers the core mechanism)
    Dependent Claim 2 (adds one element: PGP fingerprint extraction)
    Dependent Claim 3 (adds another: amount correlation)
    Dependent Claim 4 (adds another: onion graph edge type)

Independent Claim 5 (covers a computer-readable medium variant)
Independent Claim 6 (covers a system claim — apparatus, not method)
```

---

### Phase 4: PCT International Application (Within 12 Months)

If you want international protection (Europe, India, China, Japan, Singapore — key jurisdictions for blockchain compliance companies), file a Patent Cooperation Treaty (PCT) application within 12 months of your provisional.

**Cost:** ~$3,000–$5,000 in USPTO fees alone (before attorney fees and national phase fees)

**Why PCT:**
One application, filed with the USPTO as receiving office, establishes priority in 157 countries simultaneously. You then have 30 months from priority date to enter individual national phases (paying each country's fees). This gives you time to evaluate which markets are worth pursuing before committing to full national phase costs.

**Key countries for blockchain analytics companies:**
- USA (USPTO) — primary market
- Europe (EPO, single application covers 38 countries) — major compliance market
- United Kingdom (UKIPO) — post-Brexit, separate from EPO
- Singapore (IPOS) — APAC blockchain hub
- Japan (JPO) — strong patent enforcement
- India (IPO) — growing blockchain regulation

---

## 5. Patent Claims: Drafted Templates for BTC-Intel

These are draft claim frameworks. Have a patent attorney or agent refine them before filing.

### Independent Claim 1 — PRE_CRIME_WATCHLIST Method

```
1. A computer-implemented method for assigning a pre-transaction risk
   classification to a cryptocurrency address, the method comprising:

   (a) receiving, by one or more processors, a document retrieved from
       a Tor hidden service network, the document comprising text content
       and one or more cryptocurrency addresses;

   (b) classifying, by a natural language processor, the text content
       surrounding each cryptocurrency address as one of: a payment
       context, a victim report context, or an ambiguous context,
       based on a set of contextual signal keywords associated with
       payment transactions;

   (c) for each cryptocurrency address classified as occurring in a
       payment context:
       (i)  querying a blockchain transaction database to determine
            whether the cryptocurrency address has any associated
            on-chain transaction history;
       (ii) when the cryptocurrency address has no on-chain transaction
            history, assigning the cryptocurrency address a
            PRE_CRIME_WATCHLIST classification and a confidence score
            derived from the payment context classification;

   (d) storing the PRE_CRIME_WATCHLIST classification and confidence
       score in a monitoring database;

   (e) monitoring the blockchain transaction database for a first
       on-chain transaction associated with the cryptocurrency address;
       and

   (f) upon detecting the first on-chain transaction, updating the
       risk classification of the cryptocurrency address based on the
       combination of the stored payment context evidence and the
       on-chain transaction evidence.
```

### Dependent Claims on Claim 1

```
2. The method of claim 1, wherein classifying the text content further
   comprises extracting one or more PGP public key fingerprints from
   the document and storing an association between the PGP fingerprint
   and the cryptocurrency address as corroborating evidence for the
   payment context classification.

3. The method of claim 1, wherein classifying the text content further
   comprises extracting a price amount from the document and, upon
   detecting the first on-chain transaction, comparing the first
   on-chain transaction amount to the extracted price amount to produce
   an amount correlation confidence score.

4. The method of claim 1, further comprising:
   constructing a directed graph of Tor hidden service domains in which
   each node represents a Tor hidden service domain and each edge between
   two nodes represents the co-appearance of at least one cryptocurrency
   address in payment-context documents on both domains, with edge weight
   proportional to the number of shared cryptocurrency addresses.

5. The method of claim 4, wherein the directed graph is used to identify
   clusters of Tor hidden service domains operated by a common criminal
   entity based on shared payment infrastructure.

6. The method of claim 1, wherein the confidence score is computed by
   a Bayesian inference engine that updates a prior probability of
   criminal activity based on one or more likelihood ratios assigned to
   distinct categories of evidence signals, the Bayesian inference engine
   further comprising a provenance tracking module that maintains a
   directed acyclic provenance graph for each evidence signal and
   excludes from the Bayesian update any evidence signal whose provenance
   graph contains a cycle with an already-applied evidence signal.
```

### Independent Claim 7 — Provenance-Aware Bayesian Fusion Method

```
7. A computer-implemented method for combining cryptocurrency address
   risk evidence from a plurality of sources, the method comprising:

   (a) receiving a plurality of risk evidence signals for a
       cryptocurrency address from a plurality of distinct sources,
       each evidence signal associated with an evidence type and a
       source identifier;

   (b) for each evidence signal, determining a provenance chain
       comprising one or more source identifiers that contributed
       to the generation of the evidence signal by the associated
       source;

   (c) maintaining an active evidence set comprising the source
       identifiers of evidence signals already applied to a
       Bayesian risk score computation;

   (d) for each evidence signal, determining whether any source
       identifier in the provenance chain of the evidence signal
       is present in the active evidence set;

   (e) when a source identifier in the provenance chain is present
       in the active evidence set, excluding the evidence signal
       from the Bayesian risk score computation to prevent
       double-counting of correlated evidence; and

   (f) computing a final risk score for the cryptocurrency address
       by applying only the non-excluded evidence signals as
       sequential Bayesian updates to a prior probability.
```

### Independent Claim 8 — System Claim (Apparatus)

```
8. A system for cryptocurrency address threat intelligence, the system
   comprising:

   one or more processors; and

   one or more non-transitory computer-readable media storing
   instructions that, when executed by the one or more processors,
   cause the system to perform operations comprising:

   [repeat method steps from Claims 1 and 7 in system language]
```

---

## 6. Prior Art Search: Where to Look and What to Look For

### Searching for Patent Prior Art

**Query templates for USPTO/Google Patents:**

```
Query 1 (PRE_CRIME_WATCHLIST):
"cryptocurrency" AND "pre-transaction" AND "risk"
"blockchain" AND "dark web" AND "risk score"
"bitcoin" AND "zero transaction history" AND "classification"
"tor" AND "hidden service" AND "cryptocurrency address" AND "risk"

Query 2 (Onion Graph):
"tor hidden service" AND "cryptocurrency" AND "graph"
"onion network" AND "bitcoin" AND "clustering"
"dark web" AND "payment address" AND "network graph"

Query 3 (Bayesian Fusion):
"cryptocurrency" AND "Bayesian" AND "evidence fusion"
"blockchain" AND "provenance" AND "double counting"
"bitcoin" AND "likelihood ratio" AND "risk scoring"

Assignee searches (check these companies' portfolios):
Assignee: "Chainalysis"     — 15+ active patents
Assignee: "TRM Labs"        — 8+ filed, some not yet public
Assignee: "Elliptic"        — 5+ filed
Assignee: "CipherTrace"     — acquired by Mastercard; check both
Assignee: "Blockchain.com"  — smaller portfolio
```

**How to read a patent claim for blocking prior art:**

Read only the independent claims first. An independent claim blocks you only if it covers ALL elements of your claim. Missing even one element means the claim doesn't cover you (but watch for obviousness — combining two references).

For Chainalysis US10977655B2, read Claim 1 carefully:
- It requires: "generating a risk score based at least in part on a taint value propagated from a previously classified cryptocurrency address"
- Your Claim 1 does NOT involve taint propagation — it acts on addresses with NO prior classification
- Therefore, Chainalysis Claim 1 does NOT block your Claim 1 ✓

### Searching for Non-Patent Prior Art

**arXiv searches:**
```
cs.CR (Cryptography and Security):
site:arxiv.org "bitcoin" "dark web" "risk" after:2020
site:arxiv.org "blockchain" "pre-transaction" "intelligence"
site:arxiv.org "onion" "bitcoin" "graph" "clustering"

cs.SI (Social and Information Networks):
site:arxiv.org "tor hidden service" "bitcoin" "clustering"
```

**ACM Digital Library and IEEE Xplore:**
Search: "bitcoin" AND "dark web" AND ("risk" OR "intelligence")
Filter: 2020–present

**SSRN (legal/economics papers):**
Search: "cryptocurrency intelligence" "pre-crime" "blockchain monitoring"

---

## 7. Research Paper: Target Venues and Selection Strategy

### Primary Target Venues (by prestige and fit)

| Venue | Prestige | Deadline Pattern | Acceptance Rate | Why BTC-Intel Fits |
|-------|----------|-----------------|-----------------|-------------------|
| **Financial Cryptography (FC)** | A | October (for February) | ~20% | Primary blockchain security venue; routinely publishes blockchain analytics |
| **IEEE S&P (Oakland)** | A* | November (for May) | ~15% | Highest prestige; security systems; strong precedent for blockchain analytics papers |
| **USENIX Security** | A* | Rotating deadlines | ~16% | Systems security; Kappos 2018 (Paper 1.4) published here |
| **ACM CCS** | A* | February (for November) | ~18% | Strong cryptography and security track |
| **NDSS** | A | June (for February) | ~17% | Network and distributed system security; dark web measurement papers accepted |
| **ACM IMC** | A | May (for October) | ~25% | Internet Measurement Conference; Meiklejohn 2013 published here — strong precedent |
| **ACM WebSci** | B | January (for April) | ~30% | Dark web measurement; Christin 2013 published here |
| **ARES** | B | March (for August) | ~35% | Applied security; Nerino 2021 published here — good fit for BTC-Intel system paper |

### Selection Strategy for BTC-Intel

**First submission target: Financial Cryptography (FC)**
FC has the best fit for BTC-Intel: it publishes blockchain analytics papers, privacy/anonymity papers, and financial crime papers. The 20% acceptance rate is challenging but achievable with strong experimental results.

**If FC rejects:** Submit to NDSS (strong dark web measurement track) or ACM IMC (measurement focus matches your dark web crawling methodology).

**If you want faster publication:** Submit to ARES (35% acceptance, shorter review cycle). Less prestigious but still citable.

**For the research novelty angle (not the system angle):** If you focus on one contribution only (e.g., just the PRE_CRIME_WATCHLIST mechanism with rigorous evaluation), IEEE S&P or USENIX Security are realistic targets. They prefer focused technical contributions over large system papers.

**Workshop venues (lower bar, faster feedback):**
- IEEE S&P Workshop on Deep Learning Security
- USENIX Workshop on Cyber Security Experimentation and Test (CSET)
- FC Workshop on Blockchain Technologies (WTSC)

**Workshop strategy:** Submit a 6-page workshop paper describing the PRE_CRIME_WATCHLIST mechanism with preliminary results. This establishes a citation anchor and gets reviewer feedback before your full conference submission.

---

## 8. Research Paper: Complete Structure and Section-by-Section Guide

### Paper Length and Format

Most security and cryptography venues accept 12–16 pages (double column, 10pt font, ACM or IEEE template). Check the specific call for papers for your target venue.

---

### Section 1: Introduction (2 pages)

**Paragraph 1 — The Problem (hook the reviewer):**
Open with a concrete, specific, shocking statistic about cryptocurrency-based crime. Then state that existing monitoring systems have a fundamental blind spot: they can only flag addresses AFTER suspicious activity, leaving a window during which funds are being accumulated without oversight.

Example opening (do NOT use this verbatim — write your own):
*"In 2023, cryptocurrency-related crime reached [X] billion dollars globally [cite Chainalysis annual report]. Despite sophisticated blockchain analytics tools deployed by financial institutions and law enforcement agencies, existing monitoring systems share a fundamental limitation: they require an on-chain transaction history before any risk assessment is possible. An address receiving its first payment from a criminal enterprise appears identical to a brand-new legitimate address to every existing commercial and academic system."*

**Paragraph 2 — The Gap:**
State that no existing published system addresses the pre-transaction phase. Cite the specific papers/patents that demonstrate this gap. This paragraph is the justification for why this paper should be accepted — without it, reviewers don't know what problem you're solving.

**Paragraph 3 — Your Approach (high level):**
One paragraph describing BTC-Intel without details. "We present BTC-Intel, a system that integrates intelligence from Tor hidden services with Bitcoin transaction graph analysis to..." Do not use jargon the reviewer doesn't know yet.

**Paragraph 4 — Your Contributions (bulleted list):**
This is standard in security papers. Explicit, numbered list of contributions:
```
In summary, this paper makes the following contributions:
(1) We present the PRE_CRIME_WATCHLIST mechanism, the first published
    method for assigning non-zero risk to cryptocurrency addresses
    prior to any on-chain transaction. [Section 4]
(2) We introduce the shared-payment-address edge type in Tor hidden
    service graphs. [Section 5]
(3) We present a provenance-aware Bayesian evidence fusion engine that
    prevents double-counting of correlated intelligence signals. [Section 6]
(4) We evaluate BTC-Intel on [dataset] and demonstrate [X]% precision
    at [Y]% recall, outperforming the naive OFAC-taint baseline by
    [Z] percentage points on recall while maintaining comparable precision.
    [Section 7]
(5) We identify and discuss [N] research gaps in the existing blockchain
    intelligence literature and propose directions for future work. [Section 8]
```

**Paragraph 5 — Paper Organisation:**
"Section 2 presents background. Section 3 describes the threat model. Section 4 introduces..." One sentence per section.

---

### Section 2: Background and Related Work (1.5–2 pages)

**Subsection 2.1 — Bitcoin Address Clustering:**
Describe CIO clustering (Meiklejohn 2013) and change address heuristics. Explicitly state: "We use the multi-heuristic weighted voting approach of Delgado-Segura et al. [2021] for clustering. The CIO heuristic was introduced by Meiklejohn et al. [2013] and is not our contribution."

**Subsection 2.2 — Risk Propagation Methods:**
Describe taint propagation (Chainalysis patent — reference as "the commercial approach"), label propagation (Nerino 2021), and Personalised PageRank. State that you compare all three.

**Subsection 2.3 — Dark Web Intelligence:**
Cover Biryukov 2014 (onion enumeration), Spitters 2014 (topic classification), Ghosh 2017 (market analysis). State: "Our shared-payment-address edge type extends Biryukov's hyperlink graph with a novel financial signal not present in any prior work."

**Subsection 2.4 — Behavioral Analysis:**
Cover Peled 2021 and Weber 2019. State: "We extend Peled et al.'s feature set with temporal delta features and off-chain/on-chain temporal gap features."

**Critical tone for this section:**
Be generous in crediting prior work. Reviewers from those prior papers may review your paper. Understating prior contributions is the fastest way to get a rejection.

---

### Section 3: Threat Model and Problem Definition (0.5–1 page)

**What a threat model is:**
A formal statement of: who the adversary is, what they can and cannot do, what the defender (your system) is trying to achieve, and what counts as success or failure.

**BTC-Intel threat model:**

*Adversary:* A criminal actor who uses Bitcoin for illicit payments and advertises payment addresses on Tor hidden services. The adversary is assumed to: (a) generate fresh addresses for each transaction, (b) use coin mixing to obscure fund flow, (c) operate across multiple dark web markets under different aliases, and (d) bridge to other blockchains for final cash-out.

*Defender:* BTC-Intel, operating as a passive observer with: (a) access to the full public Bitcoin blockchain, (b) ability to crawl publicly accessible (unauthenticated) Tor hidden services, and (c) access to OFAC SDN lists and community intelligence databases.

*Out of scope:* The adversary's activities on Ethereum, Monero, or any other blockchain. Activities behind authentication walls on dark web markets. Operational security failures (e.g., KYC at exchanges) — these are complementary channels.

*Success criteria:* Assigning risk classifications with at least 90% precision and demonstrating detection of pre-transaction addresses that are subsequently confirmed as criminal.

---

### Section 4: System Architecture (3–4 pages)

This is the technical heart of the paper. Structure it layer by layer, matching the architecture document. Include:

- **Figure 1:** Full system architecture diagram (the one from the implementation plan)
- **For each layer:** One paragraph description + the key algorithmic decision + why you made it
- **Pseudocode or algorithm boxes** for the three novel contributions (PRE_CRIME_WATCHLIST, shared-wallet edge, provenance Bayesian)

**Key writing principle:** For each component, state what it does, then state why you chose this approach over alternatives. Reviewers want to know you considered alternatives.

---

### Section 5: The PRE_CRIME_WATCHLIST Mechanism (1–1.5 pages)

Dedicated section for your primary novel contribution. Structure:

1. **Motivation:** Explain the problem (existing systems cannot flag zero-history addresses)
2. **Design:** Explain the mechanism (context window classification → watchlist → monitoring)
3. **Confidence scoring:** Explain how the confidence score is computed
4. **Algorithm box:** Formal algorithm for the classification process
5. **Monitoring state machine:** Show the state transitions: PRE_CRIME_WATCHLIST → (first transaction detected) → WATCHLISTED/BLACKLISTED/CLEAN

---

### Section 6: Dark Web Intelligence Integration (1 page)

1. **Crawler architecture** (brief — this is not the novel contribution)
2. **Address extraction** (4-stage pipeline)
3. **The shared-wallet onion graph edge type** (novel contribution — go deep here)
4. **Entity resolution** (4-signal probabilistic resolution)

---

### Section 7: Evaluation (3–4 pages)

This section makes or breaks the paper. Weak evaluation = rejection.

**7.1 — Datasets:**
Describe each dataset used:
```
Dataset 1: OFAC SDN Cryptocurrency Addresses
  Source: U.S. Treasury OFAC SDN XML (retrieved [date])
  Size: [N] unique Bitcoin addresses
  Use: Ground truth for BLACKLISTED classification (true positives)

Dataset 2: Elliptic Bitcoin Transaction Dataset
  Source: Weber et al. 2019, available on Kaggle
  Size: 203,769 transactions, 4,545 illicit-labeled
  Use: Baseline comparison, feature evaluation

Dataset 3: WalletExplorer Service Labels
  Source: walletexplorer.com (public)
  Size: [N] exchange and service cluster labels
  Use: Ground truth for CLEAN classification (true negatives)

Dataset 4: BTC-Intel Dark Web Sample
  Source: Pre-crawled Tor hidden service pages (in-house)
  Size: [N] pages, [M] extracted Bitcoin addresses
  Availability: Cannot be released (legal constraints); hash-verified subset
               released for reproducibility
```

**7.2 — Evaluation Metrics:**
Define each metric precisely:
- Precision: TP / (TP + FP) — what fraction of BLACKLISTED classifications are correct
- Recall: TP / (TP + FN) — what fraction of known criminals are found
- F1: Harmonic mean of precision and recall
- False Positive Rate (FPR): FP / (FP + TN) — what fraction of clean addresses are incorrectly flagged

**7.3 — Baseline Comparison:**
Compare against at least two baselines:
1. **Naive baseline:** Single-hop OFAC taint only
2. **Peled 2021 baseline:** Random Forest on Elliptic features (reproduced)
3. **BTC-Intel:** Your full system

**7.4 — Ablation Study:**
This is required for top venues. Test each component individually to prove it contributes:
```
System variant             | Precision | Recall | F1
--------------------------|-----------|--------|----
Full BTC-Intel             |    X.XX   |  X.XX  | X.XX
- Without PRE_CRIME layer  |    X.XX   |  X.XX  | X.XX  (shows Contribution 1 impact)
- Without DW intelligence  |    X.XX   |  X.XX  | X.XX  (shows dark web adds value)
- Without temporal features|    X.XX   |  X.XX  | X.XX  (shows temporal features add value)
- Without Bayesian (rules) |    X.XX   |  X.XX  | X.XX  (shows Bayesian adds value)
- Without provenance dedup |    X.XX   |  X.XX  | X.XX  (shows dedup prevents inflation)
```

**7.5 — PRE_CRIME_WATCHLIST Evaluation (novel):**
This is the hardest evaluation because you need ground truth for pre-transaction classification. How to build the test set:
1. Find OFAC addresses that were confirmed criminal (OFAC listing date known)
2. Check BTC-Intel's crawl records: was this address in dark web data BEFORE the OFAC listing date?
3. If yes: this is a true positive for PRE_CRIME_WATCHLIST (caught before OFAC noticed)
4. Report how many addresses BTC-Intel would have flagged N days before OFAC confirmation

**7.6 — Three-Way Propagation Comparison:**
```
Method         | Precision | Recall | F1   | FPR
--------------|-----------|--------|------|-----
Taint          |           |        |      |
Label Prop.    |           |        |      |
PPR            |           |        |      |
Ensemble       |           |        |      |
```

---

### Section 8: Limitations (0.5 pages)

**This section is not optional.** Reviewers will find your limitations anyway — it's better to state them yourself. Shows intellectual honesty and prevents "why didn't they address X?" rejections.

Required limitations to state:
- Authentication wall: ~8% unauthenticated surface coverage (cite Owenson 2018)
- Cross-chain blind spot: cannot track funds that exit to Ethereum, Monero, or other chains
- Taproot clustering degradation: script-type heuristic is unreliable for P2TR
- Lightning Network off-chain invisibility
- Temporal lag: Tor crawl data has 1–24 hour freshness latency
- Evaluation dataset coverage: Elliptic dataset ends 2018; criminal behavior has evolved

---

### Section 9: Ethics and Legal Considerations (0.5 pages)

Many top venues now require an explicit ethics section. Include:
- IRB approval status and protocol number (or statement that research qualified for exemption)
- GDPR compliance statement (data minimisation, retention policy)
- Statement that researchers did not participate in any criminal activity during dark web crawling
- Statement on responsible disclosure (if any active criminal infrastructure was discovered)
- Data availability: what can and cannot be released (dark web raw pages likely cannot; feature vectors may be releasable after de-identification)

---

### Section 10: Conclusion (0.5 pages)

Three paragraphs:
1. Summary: what you built and what it demonstrated
2. Key finding: the one number that matters most (e.g., "BTC-Intel identified X% of subsequently OFAC-confirmed addresses in the PRE_CRIME_WATCHLIST state an average of Y days before OFAC action")
3. Future work: temporal graph networks for lifecycle modeling; cross-chain extension to Ethereum; authentication-capable crawling for authenticated market access

---

## 9. Abstract Templates for BTC-Intel

### Paper Abstract Template (250 words max)

```
Cryptocurrency-based financial crime poses a significant challenge to
law enforcement and financial institutions. Existing blockchain analytics
systems — both commercial and academic — share a fundamental limitation:
they can only assess risk for addresses that have participated in at
least one on-chain transaction. This leaves a pre-transaction window
during which criminal payment infrastructure is established but entirely
invisible to monitoring systems.

We present BTC-Intel, a cryptocurrency threat intelligence system that
integrates intelligence from Tor hidden services with Bitcoin transaction
graph analysis to address this gap. BTC-Intel introduces the
PRE_CRIME_WATCHLIST classification, assigning non-zero risk to Bitcoin
addresses found in payment-context documents on dark web markets prior
to any on-chain activity. We additionally contribute: (1) a shared-payment-
address edge type for Tor hidden service infrastructure graphs that reveals
criminal coordination relationships not present in hyperlink-based graphs;
and (2) a provenance-aware Bayesian evidence fusion engine that prevents
circular double-counting of correlated intelligence signals.

We evaluate BTC-Intel on a combination of OFAC SDN confirmed addresses,
the Elliptic Bitcoin dataset, and WalletExplorer service labels.
BTC-Intel achieves [X]% precision at [Y]% recall on the confirmed
criminal address classification task, outperforming the single-hop OFAC
taint baseline by [Z] percentage points on recall while maintaining
precision above [W]%. Critically, BTC-Intel identified [N]% of
subsequently OFAC-confirmed criminal addresses in the PRE_CRIME_WATCHLIST
state an average of [D] days prior to official designation.
```

### Patent Abstract Template (150 words max)

```
A computer-implemented method assigns risk classifications to
cryptocurrency addresses prior to on-chain transaction activity.
The method retrieves documents from Tor hidden service networks and
classifies text surrounding extracted cryptocurrency addresses as
payment-context or non-payment-context using natural language processing.
Cryptocurrency addresses classified as payment-context and having no
on-chain transaction history receive a PRE_CRIME_WATCHLIST classification
and confidence score. The method monitors designated addresses for
first on-chain transactions and updates risk classifications upon
detection. A provenance-aware Bayesian inference engine combines
evidence from multiple sources while tracking evidence provenance chains
to prevent double-counting of correlated signals. An onion service
graph uses shared cryptocurrency address co-appearances as edge
weights between hidden service domains to reveal criminal network
infrastructure relationships.
```

---

## 10. Evidence and Evaluation: What Numbers You Must Have

These are the measurements that MUST be in your paper before submission. Without these, the paper is rejected for insufficient evaluation. Collect all of these during your evaluation phase (Week 9 of the POC plan):

### Required Measurements

| Measurement | Why Required | Where in Paper |
|-------------|-------------|----------------|
| Precision (BLACKLISTED) on OFAC test set | Proves system doesn't over-flag | Section 7.3 |
| Recall (BLACKLISTED) on OFAC test set | Proves system finds criminals | Section 7.3 |
| F1 score | Summary metric | Section 7.3 |
| False Positive Rate on known-clean set | Proves operational usability | Section 7.3 |
| Elliptic baseline precision/recall | Proves you reproduced Peled 2021 | Section 7.3 |
| Your system vs. Elliptic baseline delta | Proves improvement | Section 7.3 |
| Ablation results for each component | Proves each component contributes | Section 7.4 |
| Number of PRE_CRIME_WATCHLIST addresses | Proves the mechanism produces output | Section 7.5 |
| Days-before-OFAC for PRE_CRIME addresses | Proves early detection value | Section 7.5 |
| Three-way propagation comparison table | Proves propagation method matters | Section 7.6 |
| Cluster precision (CIO on evaluation set) | Validates clustering component | Section 7 |
| Processing time per address | Demonstrates operational feasibility | Section 7 |

### Numbers to NEVER Claim Without Measurement

The following claims will get your paper rejected if you cannot support them with measured data:

- "BTC-Intel achieves X% precision" — if X is fabricated or estimated
- "Our system outperforms Chainalysis" — cannot measure against proprietary system
- "Processing time is sub-200ms" — must be measured on specific hardware, specified
- "We analyzed X million addresses" — must be verifiable from your dataset description
- "Y% of dark web addresses are criminal" — wild claim; needs ground truth

---

## 11. Avoiding Common Rejection Reasons

### Rejection Reason 1: "The contributions are not clearly distinguished from prior work"

**Fix:** Add a table at the end of Section 2 explicitly comparing your system to prior work, with a column for each contribution and a checkmark showing which prior papers do and do not address it.

### Rejection Reason 2: "Insufficient evaluation — the experimental results do not support the claims"

**Fix:** Ensure every claim in your contribution list (Section 1) has a corresponding experimental result in Section 7. If you claim "first published system to do X," you need to prove that no prior paper does X (cite absence of results in those papers).

### Rejection Reason 3: "The threat model is unrealistic"

**Fix:** Acknowledge in your threat model exactly what your system cannot do (see limitations section). Reviewers trust papers that know their own limitations.

### Rejection Reason 4: "Ethical concerns — crawling dark web sites without authorisation"

**Fix:** Include the explicit ethics section (Section 9). State IRB status. State that crawling public (unauthenticated) dark web sites is legally analogous to crawling public surface web sites — both are public-facing servers accessible without authentication. Cite legal precedent if possible.

### Rejection Reason 5: "Novelty is incremental — this is just applying existing techniques to a new domain"

**Fix:** This is the hardest rejection to overcome for a system paper. Pre-empt it by: (a) explicitly stating in the introduction what you claim as novel vs. what you took from prior work, and (b) including your ablation study, which proves that the specific novel combination produces results that individually cannot be achieved.

### Rejection Reason 6: "Reproducibility — the dark web dataset cannot be shared"

**Fix:** Provide reproducibility in two ways: (1) release a SHA-256 hash of the raw dataset for verification if requested under NDA, and (2) release all code for the pipeline components that don't depend on the dark web data (the Elliptic evaluation, the clustering algorithm, the Bayesian engine). Make these available on GitHub and reference from the paper.

---

## 12. Timeline: When to File Patent vs. When to Submit Paper

```
MONTH 0   File Provisional Patent Application
          [Priority date established]

MONTH 0   File arXiv preprint (cs.CR)
          [Academic priority established]

MONTH 1   Submit workshop paper to FC Workshop on WTSC
          (6 pages, preliminary results only)

MONTH 2   Complete POC evaluation (collect all required measurements)

MONTH 3   Write full paper (12–16 pages)
          Have 2 colleagues proofread (at least one not on the project)

MONTH 4   Submit to Financial Cryptography (FC) — target primary venue

MONTH 5   Receive workshop paper decision
          Present at workshop (establishes public presentation record)

MONTH 6   Begin drafting Non-Provisional Patent Application

MONTH 8   FC decision (accept/reject/revision)
          If revision requested: address all reviewer comments
          If rejected: revise and resubmit to NDSS

MONTH 10  File PCT International Application
          [International priority established in 157 countries]

MONTH 11  File Non-Provisional US Patent Application

MONTH 12  Provisional patent expires (12-month deadline)
          Must have filed non-provisional by now

MONTH 14  FC paper published at conference (if accepted)

MONTH 18  PCT application published (public — was confidential until now)

MONTH 30  Enter national phase in selected countries (EPO, UKIPO, JPO, etc.)
```

**Critical path:** Month 0 (provisional filing) → Month 12 (non-provisional filing) is the hardest deadline. Missing it means losing your priority date.

---

## 13. Budget and Resource Planning

### Patent Budget

| Item | Cost (Self-file) | Cost (With Agent) | Notes |
|------|-----------------|------------------|-------|
| Provisional patent (USPTO filing fee) | $320 | $320 + $1,500 agent fee | Micro-entity rate |
| Prior art search | $0 (self) | $1,000–$2,000 | Agent searches are thorough |
| Non-provisional (USPTO fees) | $800 | $800 + $3,000 agent | Includes exam fee |
| PCT application (USPTO fees) | $3,000 | $3,000 + $2,000 agent | International |
| EPO national phase | €4,000+ | +€2,000 agent | If Europe targeted |
| USPTO examiner responses | $0–$600 | $1,500–$3,000 | For each office action |
| **Total (US only, with agent)** | | **~$10,000–$15,000** | Over 2–3 years |
| **Total (international, with agent)** | | **~$25,000–$40,000** | Over 3–5 years |

**Funding sources for academic researchers:**
- University Technology Transfer Office — they often cover patent costs in exchange for a share of licensing revenue
- Proof of Concept grants (NSF I-Corps, Innovate UK, EIC Accelerator)
- Research commercialisation funds at most major universities

### Paper Budget

| Item | Cost | Notes |
|------|------|-------|
| Conference registration (if accepted) | $600–$1,200 | Required for presentation |
| Travel and accommodation | $1,000–$3,000 | If in-person conference |
| Open access publication fee (optional) | $0–$1,500 | Most security venues don't require open access |
| arXiv submission | $0 | Free |
| Proofreading (professional) | $200–$500 | Highly recommended for non-native English writers |
| **Total** | **~$2,000–$5,000** | |

---

## 14. The arXiv Preprint Strategy: Establishing Priority Without Delay

### Why arXiv Matters Even if You're Filing a Patent

arXiv creates a timestamped public record of your work that is indexed by Google Scholar and widely read in the computer science community. An arXiv submission:
- Establishes public academic priority (in case someone independently publishes similar work)
- Generates citations before formal publication (papers often cite arXiv versions)
- Gets your work in front of potential collaborators, reviewers, and employers
- Can be updated with improved versions while the formal paper is under review

### arXiv Submission Process

1. Go to: https://arxiv.org/submit
2. Select category: **cs.CR** (Cryptography and Security) as primary; **cs.SI** (Social and Information Networks) as cross-list
3. Upload a PDF of your paper (use LaTeX — arXiv requires LaTeX source or PDF from LaTeX)
4. Write a 1–3 paragraph plain-text abstract for arXiv (shorter than paper abstract is fine)
5. List all authors
6. Set license: CC BY 4.0 (permissive, most compatible with conference copyright transfers)

**Important arXiv rules:**
- Submissions are moderated — allow 1–3 business days for approval
- Once submitted, you cannot fully retract (only "withdraw" leaving a stub)
- If a conference requires double-blind review, check their policy on arXiv preprints — some ban them during review
- Financial Cryptography requires double-blind: submit arXiv AFTER the FC review window closes, or use an anonymised preprint version

### The Anonymous Preprint Strategy

For double-blind conferences:
1. File provisional patent (establishes private priority date)
2. Submit anonymised preprint to arXiv (no author names, institution scrubbed from PDF)
3. Submit non-anonymous version to conference under double-blind rules
4. After acceptance (and de-anonymisation), update arXiv with the named version

---

## 15. Checklists

### Patent Ready Checklist

Before filing your provisional application, confirm ALL of the following:

- [ ] Inventor's notebook entry dated and witnessed
- [ ] Prior art search completed for all three primary claims
- [ ] Confirmed Chainalysis US10977655B2 does not read on your primary claim
- [ ] Confirmed no TRM Labs pending application covers PRE_CRIME_WATCHLIST (18-month window risk)
- [ ] Provisional application text written (all 8 required sections present)
- [ ] Drawings prepared (system diagrams, flowcharts, all elements numbered)
- [ ] USPTO account created on Patent Center
- [ ] Micro-entity qualification confirmed (income < 3× US median)
- [ ] $320 payment method ready
- [ ] Application Number recorded after filing (keep in 3 locations)
- [ ] 12-month non-provisional deadline calendared (with 1-month buffer reminder)
- [ ] 12-month PCT deadline calendared (same date as non-provisional)

### Paper Ready Checklist

Before submitting to any venue, confirm ALL of the following:

**Content:**
- [ ] All five contributions from Section 1 are addressed in evaluation Section 7
- [ ] Baseline comparison with at least two prior approaches included
- [ ] Ablation study with at least 5 system variants reported
- [ ] PRE_CRIME_WATCHLIST evaluation (days-before-OFAC metric) included
- [ ] Three-way propagation comparison table included
- [ ] Limitations section explicitly addressing 6 documented limitations
- [ ] Ethics section with IRB status and GDPR compliance statement
- [ ] Prior art is cited generously and nothing is claimed as novel without justification

**Format:**
- [ ] Page count within venue limit (check specific call for papers)
- [ ] Uses correct template (ACM, IEEE, or Springer LNCS depending on venue)
- [ ] All figures have captions and are referenced in text
- [ ] All tables have captions and are referenced in text
- [ ] No self-identifying information in double-blind submission version
- [ ] References are complete (all cited works have full citation details)
- [ ] Abstract is within word limit (check venue: typically 200–300 words)

**Quality:**
- [ ] Proofread by at least two people who were not involved in writing
- [ ] All numerical claims (precision, recall, etc.) are measured values, not estimates
- [ ] All "X%" claims are backed by a table or figure in the paper
- [ ] Reproducibility statement included (what code/data is released and where)
- [ ] GitHub repository created with released code, README, and license

**Submission:**
- [ ] Submission deadline confirmed (not estimated — check venue website)
- [ ] Submission system account created
- [ ] PDF generated from LaTeX source (not Word — most venues strongly prefer LaTeX)
- [ ] Supplementary material prepared if any (appendices, extended proofs, additional results)

---

## Final Advice: The Two Most Important Things

**1. File the provisional patent application this week.**
Not next month. Not after you finish the evaluation. This week. The $320 cost is trivial compared to the risk of losing your priority date to a competitor who files one week before you. Everything else in this document can wait; the provisional patent cannot.

**2. Do not claim more than you can prove.**
The single fastest path to paper rejection and patent invalidation is overclaiming. If your system achieves 87% precision, say 87%. If your PRE_CRIME_WATCHLIST mechanism identifies 40% of OFAC addresses before OFAC acts, say 40%. Reviewers and patent examiners are experts who will verify your claims. The moment they find one overstatement, they distrust everything else in the document.

The research gap is real. The contributions are novel. The implementation is sound. Present it honestly and let the results speak.

---

*This document should be reviewed by a registered patent attorney before any patent filing. The claim templates provided are starting points for discussion with legal counsel, not final legal documents. Laws and procedures vary by jurisdiction and change over time.*
