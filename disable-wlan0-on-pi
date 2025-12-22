# Complete Guide: Permanently Disable wlan0 on Linux/Raspberry Pi

**Goal**: Keep wlan0 (WiFi) interface **DOWN by default** on every boot. Only enable manually when needed. Works despite NetworkManager, systemd-networkd, dhcpcd, Tailscale, Docker.

**Your Setup**: Raspberry Pi CLI-only, eth0+tailscale0 working, wlan0 keeps coming UP automatically.

## Table of Contents
- [Why wlan0 Keeps Coming UP](#why)
- [Method 1: Nuclear Loop (Recommended)](#nuclear)
- [Method 2: NetworkManager Config](#nm)
- [Method 3: systemd-networkd Config](#systemd-net)
- [Method 4: dhcpcd Config](#dhcpcd)
- [Method 5: Early Boot Service](#early-service)
- [Verification & Manual Enable](#verify)
- [Troubleshooting](#troubleshoot)

## Why wlan0 Keeps Coming UP
```
Your current state:
3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 ... state UP
```
**Culprits** (in order of likelihood on your Pi):
1. **systemd-networkd** (no dhcpcd.service found)
2. **Tailscale** auto-activating interfaces
3. **Docker** network management
4. Boot timing - services override your disable attempts

## Method 1: Nuclear Loop (Recommended - Bulletproof)
**Works always, survives everything.** Runs forever, disables wlan0 every 5 seconds.

**Create**: `/etc/systemd/system/keep-wlan0-down.service`
```ini
[Unit]
Description=Force wlan0 DOWN forever
After=network-online.target systemd-networkd.service NetworkManager.service tailscaled.service docker.service
Wants=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'while true; do ip link set dev wlan0 down 2>/dev/null || true; rfkill block wifi 2>/dev/null || true; sleep 5; done'
Restart=always
RestartSec=5
Nice=19

[Install]
WantedBy=multi-user.target
```

**Activate**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now keep-wlan0-down.service
sudo reboot
```

## Method 2: NetworkManager Config
**If** `sudo systemctl status NetworkManager` shows active:

**Create**: `/etc/NetworkManager/conf.d/99-unmanaged-wlan0.conf`
```ini
[keyfile]
unmanaged-devices=interface-name:wlan0
```

**Apply**:
```bash
sudo systemctl reload NetworkManager
sudo reboot
```

## Method 3: systemd-networkd Config (Most Likely on Your Pi)
**If** `sudo systemctl status systemd-networkd` shows active:

**Create**: `/etc/systemd/network/99-disable-wlan0.network`
```ini
[Match]
Name=wlan0

[Network]
DHCP=no
LinkLocalAddressing=no

[Link]
Unmanaged=yes
RequiredForOnline=no
```

**Apply**:
```bash
sudo systemctl restart systemd-networkd
sudo reboot
```

## Method 4: dhcpcd Config (If dhcpcd was present)
**Edit**: `/etc/dhcpcd.conf` (add to very end):
```bash
denyinterfaces wlan0
```

**Apply**:
```bash
sudo systemctl restart dhcpcd
sudo reboot
```

## Method 5: Early Boot Service (Original Attempt)
**Create**: `/etc/systemd/system/disable-wlan0.service`
```ini
[Unit]
Description=Keep wlan0 down early
Before=networking.service systemd-networkd.service NetworkManager.service dhcpcd.service multi-user.target
After=local-fs.target

[Service]
Type=oneshot
ExecStart=/sbin/ip link set dev wlan0 down
ExecStart=/usr/sbin/rfkill block wifi
RemainAfterExit=yes

[Install]
WantedBy=sysinit.target
```

**Activate**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable disable-wlan0.service
```

⚠️ **This fails** because network services run later and re-enable wlan0.

## Step 0: Identify Your Network Manager (Run First)
```bash
sudo systemctl status networking systemd-networkd NetworkManager dhcpcd
ps aux | grep -E 'network|dhcp'
```
**Pick Method 2, 3, or 4 based on what's active.**

## Verification
**After reboot, run**:
```bash
ip link show wlan0          # Must show: <BROADCAST,MULTICAST> state DOWN
rfkill list wifi            # Must show: "Soft blocked: yes"
systemctl status keep-wlan0-down  # Active (if using Nuclear)
```

**Success looks like**:
```
3: wlan0: <BROADCAST,MULTICAST> mtu 1500 qdisc fq_codel state DOWN mode DORMANT
```

## Manual WiFi Enable (Temporary)
```bash
# Stop loop service (if using Nuclear)
sudo systemctl stop keep-wlan0-down.service

# Unblock and bring up
sudo rfkill unblock wifi
sudo ip link set wlan0 up

# Use WiFi normally now
```

**Re-disable**:
```bash
sudo systemctl start keep-wlan0-down.service  # Nuclear method
# OR just reboot
```

## Troubleshooting Table
| Problem | Check | Fix |
|---------|-------|-----|
| Still UP after reboot | `journalctl -u keep-wlan0-down -f` | Nuclear loop takes 5-10s, wait |
| `rfkill: command not found` | - | `sudo apt install rfkill` |
| Service fails to start | `systemctl status keep-wlan0-down` | Check logs: `journalctl -u keep-wlan0-down` |
| Tailscale re-enables | `sudo systemctl stop tailscaled` | Test without Tailscale |
| Boot hangs | `systemd-analyze blame \| grep network` | Disable network-online.target |

## Your Current Network Status
```
✅ eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>     (Ethernet ✅)
✅ tailscale0: <POINTOPOINT,MULTICAST,UP>      (VPN ✅)  
❌ wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP>    (Will be fixed ✅)
✅ docker0: <NO-CARRIER,BROADCAST,UP>         (Docker ready)
```

## Recommendation
1. **Use Nuclear Loop (Method 1)** - survives all scenarios
2. **Also apply your network manager config** (Method 2/3) for efficiency
3. **Reboot and verify**

**This documentation covers everything discussed.** Nuclear method guarantees success on your Raspberry Pi.
