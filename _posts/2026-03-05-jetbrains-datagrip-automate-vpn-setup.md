---
layout: post
title: "TIL: Jetbrains DataGrip -- Automatically start VPN connection"
tags: [til, azure, vpn, datagrip, macos, database]
categories: [TIL, Azure, Vpn, Datagrip, Macos, Database]
snippet: "Learn how to automate VPN connections in DataGrip for Azure-hosted databases on macOS."
---

A good security approach when working with Azure-hosted databases is to connect through a VPN tunnel.

This typically involves installing the _Azure VPN Client_ and importing a profile file, and then starting that VPN tunnel before connecting to the database.

On macOS the above creates a system-wide VPN profile, which means it can be started from the command line with:

```sh
scutil --nc start "vpn profile name"
```

Which in turn means that we can have _DataGrip_ automatically start it before opening a connection to the database.

Steps are as following:

1. Locate the name of the VPN profile in macOS _System Settings_ -> _VPN_.  
   Mine is `prod-shared-vnet`.
2. After selecting the desired data source, open the _Options_ panel.
3. Find the _Before connection_ section, click `+` to _Add New Configuration_ and select _Run External Tool_.
4. Create a new tool with an explicit name like "vpn connect", then enter:
   1. **Program**: `scutil`
   2. **Arguments**: `--nc start prod-shared-vnet`, or whatever is your VPN connection name.
5. Make sure the "vpn connect" external tool has been selected before returning to the _Before connection_ section.

**Note**: 
* executing the first query fast enough, before giving the tunnel a chance to fully connect,  might fail with a "Cannot find server" or something similar; retrying works pretty reliably.
* `scutil --nc stop prod-shared-vnet` disconnects the VPN tunnel. It seems to also drop when the computer goes to sleep.

Screenshots below.

*Categories: TIL, Azure, Vpn, Datagrip, Macos, Database*
