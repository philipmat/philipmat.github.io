---
layout: post
title: "TIL: LLM Pricing Calculator"
tags: [til, llm, pricing, tools, tokenization, machine-learning]
snippet: "Estimate LLM costs by entering input, cached, and output token counts and per‑million rates; includes model price comparisons and a GitHub source link."
source_url: https://www.llm-prices.com/
---

> **Summary**
>
> This article describes a web-based LLM pricing calculator that estimates model operation costs based on token usage. Users provide the number of input (prompt) tokens, cached input tokens, and output (completion) tokens along with cost-per-million-token rates for input, cached input, and output; the tool then computes the total cost.
>
> The page also includes a model-pricing table showing prices per million tokens, controls to select or clear models for comparison, and a compare feature. It notes that different models use different tokenizers, so direct token-based price comparisons may not be fully accurate, and provides a link to view the source on GitHub with price update metadata.

Allows you to compare models and there it includes nice explanations like "_1.33x input vs Gemini 2.0 Flash Lite, 1.33x output_".

Can also calculate operation pricing if the number of input and output (and cached) tokens are known.

Source: [LLM Pricing Calculator](https://www.llm-prices.com/)
