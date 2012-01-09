---
title: Conditional console.log
layout: post
---

The console is a wonderful thing. You should read the **CSS Ninja**'s [Getting fancy with the console](http://www.thecssninja.com/javascript/console) to find out how cool it is (Hint: it is really cool!)

One of the things that annoy me about the console is that in some browsers, such as Internet Explorer 8, `console.log` tends to throw an error unless you have the **Developer Tools** window running. I'm 47.5% sure it throws errors in Firefox too if you don't have Firebug installed. 

Of course, being a smarter developer than me, you always test for undefined values, so you probably write code like this all over the place:

{% highlight javascript %}
if (typeof(console) != undefined)
	console.log("Text of node(%d)=%s", nodeIndex, node.innerText);

{% endhighlight %}

But that's too long for me because I am a lazy developer. What I want to write is:
{% highlight javascript %}
log("Text of node(%d)=%s", nodeIndex, node.innerText);
{% endhighlight %}

Furthermore, if you write a browser extension, like [I did][/projects/highlighter.html], you might consider having a setting that toggles logging mode on/off. After all, if you're a developer, it's quite annoying to try to debug something in the console window and have another script or extension spew, trickle, or even just spit text you are not interested in. Here's the log function I use for [Highlighter](/projects/highlighter.html):

{% highlight javascript %}
function log() {
  if (SETTING['debug'] && typeof(console) != undefined)
    console.log.apply(console, arguments);
}
{% endhighlight %} 

Using `console.log.apply(console, arguments)` transfers all the arguments passed on to `log` to `console.log`. That allow me to use all the fancy string formatting that `console.log` is capable of with my own fuction.
