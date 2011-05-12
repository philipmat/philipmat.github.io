---
title: ipy - completion for python interactive
snippet: Enabling completion for Python in interactive mode.
layout: post
---

Bash has awesome command and file completion. I like that.  Ruby people are just spoiled with **irb**.

Python can do that too.

Completion is handled by the [`rlcompleter` module][rlc], aided by the `readline` library, and it is all set up with two lines of code.

Example:

{% highlight python %}
>>> import rlcompleter, readline
>>> readline.parse_and_bind("tab: complete")
>>> readline. <TAB PRESSED>
readline.__doc__          readline.get_line_buffer(  readline.read_init_file(
readline.__file__         readline.insert_text(      readline.set_completer(
readline.__name__         readline.parse_and_bind(
>>> readline.
{% endhighlight %}

Useful, but you want to have that set up automatically (if you can remember or can be bothered to type those liens every time you start `python`, you have my deepest respects, yet I'm also slightly suspicious of your sanity). You have two options:

1. The [`PYTHONSTARTUP`][PYSU] environment variable, which if pointing to the name of a readable file <q>the Python commands in that file are executed before the first prompt is displayed in interactive mode.</q>
2. Running `python -i [script]`, which will cause the interpreter to remain in interactive mode after evaluating the script specified on the command line. You can use it in combination with an `alias` command.

Start by saving those two lines to a file. I'll call mine `~/.python_init.py`:

{% highlight python %}
import rlcompleter, readline
readline.parse_and_bind("tab: complete")
{% endhighlight %}


**The `PYTHONSTARTUP` route** sets this environment variable in your **personal initialization file**,  `.bashrc` for the bashful of us ([why you want `bashrc` instead of `bash_profile`](http://www.joshstaiger.org/archives/2005/07/bash_profile_vs.html)):

{% highlight bash %}
export PYTHONSTARTUP=~/.python_init.py
{% endhighlight %}

**The `alias` route** defines an alias in your **personal initialization file** for `python -i ~/.python_init.py`:

{% highlight bash %}
alias ipy='python -i ~/.python_init.py'
{% endhighlight %}

Now you can start your **python** interpreter using *50% fewer characters!*:

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


Either works the same, but I would think that `PYTHONSTARTUP`, being a *set and forget* option, would serve you better.


Want to know more? Read the [rlcompleter documentation][rlc]. The [readline docs](http://docs.python.org/library/readline.html) are interesting, too.



[rlc]: http://docs.python.org/library/rlcompleter.html
[PYSU]: http://docs.python.org/using/cmdline.html#envvar-PYTHONSTARTUP

