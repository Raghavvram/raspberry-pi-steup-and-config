# Samba Troubleshooting

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
\192.168.0.215\sata
```

### Optional: enable via Group Policy (Pro/Enterprise)

If Group Policy Editor is available:

1.  Run `gpedit.msc`.
2.  Navigate to:

    `Computer Configuration → Administrative Templates → Network → Lanman Workstation`.

3.  Set **Enable insecure guest logons** to **Enabled**.

After changing, again clear sessions (`net use * /delete /y`) and reconnect.

Once this policy/setting is enabled, Windows will connect to the `sata` share without asking for any username or password.
