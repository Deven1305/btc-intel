# setup/windows/02_postgresql_setup.md

Stepwise PostgreSQL 16 install on Windows, assuming zero prior experience.

---

## Step 1 — Download

[Windows browser]
1. Go to https://www.postgresql.org/download/windows/
2. Click **Download the installer** — this links to the EDB (EnterpriseDB)
   Windows installer page, which is the official Windows build PostgreSQL
   itself recommends.
3. Pick **PostgreSQL 16.x** (the latest 16.x point release — keep major
   version 16, matching Section 12's schema target) for **Windows x86-64**.
   Re-check the page for the current 16.x point number before downloading;
   point releases (16.0 -> 16.1 -> ...) ship regularly but the major
   version (16) is what matters for compatibility here.

## Step 2 — Run the installer

[Windows cmd/PowerShell — run the downloaded .exe as Administrator]

You'll see these screens, in order:

1. **Welcome** → Next.
2. **Installation Directory** → keep the default
   (`C:\Program Files\PostgreSQL\16`) → Next.
3. **Select Components** → keep all four checked: PostgreSQL Server,
   pgAdmin 4, Stack Builder, Command Line Tools → Next.
   (pgAdmin 4 is a GUI you likely won't need day-to-day since you'll use
   `psql` and Python, but it's useful for poking at the schema visually if
   you get stuck — no harm in keeping it.)
4. **Data Directory** → keep the default → Next.
5. **Password** → **this is the most important screen.** Set a password
   for the `postgres` superuser. Write it down somewhere safe — you'll
   need it in the next step. (This is a different account from the
   `btcintel` app user you'll create afterward.)
6. **Port** → keep the default **5432** (this matches the
   `POSTGRES_URI` template in `.env.example`, which assumes 5432 — if you
   change it here, also change it in `.env`).
7. **Advanced Options / Locale** → keep the default.
8. **Pre Installation Summary** → Next → installs (takes a few minutes).
9. At the end, **uncheck** "Launch Stack Builder at exit" (Stack Builder
   installs optional extensions/drivers we don't need for this project) →
   Finish.

## Step 3 — Verify it's running

[Windows cmd/PowerShell]
```
psql -U postgres
```
Enter the password from Step 2, Screen 5. A successful first login looks
like this prompt:
```
psql (16.x)
Type "help" for help.

postgres=#
```
If `psql` isn't recognized, the installer didn't add it to PATH — open a
**new** terminal window first (PATH changes need a fresh shell), or use
the full path:
```
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres
```

Type `\q` and press Enter to exit `psql`.

## Step 4 — Create the btcintel user and database

[Windows cmd/PowerShell]
```
psql -U postgres
```
Then, at the `postgres=#` prompt, run each line (replace `CHANGE_ME` with
a real password — use the SAME value you'll put in `.env`'s
`POSTGRES_URI`):
```sql
CREATE USER btcintel WITH PASSWORD 'CHANGE_ME';
CREATE DATABASE btcintel OWNER btcintel;
GRANT ALL PRIVILEGES ON DATABASE btcintel TO btcintel;
\q
```

## Step 5 — Load the schema

[Windows cmd/PowerShell — run from the project root, e.g. `C:\btc-intel`]
```
psql -U btcintel -d btcintel -h localhost -f schema/001_init.sql
```
Enter the `btcintel` user's password (the `CHANGE_ME` value from Step 4)
when prompted. This is the **one exact command** that loads every table
from Section 12 (plus the new `graph_cache` table — see README "Gaps I
found"). No output beyond a series of `CREATE TABLE` / `CREATE INDEX`
lines means success.

Verify the tables exist:
```
psql -U btcintel -d btcintel -h localhost -c "\dt"
```
You should see `seed_addresses`, `service_labels`, `dark_web_records`,
`pre_crime_watchlist`, `taint_scores`, `address_clusters`,
`risk_decisions`, `crawl_queue`, `reassessment_queue`,
`evaluation_results`, `audit_log`, and `graph_cache`.

## Step 6 — Managing the service on Windows

PostgreSQL installs as a Windows **service**, so it starts automatically
on boot — you usually won't need to touch this. If you ever do:

[Windows cmd/PowerShell — run as Administrator]
```
net stop postgresql-x64-16
net start postgresql-x64-16
```
Or via the GUI: press Win+R, type `services.msc`, find
**postgresql-x64-16**, right-click → Start/Stop/Restart.

## Update `.env`

Set `POSTGRES_URI` to match what you created:
```
POSTGRES_URI=postgresql://btcintel:CHANGE_ME@localhost:5432/btcintel
```
