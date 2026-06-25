# setup/windows/01_virtualbox_vm_setup.md

This replaces Section 4 ("College Server + VM Setup") for a single-user
Windows laptop/desktop instead of a bare-metal Ubuntu host with KVM.
VirtualBox gives the same "blast shield" isolation property KVM did in the
original design — an exploited or misbehaving process inside the VM cannot
touch your real filesystem, your PostgreSQL/Neo4j/MinIO data, or your host
network identity outside of what the VM's own network adapter exposes.

**What this VM is for in this build:** Tor + Splash only — the rendering
and proxy stack for processing already-acquired archive content (see
README "Dark web data" section for why this project does not run a live
crawler against the open dark web). It does not run PostgreSQL, Neo4j,
MinIO, or any of the heavier services — those run natively on the Windows
host (see `02_postgresql_setup.md`, `03_neo4j_setup.md`,
`04_minio_redis_setup.md`).

---

## Step 1 — Install VirtualBox on Windows

Current stable release as of June 2026: **VirtualBox 7.2.10** (released
June 16, 2026). Always re-check https://www.virtualbox.org/wiki/Downloads
for the current number before downloading — Oracle ships frequent
maintenance releases.

[Windows browser]
1. Go to https://www.virtualbox.org/wiki/Downloads
2. Under "VirtualBox 7.2.10 platform packages", click **Windows hosts**.
   This downloads `VirtualBox-7.2.10-<build>-Win.exe` (~170-180 MB).
3. Also download the **VirtualBox Extension Pack** from the same page
   (same version number). You don't strictly need it for this VM (no
   USB passthrough, no RDP needed), but it's free for personal/educational
   use and worth having.

[Windows cmd/PowerShell — run as Administrator]
4. Run the downloaded `.exe`. Accept all installer defaults:
   - Custom Setup: keep all components checked (VirtualBox USB Support,
     Networking, Python Support).
   - You'll see a warning that installing the network features will
     temporarily disconnect your network — this is normal, click Yes.
   - Windows may prompt to install a driver from "Oracle Corporation" —
     click Install/Allow.
5. Launch VirtualBox from the Start menu to confirm it opens (empty VM
   list is expected on first run).

---

## Step 2 — Download Ubuntu Server (not Desktop)

Current LTS as of June 2026: **Ubuntu Server 24.04.4 LTS** ("Noble
Numbat"). Always re-check https://ubuntu.com/download/server for the
current point release before downloading.

[Windows browser]
1. Go to https://ubuntu.com/download/server
2. Click **Download 24.04.4 LTS**. This downloads an ISO
   (`ubuntu-24.04.4-live-server-amd64.iso`, ~2-3 GB).

We use Server, not Desktop, because this VM only runs Tor + a Splash
Docker container + a small Python script — there's no need for a GUI,
and Server uses less RAM/disk for the same workload.

---

## Step 3 — Create the VM

This VM only needs to run Tor + Splash + a Python script processing
archive content through them — it is NOT running PostgreSQL/Neo4j/MinIO
(those live on the host). Give it a modest allocation:

| Setting | Value | Why |
|---|---|---|
| RAM | 4096 MB (4 GB) | Tor + one Splash container + Python is light; 4 GB leaves headroom |
| vCPUs | 2 | Splash's headless rendering benefits from 2 cores; more is wasted here |
| Disk | 40 GB, dynamically allocated | OS + Docker + Tor + temp files; archive HTML itself lives on the host, not in the VM |
| Network | NAT (see Step 5 for why) | |

[Windows: VirtualBox GUI]
1. Open VirtualBox. Click **New**.
2. Name: `btcintel-crawler`. Type: Linux. Version: Ubuntu (64-bit).
3. Memory size: drag to **4096 MB**.
4. Processors: **2**.
5. Hard disk: **Create a Virtual Hard Disk Now**. Type **VDI**,
   **Dynamically allocated**, size **40 GB**.
6. Click **Finish**.
7. Select the new VM → **Settings** → **Storage** → click the empty
   optical drive icon → **Choose a disk file** → select the Ubuntu
   Server ISO you downloaded in Step 2.

---

## Step 4 — Install Ubuntu Server inside the VM

[Inside Ubuntu VM — this is the VM's own installer, not a host terminal]
1. Start the VM (double-click it in VirtualBox, or click **Start**).
2. The Ubuntu Server installer (Subiquity) boots from the ISO. Follow the
   prompts:
   - Language: English (or your preference).
   - Keyboard layout: default is fine.
   - **Network connections**: leave default (DHCP via the NAT adapter —
     see Step 5). It should show an IP like `10.0.2.15`.
   - **Proxy**: leave blank.
   - **Mirror**: leave default (archive.ubuntu.com).
   - **Storage**: "Use an entire disk" (the 40 GB virtual disk) — default
     LVM partitioning is fine for this VM.
   - **Profile setup**: pick a username (e.g. `btcintel`) and a password.
     Write the password down — you'll need it for every `sudo` command.
   - **SSH setup**: **check "Install OpenSSH server"** — this lets you SSH
     in from the Windows host instead of using the VirtualBox console
     window, which is much more comfortable to work in.
   - **Featured server snaps**: skip all of these (leave unchecked) — none
     are needed for Tor/Splash/Python.
3. Installation runs, then prompts to reboot. Select **Reboot Now**. If it
   complains about removing the install medium, just press Enter — go to
   VirtualBox Settings → Storage and remove the ISO from the optical drive
   if it doesn't unmount itself.
4. Log in with the username/password you set.

---

## Step 5 — Networking: which adapter mode, and why

VirtualBox offers several network adapter modes. Here's what each means in
plain English, and which one to use:

- **NAT** (what we use): the VM gets its own private IP (something like
  `10.0.2.15`) behind a virtual router that VirtualBox runs for you. The
  VM can reach the internet (so Tor works fine), but nothing on your
  Windows host's real network can see the VM directly — and nothing
  outside your laptop can see it either. To reach something *inside* the
  VM from Windows (like SSH), you set up a **port forward** (next step).
  This is the right choice here: the crawler doesn't need to be reachable
  from anywhere except your own Windows host.
- **NAT Network**: same idea as NAT but lets *multiple* VMs talk to each
  other through a shared virtual switch. Unnecessary — we only have one VM.
- **Bridged**: makes the VM appear as its own device on your real Wi-Fi/
  Ethernet network, with its own IP from your router. This would expose
  the VM (and whatever it's doing) to your home network and possibly to
  whatever network you're demoing on (e.g. a shared venue Wi-Fi) — more
  exposure than this VM needs.
- **Host-only**: the VM can talk to the Windows host but NOT to the
  internet at all. This would break Tor entirely, so it's wrong here.

**Use NAT** (it's the VirtualBox default for a new VM's first adapter, so
you likely don't need to change anything).

### Setting up the SSH port forward

[Windows: VirtualBox GUI]
1. Shut down the VM if it's running (`sudo poweroff` inside the VM, or
   close the window and choose "send shutdown signal").
2. Select the VM → **Settings** → **Network** → Adapter 1 → confirm
   "Attached to: NAT" → click **Port Forwarding**.
3. Add a rule: Name `ssh`, Protocol `TCP`, Host IP *(leave blank)*,
   Host Port `2222`, Guest IP *(leave blank)*, Guest Port `22`.
4. Click OK, OK. Start the VM again.

[Windows cmd/PowerShell — on the host]
```
ssh btcintel@127.0.0.1 -p 2222
```
This SSHes into the VM from a normal Windows terminal — no VirtualBox
console window needed for day-to-day work.

---

## Step 6 — Take the clean snapshot BEFORE installing anything else

This is the "blast shield" restore point: if anything inside the VM
behaves unexpectedly, you revert to this snapshot in under two minutes and
the VM is back to a known-clean state, with zero effect on your host.

[Windows cmd/PowerShell — VBoxManage is installed alongside VirtualBox and
added to PATH automatically; if `VBoxManage` isn't recognized, restart
your terminal or use the full path
`"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"`]
```
VBoxManage snapshot btcintel-crawler take clean_base --description "Fresh Ubuntu 24.04 Server install, nothing else installed yet"
```

To restore this snapshot later if needed:
```
VBoxManage controlvm btcintel-crawler poweroff
VBoxManage snapshot btcintel-crawler restore clean_base
```

(This is the VBoxManage equivalent of the original design's
`virsh snapshot-revert btcintel-crawler clean_base`.)

---

## Step 7 — Install Tor, Docker (for Splash), and the Python crawler-support stack inside the VM

[Inside Ubuntu VM, via SSH from Step 5]
```bash
sudo apt update && sudo apt upgrade -y

# Tor
sudo apt install -y tor
sudo systemctl enable --now tor
# Verify Tor is listening on its SOCKS5 port:
ss -tlnp | grep 9050
# Expect a line showing 127.0.0.1:9050 LISTEN

# Docker (for the Splash JS-rendering container)
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Log out and back in (or `newgrp docker`) for the group change to apply

# Splash, routed through the VM's local Tor SOCKS5 proxy
docker pull scrapinghub/splash
docker run -d --name splash -p 8050:8050 scrapinghub/splash \
  --proxy-profiles-path /etc/splash/proxy-profiles

# Python 3 + pip for any local processing scripts you run inside the VM
sudo apt install -y python3 python3-pip python3-venv
```

Verify Tor is actually proxying traffic (this confirms the SOCKS5 proxy
works, without fetching any .onion content — it just checks your own
exit-node IP via Tor's own check service):
```bash
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
```
Expect a JSON response like `{"IsTor":true,"IP":"<exit node ip>"}`.

---

## What this VM is — and isn't — used for in this build

This repo does not ship a live dark-web crawler (see README "Dark web
data" section for the full reasoning). The Tor/Splash stack above is kept
here because:
- it's genuinely useful if you ever process .onion-hosted content you have
  independent, legitimate access to and want JS-rendered locally rather
  than relying on a static HTML export, and
- it demonstrates the isolation pattern (VM blast shield) the original
  architecture document correctly emphasizes, which is good practice to
  understand regardless of whether you crawl live.

For populating `dark_web_records`, use `scripts/ingest_archive.py`
against already-downloaded archive content (see README "Dark web data"),
which runs on the Windows host and needs neither this VM nor Tor running.
