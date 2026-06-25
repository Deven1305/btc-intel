# setup/windows/03_neo4j_setup.md

Stepwise Neo4j Community Edition install on Windows, assuming zero prior
experience.

**Important — read this before downloading anything:** Neo4j Desktop (the
GUI app most tutorials point you to) bundles **Neo4j Enterprise Edition**
under a free "Developer" license, NOT Community Edition — confirmed
current as of June 2026. Since the architecture doc (Section 4) specifies
Community, we install the **standalone Community zip** instead of Neo4j
Desktop. This is more terminal-driven than Desktop, but it's the only way
to be certain you're running genuine Community Edition.

---

## Step 1 — Download

[Windows browser]
1. Go to https://neo4j.com/deployment-center/
2. Under "Graph Database Self-Managed", find **Community Edition**.
3. Download the **Windows Executable (.zip)** for the current release
   (e.g. `neo4j-community-<version>-windows.zip` — re-check the page for
   the current version number; as of June 2026 the latest is the
   2026.05.x calendar-versioned release line, but Neo4j 5.x is also still
   actively supported if you'd rather pin to that major line for closer
   alignment with the architecture doc's "Neo4j Community 5.x" wording —
   either works with the code in this repo, since the Python `neo4j`
   driver and Cypher used here are stable across both).
4. You also need a **Java Runtime** — Neo4j runs on the JVM. Check the
   Deployment Center page for the exact JDK version your chosen Neo4j
   release requires (it states this directly above the download link),
   and if you don't already have it, download the matching **Eclipse
   Temurin JDK** (free, no license friction) from
   https://adoptium.net/temurin/releases/ for Windows x64.

## Step 2 — Install the JDK (if you don't already have one)

[Windows cmd/PowerShell — run the Temurin .msi installer as Administrator]
Accept the defaults. The installer sets `JAVA_HOME` for you. Verify:
```
java -version
```

## Step 3 — Extract Neo4j

[Windows cmd/PowerShell]
1. Right-click the downloaded zip → **Extract All** → extract to
   `C:\neo4j\` (so you end up with e.g.
   `C:\neo4j\neo4j-community-2026.05.0\`).
2. Set an environment variable so commands below are shorter:
```
setx NEO4J_HOME "C:\neo4j\neo4j-community-2026.05.0"
```
   (Open a **new** terminal after this for the variable to take effect.)

## Step 4 — Set the initial password

Community Edition ships with a default account `neo4j` and requires you
to set a real password before first use — there's no installer screen for
this since there's no installer; it's done with the bundled admin tool.

[Windows cmd/PowerShell]
```
cd %NEO4J_HOME%\bin
neo4j-admin dbms set-initial-password CHANGE_ME
```
Use the SAME value here as the `NEO4J_PASSWORD` you'll put in `.env`.

## Step 5 — Start Neo4j and verify it's running

[Windows cmd/PowerShell]
```
cd %NEO4J_HOME%\bin
neo4j console
```
This runs Neo4j in the foreground (good for your first check — you'll see
log output directly and can Ctrl+C to stop it). Leave this window open.

[Windows browser]
Open http://localhost:7474 — this is the **Neo4j Browser**. A successful
first login looks like: a connection screen asking for username/password
(use `neo4j` / the password from Step 4), then a query input bar at the
top of the page once connected.

Run this in the Neo4j Browser's query bar to confirm the edition:
```cypher
CALL dbms.components() YIELD name, edition RETURN name, edition;
```
This should show `edition: "community"` — confirming Community, not
Enterprise (the original design's Section 4 requirement).

## Step 6 — Run it as a Windows service instead (recommended after the first check)

Running `neo4j console` in a terminal window works, but means Neo4j stops
if you close that window. Installing it as a proper Windows service means
it starts automatically and runs in the background — closer to how
PostgreSQL behaves.

[Windows cmd/PowerShell — run as Administrator]
```
cd %NEO4J_HOME%\bin
neo4j windows-service install
neo4j windows-service start
```
Verify the same way as the GUI/HTTP check (Step 5), or via Windows
Services:
```
net start "Neo4j Graph Database - <version>"
net stop "Neo4j Graph Database - <version>"
```
Or: Win+R → `services.msc` → find the Neo4j service → Start/Stop/Restart.

## Update `.env`

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=CHANGE_ME
```
(Port 7687 is the Bolt protocol port Neo4j uses for driver connections —
this is the default and matches the `services/graph/onion_graph.py` driver
config; 7474 is only the HTTP Browser UI port, used for the manual check
in Step 5, not by the Python code.)
