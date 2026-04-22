---
layout: post
title: "Getting `fnm` to clean up its auto-links"
tags: [til, fnm, terminal, macos, tools, npm, development]
snippet: "Automatically remove fnm's per-shell symlinks by using $FNM_MULTISHELL_PATH and a trap EXIT function in zsh/bash to avoid thousands of leftover links."
---

[fnm](https://github.com/Schniz/fnm) is a fantastically fast `node` manager, which make it a pleasure to use over `nvm`.

_fnm_ handles its own `node` versions and it observes `.node-version` files in folder, automatically installing/loading the proper node version.

Part of how it does that:

1. It keeps a user-global installation in `$HOME/Library/Application\ Support/fnm`, and it's where it stores the various `node` versions installed by the user.
2. It creates links to those version in `$HOME/.local/state/fnm_multishells`, one link per shell.

The side-effect of (2) is that every time you open a shell, a new link is created. And `fnm` does not clean up when the shell exits. This is by design -- so that different shells can have different `node` versions.  
No big deal, but these links can accumulate over time. When I cleaned up my `fnm_multishells` I had some 3k links in there.

You can clean these up periodically, or you can set a `trap EXIT` function in `zsh` and `bash` to clean it up. Luckily, `fnm` uses the `$FNM_MULTISHELL_PATH` to point to the exact sub-folder where the links are created.

Add this to your `.zshrc` to clean up after `fnm`.

```zsh
# fnm creates a bunch of links into $FNM_MULTISHELL_PATH = ~/.local/state/fnm_multishells
# one link per shell instance and it never cleans them up
# this function attempts to do that on shell exit
cleanup_fnm() {
  if [[ -n "$FNM_MULTISHELL_PATH" && -d "$FNM_MULTISHELL_PATH" ]]; then
    rm -rf "$FNM_MULTISHELL_PATH"
  fi
}
trap cleanup_fnm EXIT
```
