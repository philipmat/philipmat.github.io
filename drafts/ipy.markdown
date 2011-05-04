---
title: ipy - completion for python interactive
layout: post
---

Bash has a good degree of command and file completion. I like that. Ruby people are just spoiled with `irb`.

So here's how you do the same for python, when running in *interactive mode*.

First I save the following script to `~/scripts/set_python_interactive.py`:

{% highlight python %}
import rlcompleter, readline                                               
readline.parse_and_bind('tab: complete')
{% endhighlight %}

Then I add an `alias` because I'm very lazy:

{% highlight bash %}
alias ipy='python -i ~/scripts/set_python_interactive.py'
{% endhighlight %}

So finally instead of simply starting with `python`, I start with `ipy`:

{% highlight bash %}
$ ipy
>>> import re
>>> re.<TAB>
re.DEBUG              re.__doc__            re._compile_repl(
re.DOTALL             re.__file__           re._expand(
re.I                  re.__format__(        re._pattern_type(
re.IGNORECASE         re.__getattribute__(  re._pickle(
re.L                  re.__hash__(          re._subx(
re.LOCALE             re.__init__(          re.compile(
...
{% endhighlight %}

Want to know more? Read the [rlcompleter documentation](http://docs.python.org/library/rlcompleter.html). The [readline docs](http://docs.python.org/library/readline.html) are interesting, too.
