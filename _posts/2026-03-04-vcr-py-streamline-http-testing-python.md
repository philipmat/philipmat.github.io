---
layout: post
title: "TIL: VCR.py -- records and replays HTTP calls for testing"
tags: [til, python, testing, http, development]
snippet: "Discover how VCR.py can simplify and speed up your HTTP testing by recording and replaying HTTP interactions."
source_url: https://vcrpy.readthedocs.io/en/latest/
---

> **Summary**
>
> VCR.py is a Python library inspired by Ruby's VCR, which simplifies and accelerates testing that involves HTTP requests. VCR.py records HTTP interactions the first time they occur and saves them in a 'cassette' file. On subsequent test runs, it replays these interactions, eliminating the need for actual HTTP traffic. This approach allows for offline testing, ensures deterministic test results, and speeds up test execution. If the API changes, simply delete the cassette files, and VCR.py will record new interactions, keeping tests up-to-date.

[`pytest-recording`](https://github.com/kiwicom/pytest-recording) plugs into `pytest` to create re-usable API-calling tests.

[scotch](https://github.com/mleech/scotch) and [Betamax.NET](https://github.com/mfloryan/Betamax.Net) are the VCR.py .NET alternatives, neither of which have been updated in a few years.

Source: [VCR.py -- records and replays HTTP calls for testing](https://vcrpy.readthedocs.io/en/latest/)
