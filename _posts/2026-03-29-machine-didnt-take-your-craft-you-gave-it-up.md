---
layout: post
title: "\"The machine didn't take your craft. You gave it up.\" -- David Abram"
tags: [til, ai, llm, development, best-practices]
snippet: "David Abram argues LLMs shift where problems are solved—typing code is incidental; the real value remains system understanding, judgment, and choosing what should exist."
---

It's a bit of a [long essay by David Abram](https://www.davidabram.dev/musings/the-machine-didnt-take-your-craft/) in which he argues that LLMs shifted where problems are solved, much the way we shifted to high-level languages or compiler.


> I have been doing this for years, and the hardest parts of the job were never about typing out code. I have always struggled most with understanding systems, debugging things that made no sense, designing architectures that wouldn't collapse under heavy load, and making decisions that would save months of pain later.
> 
> None of these problems can be solved LLMs. They can suggest code, help with boilerplate, sometimes can act as a sounding board. But they don't understand the system, they don't carry context in their "minds", and they certianly _[sic]_ don't know why a decision is right or wrong.

I think that's a solid argument.  
However, at another level, code is a measurable output, while knowledge is not.

I have seen product owners/managers being mistaken about their level of "understanding the system" and think that with the help of an AI agent that "understanding" is trivial to transfer into some output (code).

> And the most importantly, they don't choose. That part is still yours. The real work of software development, the part that makes someone valuable, is knowing what should exist in the first place, and why.

Also fully agree with this, though I didn't quite see it bare in practice in any environment. If that were true in the workforce, we would see a lot higher value assigned to long-timers who might have that knowledge, but are not interested in climbing up the ladder.  
Based on my personal experience, "seniority" is more closely associated with demonstrating forward-looking coding and architectural skills rather than knowledge of the existing systems (and the choices made to get there); those tend to be mere by-products or "nice to haves".

> If you reduce yourself to "the one who types code," then yes, you should feel obsolete. But don't fool yourself any further: typing code that was never the essence of the craft.

This is a long standing argument that the "code" is an incidental side-product of software development; the main goal is satisfying product requirements. (And, cynically but no less true, in enterprise environments is about _making your boss look good_.)

> The real danger is that people stop thinking. The actual trap is engineers letting the tool carry the cognitive load they were meant to build -- The abdication of reason from within.

I'd argue that we see is a real transfer of "work" from engineers to product builders, the latter which (might) over-estimate their knowledge, and conclude they have no need of the former.

To take it one step further: if the decisions that built a system are encoded in some documentation -- including product decision, architectural decisions, etc -- and and LLM can look at those and the resulted code and explain "everything", then where do the engineers David describes fit in?
