---
layout: post
title: "TIL: lnav - a fast log viewer with remote capabilities"
tags: [til, log-viewer, terminal, performance, sqlite]
snippet: "lnav is a terminal log viewer that merges, tails, searches, and queries logs with automatic format detection and high performance—no server or setup required."
source_url: https://lnav.org/
---

A TUI for log files.

> **Summary**
>
> lnav is a terminal-based log file viewer that lets you merge, tail, search, filter, and query log files without any server or complex setup. It automatically detects file formats, unpacks compressed files on the fly, and provides online help and operation previews to simplify use.
>
> Designed for performance, lnav can outperform standard terminal tools when processing large logs and exposes a SQLite interface for advanced querying. The project includes an introductory video and documentation to help users get started.

The [remote-host tailing feature](https://lnav.org/2021/05/03/tailing-remote-files.html) is kind of cool. 

> When lnav accesses a remote host, it transfers an agent (called the “tailer”) to the host to handle file system requests from lnav. The agent is an [αcτµαlly pδrταblε εxεcµταblε](https://justine.lol/ape.html) that should run on most X86 Operating Systems. The agent will monitor the files of interest and synchronize their contents back to the host machine.
>
> The only setup required is to ensure the machines can be accessed via SSH without any interaction, meaning the host key must have been previously accepted and public key authentication configured.

Source: [TIL: lnav - a fast log viewer with remote capabilities](https://lnav.org/)
