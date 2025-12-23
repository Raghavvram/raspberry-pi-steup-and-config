import os
import subprocess

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def move_and_rename_file(source, destination):
    os.rename(source, destination)

def create_readme():
    content = """# Raspberry Pi Setup and Configuration

This repository contains a collection of guides for setting up and configuring a Raspberry Pi for various purposes.

## Guides

The following guides are available in the `raspberry_pi_setup` directory:

-   [`disable_wlan.md`](raspberry_pi_setup/disable_wlan.md): A guide on how to permanently disable the wlan0 interface on a Raspberry Pi.
-   [`komodo_setup.md`](raspberry_pi_setup/komodo_setup.md): A guide on how to set up Komodo using Docker.
-   [`samba_setup_external_usb.md`](raspberry_pi_setup/samba_setup_external_usb.md): A comprehensive guide on setting up a Samba share on a Raspberry Pi with an external USB device.
-   [`swap_memory_setup.md`](raspberry_pi_setup/swap_memory_setup.md): A guide on how to increase the swap memory on a Raspberry Pi.
-   [`troubleshooting.md`](raspberry_pi_setup/troubleshooting.md): A guide for troubleshooting samba setup.
"""
    with open("README.md", "w") as f:
        f.write(content)

def main():
    create_directory("raspberry_pi_setup")

    files_to_move = {
        "disable-wlan0-on-pi.md": "raspberry_pi_setup/disable_wlan.md",
        "komodo-setup-file.md": "raspberry_pi_setup/komodo_setup.md",
        "setup-samba-external-usb -device-in-pi.md": "raspberry_pi_setup/samba_setup_external_usb.md",
        "swap-memory-setup.md": "raspberry_pi_setup/swap_memory_setup.md",
    }

    for source, destination in files_to_move.items():
        if os.path.exists(source):
            move_and_rename_file(source, destination)

    create_readme()

    # Create troubleshooting.md
    troubleshooting_content = """# Samba Troubleshooting

This document provides troubleshooting steps for the Samba setup.

## Windows 10/11 Guest Access Problems

Even with a correct guest-only Samba config, Windows 10/11 still prompts for credentials due to security defaults that block “insecure guest logons” over SMB2/3.

### Enable insecure guest logons via PowerShell

On the Windows client (run **as Administrator**):

```powershell
Set-SmbClientConfiguration -EnableInsecureGuestLogons $true -Force
```

Then clear any cached SMB sessions:

```powershell
net use * /delete /y
```

Re-open in Explorer:

```text
\\192.168.0.215\sata
```

### Optional: enable via Group Policy (Pro/Enterprise)

If Group Policy Editor is available:

1.  Run `gpedit.msc`.
2.  Navigate to:

    `Computer Configuration → Administrative Templates → Network → Lanman Workstation`.

3.  Set **Enable insecure guest logons** to **Enabled**.

After changing, again clear sessions (`net use * /delete /y`) and reconnect.

Once this policy/setting is enabled, Windows will connect to the `sata` share without asking for any username or password.
"""
    with open("raspberry_pi_setup/troubleshooting.md", "w") as f:
        f.write(troubleshooting_content)

    print("Setup complete!")

if __name__ == "__main__":
    main()
