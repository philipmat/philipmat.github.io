---
layout: post
title: "TIL: Essential Claude Code Skills and Commands"
tags: [til, ai, automation, code-review, development]
snippet: "A concise guide to Claude Code’s slash commands vs. skills, and practical uses for built-ins like /simplify, /review, /batch, /loop, /debug, plus handy slash commands such as /compact and /diff."
source_url: https://batsov.com/articles/2026/03/11/essential-claude-code-skills-and-commands/
---

> [**Summary**](https://batsov.com/articles/2026/03/11/essential-claude-code-skills-and-commands/)
>
> The article explains the difference between Claude Code’s built-in slash commands and its prompt-based skills: slash commands are fixed, non-AI operations (like /clear or /model), while skills load instruction files into Claude’s context and can spawn subagents, accept arguments, use tools, and include supporting files and frontmatter. The commands-and-skills systems have been unified under the /slash interface, with .claude/skills/ recommended for new customizations because it supports richer features (templates, dynamic context, subagents, and more).
>
> It then surveys the most useful built-in skills and commands: /simplify (automated code-quality review that spawns parallel reviewers and can auto-fix issues), /review (thorough code/PR review for bugs and edge cases), /batch (decomposes large refactors into parallel worktree agents), /loop (recurring scheduled prompts), /debug (session diagnostics), and /claude-api (loads API reference material). Helpful slash commands covered include /compact (conversation compression), /diff (interactive diff of Claude’s edits), /btw (side questions without polluting context), /copy (copy code to clipboard), and /rewind (undo changes). The piece highlights practical workflows—e.g., run /review for correctness then /simplify for cleanup—and recommends listing available skills with /skills.

Commands/skills I didn't know about, and they seem useful:

> * `/btw` lets you ask a side question without affecting the main conversation context
> * `/simplify` reviews your recently changed files for code reuse opportunities, quality issues, and efficiency improvements – and then fixes them automatically.
> * `/review` gves you a proper code review of your changes – the kind of feedback you’d expect from a thorough pull request review.`  
>   [..] My typical workflow is: make changes, run /review to catch issues, fix anything it flags, then run /simplify to clean things up. 

Also `/copy` to copy code to clipboard, with a selector for multiple changes, and `/rewind` to roll back to a certain point in order to explore a new path.

Source: [Essential Claude Code Skills and Commands](https://batsov.com/articles/2026/03/11/essential-claude-code-skills-and-commands/)
