---
layout: post
title: "TIL: Building a self-updating profile README for GitHub"
tags: [til, github, automation, python, graphql, github-actions]
categories: [TIL, Github, Automation, Python, Graphql, Github Actions]
snippet: "Learn how to create a self-updating GitHub profile README using GitHub Actions and a Python script."
source_url: https://simonwillison.net/2020/Jul/10/self-updating-profile-readme/
---

> **Summary**
>
> Today I learned about a new feature on GitHub that allows you to create a profile README by setting up a repository with the same name as your GitHub account. I used this feature to build a self-updating profile page by implementing a GitHub Action that runs a Python script. This script fetches data from the GitHub GraphQL API, my blog's Atom feed, and my TILs website to update my profile with the latest releases, blog posts, and TILs. This automation is achieved with less than 150 lines of Python code, and it feels satisfying to have a profile that updates itself.

Source: [Building a self-updating profile README for GitHub](https://simonwillison.net/2020/Jul/10/self-updating-profile-readme/)

*Categories: TIL, Github, Automation, Python, Graphql, Github Actions*
