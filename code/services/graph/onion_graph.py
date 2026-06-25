# services/graph/onion_graph.py
"""
Builds a Neo4j graph where nodes are onion domains and SHARES_WALLET edges
connect domains that both list the same Bitcoin payment address. Edge
weight = number of shared addresses (the more shared, the stronger).

Why this beats a hyperlink edge: a hyperlink from forum X to market Y might
just be a recommendation, a review, or spam — it proves nothing about
shared operation. But if market Y and market Z both print the same address
as their checkout address, the same person controls the private key for
both checkouts. That is operational coordination, not a citation.

This module reads dark_web_records (populated by scripts/ingest_archive.py
from already-acquired archive content) and writes to Neo4j. It does not
fetch or crawl anything itself.
"""
from neo4j import GraphDatabase


class OnionGraphBuilder:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def build_from_records(self, db_conn) -> int:
        """Read dark_web_records, find addresses appearing on >1 domain in PAYMENT
           context, and create weighted SHARES_WALLET edges between those domains."""
        with db_conn.cursor() as cur:
            cur.execute("""
                SELECT address, ARRAY_AGG(DISTINCT onion_domain) AS domains
                FROM dark_web_records
                WHERE context_type = 'PAYMENT'
                GROUP BY address
                HAVING COUNT(DISTINCT onion_domain) > 1
            """)
            shared = cur.fetchall()

        edges = 0
        with self.driver.session() as sess:
            for address, domains in shared:
                for d in domains:
                    sess.run("MERGE (n:OnionDomain {domain:$d})", d=d)
                for i in range(len(domains)):
                    for j in range(i + 1, len(domains)):
                        sess.run("""
                            MATCH (a:OnionDomain {domain:$a}), (b:OnionDomain {domain:$b})
                            MERGE (a)-[r:SHARES_WALLET]-(b)
                            ON CREATE SET r.weight = 1, r.addresses = [$addr]
                            ON MATCH  SET r.weight = r.weight + 1,
                                          r.addresses = r.addresses + $addr
                        """, a=domains[i], b=domains[j], addr=address)
                        edges += 1
        return edges

    def find_infrastructure_groups(self, min_weight: int = 1) -> list[list[str]]:
        """Connected components over SHARES_WALLET edges = operator infrastructure groups."""
        with self.driver.session() as sess:
            result = sess.run("""
                CALL gds.graph.project.cypher(
                  'onion',
                  'MATCH (n:OnionDomain) RETURN id(n) AS id',
                  'MATCH (a:OnionDomain)-[r:SHARES_WALLET]-(b:OnionDomain)
                   WHERE r.weight >= $w
                   RETURN id(a) AS source, id(b) AS target',
                  {parameters: {w: $w}})
                YIELD graphName
                WITH graphName
                CALL gds.wcc.stream(graphName) YIELD nodeId, componentId
                RETURN componentId, COLLECT(gds.util.asNode(nodeId).domain) AS domains
                ORDER BY SIZE(domains) DESC
            """, w=min_weight)
            return [rec["domains"] for rec in result if len(rec["domains"]) > 1]
