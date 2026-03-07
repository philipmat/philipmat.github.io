---
layout: post
title: "TIL: PR (anti-) patterns in the world of agentic AI"
tags: [til, agentic-ai, code-review, best-practices, pull-requests]
snippet: "Don’t dump unreviewed agent-generated code in PRs—ensure it works, keep changes small, add context, and include testing evidence so reviewers’ time isn’t wasted."
source_url: https://simonwillison.net/guides/agentic-engineering-patterns/anti-patterns/
---

Simon Willison on [PR (anti-) patterns in the world of agentic AI](https://simonwillison.net/guides/agentic-engineering-patterns/anti-patterns/)

> There are some behaviors that are anti-patterns in our weird new world of agentic engineering.

It's so easy to create AI PR slop in this new world, even on private teams.

> If you open a PR with hundreds (or thousands) of lines of code that an agent produced for you, and you haven't done the work to ensure that code is functional yourself, you are delegating the actual work to other people.

These are good rules for event human-created PRs and these stood out:

> The change is small enough to be reviewed efficiently without inflicting too much additional cognitive load on the reviewer.
> Several small PRs beats one big one [...]
>
> The PR includes additional context to help explain the change. What's the higher level goal that the change serves? [...]
>
> Agents write convincing looking pull request descriptions. You need to review these too!
> It's rude to expect someone else to read text that you haven't read and validated yourself.
