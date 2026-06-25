#!/usr/bin/env bash
# setup/linux_vm/day1_setup_vm.sh
#
# [Inside Ubuntu VM — run via SSH, e.g. ssh btcintel@127.0.0.1 -p 2222]
#
# This is the VM-side half of "day 1" setup — Tor + Splash only. It is
# OPTIONAL: the default path for populating dark_web_records uses
# scripts/ingest_archive.py on the Windows host against already-acquired
# archive content (see README "Dark web data"), which needs neither this
# VM nor Tor running. Run this script only if you specifically want the
# Tor/Splash stack available, e.g. for locally rendering JS-heavy pages
# from content you already have independent, legitimate access to.
#
# Assumes you've already completed setup/windows/01_virtualbox_vm_setup.md
# Steps 1-6 (VM created, Ubuntu Server installed, SSH reachable, clean
# snapshot taken).

set -euo pipefail

echo "=== BTC-Intel Day 1 Setup (inside Ubuntu VM) ==="

echo
echo "[1/4] Updating package lists..."
sudo apt update && sudo apt upgrade -y

echo
echo "[2/4] Installing Tor..."
sudo apt install -y tor
sudo systemctl enable --now tor
sleep 2
if ss -tlnp 2>/dev/null | grep -q ":9050"; then
    echo "  Tor SOCKS5 proxy listening on 127.0.0.1:9050 -- OK"
else
    echo "  WARNING: Tor does not appear to be listening on port 9050. Check 'sudo systemctl status tor'."
fi

echo
echo "[3/4] Installing Docker and starting Splash..."
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
docker pull scrapinghub/splash
docker rm -f splash 2>/dev/null || true
docker run -d --name splash -p 8050:8050 scrapinghub/splash \
    --proxy-profiles-path /etc/splash/proxy-profiles

echo
echo "[4/4] Verifying Tor connectivity (own circuit only, no .onion fetch)..."
curl --socks5-hostname 127.0.0.1:9050 -s https://check.torproject.org/api/ip || \
    echo "  WARNING: Tor connectivity check failed. Re-run after 'sudo systemctl restart tor'."

echo
echo "=== VM setup complete ==="
echo "Splash is reachable from the Windows host at http://localhost:8050 (port-forward this"
echo "the same way you forwarded SSH in setup/windows/01_virtualbox_vm_setup.md Step 5, if needed)."
echo "Remember: take a fresh VBoxManage snapshot now if you want this state as your new baseline."
