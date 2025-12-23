Increasing swap memory on Raspberry Pi from default 2GB zram to 8GB swapfile on SD card involves manual file creation when dphys-swapfile is unavailable.

## System Assessment
Initial state showed 8GB RAM with 2GB zram swap (`/dev/zram0`) and 94GB free on SD card (`/dev/mmcblk0p2`). Large SATA drive (/mnt/sata) available but user preferred SD for 8GB swapfile.

## Step-by-Step Process
- Disabled zram: `sudo swapoff /dev/zram0`
- Created 8GB file: `sudo fallocate -l 8G /swapfile`
- Secured: `sudo chmod 600 /swapfile`
- Formatted: `sudo mkswap /swapfile`
- Activated: `sudo swapon /swapfile`
- Made permanent: Added `/swapfile none swap sw 0 0` to `/etc/fstab`
- Verified: `sudo swapon --show` showed both 8GB `/swapfile` and 2GB zram active

## Final Configuration
```
NAME       TYPE  SIZE  USED  PRIO
/swapfile  file    8G   0B   -2
/dev/zram0 partition 2G   0B  100
```
Total ~10GB swap available. Zram optional—disable permanently via modprobe blacklist if desired.

## Warnings & Best Practices
SD card wear accelerates with swap; migrate to SATA/SSD for production. Monitor: `free -h`, `vmstat 1`. Set `vm.swappiness=10` in `/etc/sysctl.conf` for conservative swapping.
