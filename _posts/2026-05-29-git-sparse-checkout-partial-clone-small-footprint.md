---
layout: post
title: "TIL: git sparse-checkout"
tags: [til, git, development, tools]
snippet: "Use git partial clone (--filter=blob:none) with sparse-checkout to clone large repos without downloading blobs and materialize only the directories you need, keeping files updatable."
---

This is useful in having both a limited footprint from a repo, while also the ability to update.

I use this to keep a library of AI skills up-to-date, without having to copy them manually:


```sh
$ cd ~/.agents/
$ git clone --filter=blob:none --sparse https://github.com/anthropics/skills anthropics-skills
$ cd anthropics-skills
$ git sparse-checkout set skills/frontend-design
$ ln -s ~/.agents/anthropics-skills/skills/frontend-design ~/.agents/skills/frontend-design
```

- `--filter=blob:none`  
Tells Git to clone without downloading any file contents (blobs) upfront. You get the full commit history and directory tree metadata, but actual file data is fetched lazily — only when you check out or access a file. This makes the initial clone much faster for large repos.
- `--sparse`  
Enables sparse checkout mode, which means Git will only populate your working directory with a subset of files instead of everything in the repo.
- `git sparse-checkout set skills/frontend-design`  
Configures which paths to materialize in the working directory. After this command, only the `skills/frontend-design/` directory will appear on disk. Everything else exists in the Git object store but won't be written to your filesystem.

Later on, `git pull` behaves like a normal pull but scoped to what has been materialized.
