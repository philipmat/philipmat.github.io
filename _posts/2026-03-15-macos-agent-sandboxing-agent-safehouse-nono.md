---
layout: post
title: "Two macOS tools for sandboxing agents"
tags: [til, macos, agentic-ai, security, tools]
snippet: "A brief comparison of two macOS-focused agent sandboxing tools—Agent Safehouse (bash-based) and Nono (Rust, brew-installable, cross-platform)—and pointers to VM/container alternatives."
---

Both [Agent Safehouse](https://agent-safehouse.dev) and [Nono](https://nono.sh/docs/introduction) (get it, no-no?) use macOS sandboxing to execute agents.

## Agent Safehouse

Pull down a self-contained Bash script with `curl`, and drop it in `~/.local/bin`. Run your agent command prefixed with `safehouse`: `safehouse opencode`.  
The tool auto-detects the git root of the working directory, applies a deny-all baseline, and layers on permissions for common toolchains.

## Nono

Same, but installed with `brew`. Then `nono run --profile claude-code -- claude` to run a sandboxed agent.


Nono works on Linux as well, Agent Safehouse is macOS only. Nono is written in Rust, AS is all fish-shell scripting.

Founderland.ai [mentions a few other](https://www.founderland.ai/articles/agent-safehouse-brings-native-sandboxing-to-macos-ai-agents-mmiwmf3f#:~:text=Microsandbox,microVMs): 
> Microsandbox and Agent Harbor lean on VM-level isolation. DevCage and AgentSphere target multi-platform or cloud deployments. Kilntainers gives each agent an ephemeral Linux sandbox via containers or microVMs.

May be worth investigating. It's a fledgling space, so new tools will come and go.
