---
layout: post
title: "TIL: \"output-competence decoupling\""
tags: [til, ai, agentic-ai, automation, best-practices, tools]
snippet: "Learned the term 'output-competence decoupling': AI lets novices produce expert-looking output without corresponding judgment, creating risks—verify model outputs and don't accept cheap agreement."
---

I learned of this term from [a thoughtful essay](https://nooneshappy.com/article/appearing-productive-in-the-workplace/) from _No One's Happy_ that examines the flood of AI in the workplace from within, and also without.

> Generative AI can produce work that looks expert without being expert, and the failure arrives in two shapes. The first is when novices in a field are able to produce work that resembles what their seniors produce, faster or more advanced than their judgment. The second is when people generate artifacts in disciplines they were never trained in. The two failures look similar from a distance and are not the same. Research has mostly measured the first. The second is what it is missing, and in my experience it is the riskier of the two.

The term for this new challenge, _"output-competence decoupling"_ comes from a paper by Christopher Koch, called [_Beyond the Steeper Curve: AI-Mediated Metacognitive Decoupling and the Limits of the Dunning-Kruger Metaphor_](https://arxiv.org/html/2603.29681):

> AI assistance introduces a third variable between competence and self-assessment: observable output. In classical task settings without tools, output closely tracks competence. An essay written by a novice typically reads like a novice essay. Under AI assistance, a novice can produce output indistinguishable from an expert’s—not because their competence has risen to that level, but because the competence partially resides in the system. This output-competence decoupling is the starting point of the model developed in this paper.

The essay contains veiled anecdotes that us, in the industry, have either already encountered, or will likely run against:

- **Thinking tool=solution**:

> [...] account directors and go-to-market leads who arrive with AI-generated projects and argue them. What they are proposing, in most cases, is a dashboard or website that displays the status of a process that is not ready to be automated, built to track a workflow that does not yet warrant tracking. The tool has not solved a problem; it has driven its user to identify a problem worth solving, outlined an architecture for the solution, and produced enough material — diagrams, schemas, interface mockups — that the user arrives in the room convinced the work is real. 

- **Driving beyond competence**

> People who cannot write code are building software. People who have never designed a data system are designing data systems.

These can seem like positive in absence of introspection. An maybe in a lot of cases that is good enough. When it's not:

> He could not, when asked, explain how any of it actually worked. The work was wrong from the first day. The schemas, and more importantly the objectives, were wrong in a way that would have been obvious to anyone with two years in the field.

> The person, in the transaction, becomes a kind of conduit, capable of routing the output to a recipient and incapable of evaluating it on the way through.

- **Doing the work is learning**. This bears echoes of Thomas Edison's observation that learning what not to build is as important as learning what to build; of "success teaches you little, failures teach a lot more".

> The skills of producing work and judging it were deliberately distinct, but accomplishing the work itself used to teach the judgment.

> The architectural critique that used to come from someone who was taught, or who had built and broken three of these before now comes from a model with no embodied memory of building or breaking anything. The slowness was not a tax on the real work; the slowness was the real work. It was how the work got good, and how the people producing the work got good.

- **Volume wins** - a variation of frequency bias and scents of [Goodhart's Law](https://en.wikipedia.org/wiki/Goodhart%27s_law)

> Requirements documents that were once a page are now twelve. Status updates that were once three sentences are now bulleted summaries of bulleted summaries. Retrospective notes, post-incident reports, design memos, kickoff decks: every artifact that can be elongated is, by people who do not read what they produce, for readers who do not read what they receive.

In a world where we track metrics obsessively, and where volume is easier to measure and judge than quality, volume wins:

> The cost of producing a document has fallen to nearly zero; the cost of reading one has not, and is in fact rising, because the reader must now sift the synthetic context for whatever the document was originally about.

I'm betting quite a few of us have encounter a situation where some person up- or side-the-chain drops a load of AI slop and walk away satisfied they have solved the problem _and_ did most of the work too.

I like one of his recommendations at the end because it's simple and simple rules are easy to follow.

> Use the tool where you can verify precisely what it produces. Never ask a model for confirmation; the tool agrees with everyone, and an agreement that costs the agreer nothing is worth nothing.
