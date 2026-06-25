# setup/windows/day1_setup_windows.ps1
#
# [Windows cmd/PowerShell — run from project root, e.g. C:\btc-intel]
#
# This is the Windows-host half of "day 1" setup. It assumes you've already
# completed the manual installer steps in 01_virtualbox_vm_setup.md (if you
# want the Tor/Splash VM at all),  02_postgresql_setup.md, and
# 03_neo4j_setup.md, since those involve GUI installer screens that can't
# be meaningfully scripted. This script handles everything that CAN be
# scripted: Python environment, schema load, seed collection, and launching
# the dashboard.
#
# Run the matching Linux-inside-VM script (setup/linux_vm/day1_setup_vm.sh)
# separately, INSIDE the VM, only if you're using the Tor/Splash stack —
# it is NOT required for the default ingest_archive.py path.

Write-Host "=== BTC-Intel Day 1 Setup (Windows host) ===" -ForegroundColor Cyan

# 1. Python virtual environment (Anaconda Prompt recommended, but works in
#    plain PowerShell too if you have Python 3.11 on PATH)
Write-Host "`n[1/6] Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Python dependencies
Write-Host "`n[2/6] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# 3. Copy .env template if not already present
if (-not (Test-Path ".env")) {
    Write-Host "`n[3/6] Creating .env from template — EDIT THIS before continuing!" -ForegroundColor Red
    Copy-Item ".env.example" ".env"
    Write-Host "Opened .env.example as .env. Fill in real credentials, then re-run this script." -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n[3/6] .env already exists, skipping template copy." -ForegroundColor Yellow
}

# 4. Load the database schema (assumes PostgreSQL is already running —
#    see setup/windows/02_postgresql_setup.md)
Write-Host "`n[4/6] Loading database schema..." -ForegroundColor Yellow
# Reads POSTGRES_URI components from .env for the psql call.
$envContent = Get-Content ".env" | Where-Object { $_ -match "^POSTGRES_URI=" }
Write-Host "Using: $envContent"
Write-Host "Run manually if this fails: psql -U btcintel -d btcintel -h localhost -f schema/001_init.sql"
psql -U btcintel -d btcintel -h localhost -f schema/001_init.sql

# 5. Collect seeds (first real data — all open HTTPS sources, no Tor needed)
Write-Host "`n[5/6] Collecting seed addresses from OFAC/UN/Chainabuse/CryptoScamDB/SlowMist..." -ForegroundColor Yellow
python scripts/collect_seeds.py
# Expected output:
#   OFAC: ~700-800 BTC addresses
#   UN: ~30-60 BTC addresses
#   Chainabuse: ~100 reports
#   [OK] Stored ~1,000+ criminal seeds, hundreds of service labels

# 6. Launch the dashboard
Write-Host "`n[6/6] Launching dashboard at http://localhost:8501 ..." -ForegroundColor Green
streamlit run dashboard/app.py --server.port 8501
