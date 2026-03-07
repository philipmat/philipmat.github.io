---
layout: post
title: "TIL: How to Audit a Rails Codebase: Legacy App Playbook"
tags: [til, ruby, rails, code-audit, security, legacy]
snippet: "A week-one playbook for auditing legacy Rails apps: interview stakeholders, inspect Gemfile/schema/routes, run security scans first, use SimpleCov zero-coverage as a fear map, and deliver a one-page t"
source_url: https://piechowski.io/post/how-i-audit-a-legacy-rails-codebase/
---

The post has a really strong opener:

> [...] the first week isn’t about reading the code. It’s about reading the signals.
> 
> The client already has opinions about what’s wrong. They’re usually partially right and almost always wrong about _why_. Your job in week one is to separate what looks bad from what’s actually dangerous.

> **Summary**
>
> This guide outlines a practical, week-one playbook for auditing legacy Ruby on Rails applications. Rather than starting in the code, begin by reading the signals: run stakeholder interviews to surface risky areas (deploy frequency, fear zones, blocked features), then form a working thesis by skimming three files—Gemfile, db/schema.rb, and config/routes.rb—to spot dependency duplication, god tables, missing indexes, integer primary-key risks, and architectural routing issues.
>
> After the initial read, prioritize security and dependency scans (bundle audit, Brakeman, bundle outdated) before other tooling. Use SimpleCov zero-coverage files as a “fear map,” measure SLOC and complexity (cloc, RubyCritic), inspect model structure manually and run active_record_doctor and Bullet for DB and N+1 problems, and time the test suite to gauge developer feedback loops. Deliver a concise, single-page triage with prioritized risks and next steps rather than an exhaustive report; AI tools can accelerate repetitive parts of the audit but should complement, not replace, human judgment.

I think the lessons here are well structured and easy to "port" to other frameworks and languages, with appropriate file and tool modifications.

Source: [How to Audit a Rails Codebase: Legacy App Playbook](https://piechowski.io/post/how-i-audit-a-legacy-rails-codebase/)
