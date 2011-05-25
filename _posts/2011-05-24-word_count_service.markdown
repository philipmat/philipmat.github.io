---
title: word count service for os x
layout: post
---

I recently needed a quick way to count the words in selected text on a web page. It seemed like an OS X service would be the perfect ticket, moreso since Snow Leopard shows in the Services menu only those services appropriate for the current context.

[Smarter people][df] have [tackled][eoi] this need before, but none of their solutions seemed to work for me, ironically, in Snow Leopard. I suspect that either something changed ever so slightly in AppleScript, or that those scripts were designed to work with a specific utility ([ThisService](http://wafflesoftware.net/thisservice/) - which by the way it seemed pretty awesome) rather than standalone.

Either way, here's my solution:

{% highlight applescript %}
on run {input, parameters}
  display alert "Counted " & (count words of (input as string)) & ¬
    " words." message "The selected text had " & (count characters of (input as string)) & " characters."
  return input
end run
{% endhighlight %}

Here's a screenshot of it counting the words of this post (how self-referential):
![Word Count Screenshot](/media/images/word_count.jpg)

Two quick notes: both [John Gruber][df]'s and [Nima Yousefi][eoi]'s scripts use `on process(_str)` - I had no luck getting that to work and instead I've decided to go with **Automator**'s suggestion of `on run {input, parameters}`. As a result of my choice, it seems I was also required to cast the input to a string (`(input as string)`), otherwise `count words of` would consistently and unwantedly return `0`.

[df]: http://daringfireball.net/2007/01/word_count_script_for_thisservice
[eoi]: http://equinox-of-insanity.com/2008/01/better-word-count-service/
