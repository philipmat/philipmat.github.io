---
layout: post
title: "Removing the menu icons in macOS Tahoe"
tags: [til, macos, mac, terminal]
snippet: "Run defaults write -g NSMenuEnableActionImages -bool NO and restart to hide most macOS menu icons; some apps (e.g. Finder, Firefox) keep icons and iTerm2 may not yet respect it."
---

Saw this advice from multiple sources, most pointing to [@stroughtonsmith](https://mastodon.social/@stroughtonsmith/116262411548746327):

`defaults write -g NSMenuEnableActionImages -bool NO` followed by a computer restart results in the menu icons being hidden, except for when apps specifically overwrite this settings.

> It even preserves the couple of instances you do want icons, like for window zoom/resize.

Firefox, for example, keeps icons for the _Bookmarks_ menu entries. Finder keeps the icons for the specific locations under the _Go_ menu.  
iTerm2 doesn't seem to be observing this setting as of v3.6.9, but [a fix is in the works](https://gitlab.com/gnachman/iterm2/-/work_items/12780).
