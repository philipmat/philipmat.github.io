---
layout: post
title: "TIL: Fixing no video playing in Firefox on Linux Mint -- broken ring buffer"
tags: [linux-mint, terminal, tools]
snippet: "Browser video on Linux Mint froze because snd_hda_intel CORB timeouts stopped the audio clock; workaround: set options snd_hda_intel single_cmd=1, update-initramfs and reboot."
---

**The problem:** On Linux Mint 22.3 with a Radeon RX 5700 XT (Navi 10) connected via DisplayPort, YouTube videos (and video playback generally) in both Firefox and Chrome would hang indefinitely with a spinning loading cursor — no frame ever rendered, no audio. Interestingly, downloading the same video and playing it locally worked fine, which pointed away from a codec/decode issue and toward something browser-specific.

**The diagnosis:** Hardware video decode (VA-API) checked out fine via `vainfo` — VP9, H.264, and HEVC all showed as supported. Disabling hardware decode, disabling AV1, and even forcing software WebRender rendering didn't fix it, which ruled out the GPU compositor and decode pipeline as the direct cause. 

The real clue came from testing with the video muted: **muting made playback work immediately**.

Browsers sync video playback to the audio clock, so a stalled/broken audio pipeline can leave video frozen on a single frame even though decoding is happening fine in the background (confirmed via visible CPU usage and working frame-seeking in Picture-in-Picture). 

Checking `dmesg | grep -i -E "hdmi|audio|azalia|snd_hda"` revealed the actual root cause: `snd_hda_intel 0000:03:00.1: CORB reset timeout#2, CORBRP = 65535`, repeating continuously — a hardware-level failure in the HD-audio controller's command ring buffer (CORB) that prevented the AMDGPU HDMI/DisplayPort audio codec from ever initializing. This is a known issue class on certain AMD GPU/motherboard/kernel combinations, often tied to PCIe ASPM power-state timing during boot.

**The fix:** Force the `snd_hda_intel` driver to bypass the broken ring buffer by using single-command mode instead. Create `/etc/modprobe.d/alsa-hda-fix.conf` with:

```
options snd_hda_intel single_cmd=1
```

Then run `sudo update-initramfs -u` and reboot. This resolved the CORB timeouts entirely, restored audio over DisplayPort, and — since the video freeze was actually a downstream symptom of the broken audio clock — fixed YouTube/video playback in both browsers as a side effect. If this doesn't work, disabling PCIe ASPM (`pcie_aspm=off` in GRUB kernel parameters) is the next thing to try, as ASPM timing is a common root cause of CORB reset failures.

Thank you, robot (Claude Sonnet 5).
