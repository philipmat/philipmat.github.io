---
layout: post
title: "Rejecting working AI code"
tags: [ai, code-review, best-practices, workplace-dynamics]
snippet: "Practical rules for rejecting AI-generated code: don't accept code you can't explain, that adds unnecessary abstractions, bloats diffs, makes reasoning harder, or trusts output over understanding."
---

Good rules from Vinicius Brasil on [When [to] reject AI code even if it works](https://vinibrasil.com/when-i-reject-ai-code-even-if-it-works/):

> More and more, I reject AI code for the same reasons:
> 
> - I reject AI code when I can’t explain the approach in my own words.
> - I reject AI code when the diff is bigger than the problem.
> - I reject AI code when it introduces abstractions before proving they’re needed.
> - I reject AI code when it works locally but makes the system harder to reason about.
> - I reject AI code when I’m trusting the output more than my understanding.

[Aurornis2 on HN](https://news.ycombinator.com/item?id=48615105) reinforces the abstractions point:

> Even using Fable (while it was briefly available), having it refine a plan, and directing it to make only small incremental changes, I still found reasons to reject its first pass at a lot of work. There was a lot of “You’re right to push back” responses. A lot of incidents where it would creat some giant complex set of abstractions to accomplish something that I could find ways to do much more elegantly and in a more maintainable manner.
> 
> It’s really eye opening to work with these tools on a codebase you know deeply because these problems are everywhere.


[ecshafer](https://news.ycombinator.com/item?id=48615155) points out that rejecting the wrong code is what the correct attitude in software engineering:

> If we rephrased this to "When I reject my coworkers code even if it works" and give the same reasons there would be zero dissent. There is this weird idea that seems to come up with AI that any solution must be good and adequate. Software Engineering is all about rejecting code that works for the right code that works.
