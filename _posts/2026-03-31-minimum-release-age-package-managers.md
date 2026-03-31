---
layout: post
title: "TIL: Setting a minimum release age for packages"
tags: [til, security, best-practices, python, macos]
snippet: "Many package managers let you require a minimum package age before installing; examples for npm, pnpm, bun, Python uv, and pip (v26+) with a 7-day shortcut are shown."
---

I [learned](https://news.ycombinator.com/item?id=47582632), in the light of the [axios compromise](https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan) that a good deal of package managers support setting a minimum release age for packages:

```
~/.npmrc
min-release-age=7 # days
ignore-scripts=true

~/Library/Preferences/pnpm/rc
minimum-release-age=10080 # minutes

~/.bunfig.toml
[install]
minimumReleaseAge = 604800 # seconds
```

For Python with `uv` (which by now should be the default):

```
~/.config/uv/uv.toml
exclude-newer = "7 days"
```

Alas, `pip` only supports filtering by date, and _only in version v26.0_ and later, with:  
`pip install --uploaded-prior-to=2026-03-31 SomePackage`.

That is a bit annoying so a shortcut for the 7-day gating would be  
`pip install --uploaded-prior-to=$(date -v-7d -u "+%Y-%m-%d") SomePackage`.
