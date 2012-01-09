---
title: Match Is Sometimes Exec
layout: post
has_tldr: yes
---

In my mind, JavaScript's [`string.match`][match] and [`regexp.exec`][exec] have always been similar. Sure, `exec` might give you a tad more info on matches, but at least they would *both* support matches.

I was a bit surprised when this code:

{% highlight javascript %}
inputPhrase = "My phone number is 281-555-2134, not 281-555-1234."
re = /(\d{3})[^\d]?(\d{3})[^\d](\d{4})/gi;
console.log("match:", inputPhrase.match(re))
console.log(" exec:", re.exec(inputPhrase))
{% endhighlight %}

Produces the following output:

    match: [ '281-555-2134', '281-555-1234' ]
     exec: [ '281-555-2134', '281', '555', '2134',
             index: 19, input: 'My phone number is 281-555-2134.' ] 

What was the unexpected part? `match` ignored my groups; notice that `exec` printed the whole match (I'll refer to this from now on a **Match object**), <samp>281-555-2134</samp>, and it also printed the groups I had so craftly set up. 

Now, because you're not illiterate and/or lazy like me, you'll immediately point out this fragment in the [`string.match`][match] documentation:

> If the regular expression does not include the `g` flag, returns the same result as [`regexp.exec(string)`][exec].
> 
> If the regular expression includes the `g` flag, the method returns an `Array` containing all matches.

And that's true. Take out the `g` (the *global* specifier) and the output now reads:

    match: [ '281-555-2134', '281', '555', '2134',
             index: 19, input: 'My phone number is 281-555-2134, not 281-555-1234.' ]  
    exec : [ '281-555-2134', '281', '555', '2134',
             index: 19, input: 'My phone number is 281-555-2134, not 281-555-1234.' ]  

From my perspective, as a developer, this is inconsistent.

I would've preferred that `string.match` either returns all Match objects or that it sticks to simple matches. In a different language, for the same method to return an `Array` in one case and essentially a `Dictionary` in another case would have been quite unacceptable.

That may be so, but I was still curious as to origins of this behavior. For that, I turned to the source: the [ECMA-262 (pdf)](http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-262.pdf) Standard, aka the "[ECMAScript](http://en.wikipedia.org/wiki/ECMAScript) Language Specification", 5th Edition.

Turns out that this behavior is required by the stardard. To translate in slightly more human terms, the standard (*Section 15.5.4.10 String.prototype.match (regexp)*, page 144-145) says that calling `inputPhrase.match(re)`:

1. Without the `g` specifier return the result of calling `re.exec(inputPhrase)`
2. When `g` is present
    1. start looping over `re.exec(inputPhrase)`;
        1. get each Match object ;
        2. collect each `match[0]` into an `Array`;
        3. loop until there are no more matches;
    2. return the collection array.


<A name="tldr"> </A>

## Conclusion

When called *without* the `/g` option, [`string.match`][match] behaves exactly like [`RegExp.exec`][exec]: it returns one (the first) descriptive match at the time and relies on you calling it multiple times to retrieve more matches. 

But include the global option and `string.match` changes to return an array of all the matches, but instead of the actual descriptive matches you get the first entry of each, which is the "overall match".


----
Notes:

* group backtracking
* replace





[match]: https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/String/match
[exec]: https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/RegExp/exec 
