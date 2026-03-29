---
layout: post
title: "TIL: Pairing a Logitech K380 keyboard on Linux Mint"
tags: [til, terminal, tools, github, open-source]
snippet: "Pair a Logitech K380 on Linux Mint by using ValeriaRoyal's script or bluetoothctl — scan for the input-keyboard MAC, trust/pair it, and enter the displayed passkey."
---

The Bluetooth Manager in Linux Mint 22.3 detects the Logitech K380 keyboard, but doesn't display the pairing code, or doesn't display it for long enough (supposedly 10 seconds, but I didn't see it at all).

There are two approaches:

1. The script from [ValeriaRoyal/logitech-k380-bluetooth-linux-fix](https://github.com/ValeriaRoyal/logitech-k380-bluetooth-linux-fix) is the simplest version. Scans for the code and gives you 60 seconds to enter it.  
  I didn't try this one, but if I were to do it again it would be my first option.

2. From this [StackExchange answer](https://unix.stackexchange.com/a/663566) -- using `bluetoothctl`, which comes installed on Linux Mint.

For the latter, the steps are:

```
$ bluetoothctl
Agent registered

[some prompt]# agent on
Agent is already registered

[some prompt]# scan on
Discovery started
....
```

Pay attention in the output for the `input-keyboard` line and get its MAC address. Then turn the scan off and pair the device:

```
[some prompt]# scan off
Discovery stopped
[some prompt]# trust <mac address>
...
[some prompt]# pair <mac address>
pair <mac address>
Attempting to pair with <mac address>
[CHG] Device <mac address> Connected: yes
[Keyboard K380]# [agent] Passkey: 987123
```

Enter the passkey it displays on your keyboard and it should be working!
