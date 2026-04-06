---
layout: post
title: "TIL: Adding custom wallpaper folders to macOS"
tags: [til, macos, mac, tools, open-source]
snippet: "WallpaperFolderManager is a Swift utility that lets admins programmatically add custom wallpaper folders to macOS System Settings, handling macOS 26’s new containerized config."
source_url: https://bartreardon.github.io/2025/12/04/adding-wallpaper-folders-to-macos-system-settings.html
---

A nice, notarized program, that makes adding a wallpaper folder as easy as `/usr/local/bin/wallpaper-folder add ~/Pictures/Wallpapers`

> [**AI Summary**](https://bartreardon.github.io/2025/12/04/adding-wallpaper-folders-to-macos-system-settings.html)
>
> The article explains how macOS wallpaper folder handling changed in macOS 26 and how that broke simple scripted approaches admins used to add brand or custom wallpaper collections. Previously you could drop images into /Library/Desktop Pictures (which placed them after built-ins) or add a user folder entry in ~/Library/Preferences/com.apple.systempreferences.plist (DSKDesktopPrefPane:UserFolderPaths) using tools like PlistBuddy; those techniques worked across macOS 13–15.
>
> In macOS 26 the wallpaper configuration moved into a container at ~/Library/Containers/com.apple.wallpaper.extension.image/ with embedded plists and a WallpaperAgent daemon, making shell-based edits impractical. To address this, the author created WallpaperFolderManager, a Swift utility/package that generates the required files and encoded plists, restarts cfprefsd and WallpaperAgent, and exposes commands to add, list, and remove wallpaper folders. It’s available as a signed notarized pkg, standalone binary, or Swift package, has options for verbose output and skipping service restarts, and was tested on macOS 15 and 26 (with fallback behavior for 13–15).

Source: [TIL: Adding custom wallpaper folders to macOS](https://bartreardon.github.io/2025/12/04/adding-wallpaper-folders-to-macos-system-settings.html)
