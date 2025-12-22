# Overview

This guide documents how to:

- Attach a USB–SATA bridge disk (`14cd:6116 Super Top M6116`) to a Linux host (Raspberry Pi).  
- Mount an existing NTFS volume using `PARTUUID` in `fstab`.  
- Export it over Samba as a share called `sata`.  
- Convert the share to anonymous, full read/write access.  
- Fix Windows 10/11 issues with guest access to SMB shares.[1][2][3][4][5]

***

## 1. Detecting and inspecting the USB–SATA disk

1. Confirm that the USB–SATA bridge is detected:

   ```bash
   lsusb
   ```

   Entry looks like:

   ```
   Bus 001 Device 003: ID 14cd:6116 Super Top M6116 SATA Bridge
   ```


2. List block devices and filesystems:

   ```bash
   lsblk -o NAME,MODEL,SIZE,FSTYPE,MOUNTPOINT
   ```

3. View partition table for `/dev/sda`:

   ```bash
   sudo fdisk -l /dev/sda
   ```

   In this case:

   ```text
   Disk /dev/sda: 931.51 GiB ...
   Disklabel type: dos
   Device     Boot Start        End    Sectors   Size Id Type
   /dev/sda1        2048 1953521663 1953519616 931.5G  7 HPFS/NTFS/exFAT
   ```

   So there is a single NTFS/ExFAT partition `/dev/sda1`.[6][7]

4. `blkid` gave no filesystem UUID initially because of quirks with this bridge and NTFS, but the partition **does** have a `PARTUUID`:

   ```bash
   sudo blkid -s PARTUUID -o value /dev/sda1
   ```

   Output:

   ```text
   c7afc91d-01
   ```

   `PARTUUID` is stable and safe to use in `fstab`.[8][9]

***

## 2. Mounting the NTFS partition

1. Install NTFS‑3G driver:

   ```bash
   sudo apt update
   sudo apt install ntfs-3g
   ```


2. Create a mountpoint:

   ```bash
   sudo mkdir -p /mnt/sata
   ```

3. Mount it once manually:

   ```bash
   sudo mount -t ntfs-3g -o uid=1000,gid=1000 /dev/sda1 /mnt/sata
   ```

   - `uid=1000,gid=1000` maps ownership to the main user account.  
   - Verify with:

     ```bash
     df -h /mnt/sata
     ls /mnt/sata
     ```


4. Make the mount persistent via `fstab` using `PARTUUID`:

   Edit `/etc/fstab`:

   ```bash
   sudo nano /etc/fstab
   ```

   Add:

   ```fstab
   PARTUUID=c7afc91d-01 /mnt/sata ntfs-3g defaults,uid=1000,gid=1000,umask=0022 0 0
   ```

   Then test:

   ```bash
   sudo mount -a
   df -h /mnt/sata
   ```

   `umask=0022` makes directory/files owner-writable, readable by others.[11][10]

***

## 3. Installing and enabling Samba

1. Install Samba on the Pi:

   ```bash
   sudo apt update
   sudo apt install samba
   ```


2. Ensure the service is running:

   ```bash
   sudo systemctl status smbd
   ```

***

## 4. Creating a basic share (auth required)

Initially a share was created in `/etc/samba/smb.conf` using per‑user authentication.

Minimal form:

```ini
[global]
   workgroup = WORKGROUP
   server role = standalone server
   log file = /var/log/samba/log.%m
   max log size = 1000
   logging = file
   panic action = /usr/share/samba/panic-action %d
   obey pam restrictions = yes
   unix password sync = yes
   passwd program = /usr/bin/passwd %u
   passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .
   pam password change = yes
   map to guest = Bad User
   usershare allow guests = yes

[sata]
   path = /mnt/sata
   browseable = yes
   read only = no
   guest ok = no
   valid users = admin
```

Then:

```bash
sudo adduser admin          # if not existing
sudo smbpasswd -a admin     # create Samba account
sudo smbpasswd -e admin
sudo systemctl restart smbd
```

From Windows, connect with `\\PI_IP\sata` and credentials `admin` / Samba password.[12][13]

Problems encountered: Windows could reach the server and prompt for a password but refused authentication; this was later bypassed by moving to a guest‑only model instead of troubleshooting per‑user auth.[14][15]

***

## 5. Converting to fully open guest share

The goal was: **no username/password, read/write for anyone on the LAN.**

### 5.1 Filesystem permissions

To avoid Unix permission issues, the directory on the Pi was relaxed:

```bash
sudo chown -R nobody:nogroup /mnt/sata
sudo chmod -R 777 /mnt/sata
```


### 5.2 Final minimal Samba configuration

`/etc/samba/smb.conf` was simplified to essentially:

```ini
[global]
   workgroup = WORKGROUP
   server role = standalone server
   log file = /var/log/samba/log.%m
   max log size = 1000
   logging = file
   panic action = /usr/share/samba/panic-action %d
   obey pam restrictions = yes
   unix password sync = yes
   passwd program = /usr/bin/passwd %u
   passwd chat = *Enter\snew\s*\spassword:* %n\n *Retype\snew\s*\spassword:* %n\n *password\supdated\ssuccessfully* .
   pam password change = yes
   map to guest = Bad User
   usershare allow guests = yes
   guest account = nobody

[sata]
   path = /mnt/sata
   browseable = yes
   read only = no
   guest ok = yes
   public = yes
   guest only = yes
   force user = nobody
   force group = nogroup
   create mask = 0777
   directory mask = 0777
```

Key points:

- `map to guest = Bad User` maps unknown users to guest.  
- `guest account = nobody` uses the `nobody` Unix user.  
- `guest ok = yes`, `public = yes`, `guest only = yes` make the share anonymous.  
- `force user` / `force group` and masks ensure files are created fully accessible.[4][17][16]

Validate configuration:

```bash
testparm -s
```

Output should show:

```text
[global]
    ...
    map to guest = Bad User
    usershare allow guests = Yes

[sata]
    path = /mnt/sata
    guest ok = Yes
    guest only = Yes
    read only = No
    force user = nobody
    force group = nogroup
    create mask = 0777
    directory mask = 0777
```

Restart Samba:

```bash
sudo systemctl restart smbd nmbd 2>/dev/null || sudo systemctl restart smbd
```


***

## 6. Fixing Windows 10/11 guest access problems

Even with a correct guest‑only Samba config, Windows 10/11 still prompted for credentials due to security defaults that block “insecure guest logons” over SMB2/3.[5][20]

### 6.1 Enable insecure guest logons via PowerShell

On the Windows client (run **as Administrator**):

```powershell
Set-SmbClientConfiguration -EnableInsecureGuestLogons $true -Force
```

Then clear any cached SMB sessions:

```powershell
net use * /delete /y
```

Re‑open in Explorer:

```text
\\192.168.0.215\sata
```


### 6.2 Optional: enable via Group Policy (Pro/Enterprise)

If Group Policy Editor is available:

1. Run `gpedit.msc`.  
2. Navigate to:

   `Computer Configuration → Administrative Templates → Network → Lanman Workstation`.

3. Set **Enable insecure guest logons** to **Enabled**.[22][23]

After changing, again clear sessions (`net use * /delete /y`) and reconnect.

Once this policy/setting is enabled, Windows will connect to the `sata` share without asking for any username or password.[24][25][26]

***

## 7. Final working state (summary checklist)

- USB–SATA disk visible as `/dev/sda` with NTFS partition `/dev/sda1`.  
- `fstab` entry using `PARTUUID=c7afc91d-01` mounts it via `ntfs-3g` at `/mnt/sata`.  
- Ownership and permissions on `/mnt/sata` relaxed to allow guest write access.  
- Samba configuration defines a single `[sata]` share, `guest only = yes`, forcing `nobody`.  
- Samba services (`smbd`/`nmbd`) running and listening on the LAN.  
- Windows 10/11 client has **EnableInsecureGuestLogons** turned on (`Set-SmbClientConfiguration` or Group Policy).  
- Access from Windows: `\\192.168.0.215\sata` opens directly, full read/write, no credentials required.[4][5][3]

This document captures all key technical steps, configuration fragments, and issues that arose in the earlier interaction, in a form you can save as your project documentation or README.
