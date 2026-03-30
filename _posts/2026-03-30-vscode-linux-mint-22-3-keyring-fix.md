---
layout: post
title: "TIL: Getting VS Code running on (fresh) Linux Mint v22.3"
tags: [til, linux-mint, tools, development, vs-code]
snippet: "On fresh Linux Mint 22.3, VS Code login fails due to missing libsecret/gnome-keyring; install libsecret packages and create/unlock the 'Login' keyring (restart gnome-keyring or the system if needed)."
---

The first step of Visual Studio Code install is deceptively simple: download the `.deb` file, double-click to open.

Trying to log into accounts causes a notification/error:

> You're running in a GNOME environment but the OS keyring is not available for encryption. Ensure you have gnome-keyring or another libsecret compatible implementation installed and running.

The [keyring troubleshooting page](https://code.visualstudio.com/docs/configure/settings-sync#_troubleshooting-keychain-issues) provides some clues but it's a bit clumsy to figure it out.

1. **Problem 1**: `libsecret` is not installed on a fresh Linux Mint v22.3.  
   **Solution**: install with `apt install libsecret-1-0 libsecret-1-dev libsecret-tools` (not sure all of them are required).
2. A bit buried in the docs is this bit: "_and ensure the default keyring (usually referred to as Login keyring) is unlocked_".  
  **Problem 2**: there was no "Login" password keyring visible in Seahorse (the keyring manager).  
  **Solution**: First, it's very possible a restart (of `gnome-keyring`) after installing `libsecret` might have auto-fixed this issue, but I went ahead to try to create that and failed: the UI was not showing the new keyring, so restart was in the cards anyway.  
  After restarting the computer, I was able to create the new `Login` password keyring and Visual Studio Code worked without any issues. It didn't even require the `--password-store="gnome-keyring"` argument or startup setting.

Also thanks to [this SO answer](https://stackoverflow.com/a/79057899) and [this one too](https://askubuntu.com/a/1557374).
