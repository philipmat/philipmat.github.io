---
title: DI container speed test
layout: post
---

When doing some performance testing recently, I've noticed that one of the hotspots in code was a repeated call to the Dependency Injection (DI) aka Inversion of Control (IoC) container.

I mostly prefer the constructor flavor of injection, but when [working with legacy code](http://www.amazon.com/Working-Effectively-Legacy-Michael-Feathers/dp/0131177052) the [Service Locator](http://martinfowler.com/articles/injection.html#ADynamicServiceLocator) is a good pattern to use for breaking dependencies and it is one easier to understand by all other participants. 

There's are additional reasons we chose to use a **Service Locator**, but for the purpose of this post lets assume we are querying the DI container and retrieving classes according to their contract.

The timings on individual DI container queries were insignificant in themselves, but it was getting queried a lot; that prompted my curiosity about how various DI containers perform the simple task of retrieving an object.

The numbers in themselves tell only a quarter of the story. The rest is told by the *consistent* differences in timings between the containers.

I planned to start with the barest of cases: container retrieval speed. This implies objects are mostly singletons, which in my mind is the most common case in a great deal of apps. (I don't think you really need to instantiate a StateSalesTaxCalculator on every calculation. Just cache each one on the first call and have them retrieved by some discriminator - state abbreviation, for example.)

But since I had the [code][gitdi] anyway, I thought why not get a bit fancier?

Resolving singletons tests the raw container retrieval speed and its registration internals. Creating new objects each time tests the container's build plan and the strategies it uses to create objects.

I thought about testing the containers with (delegate) factories, but I assume if that is your usage pattern your object construction is probably a good deal more complex and/or time consuming than the container's retrieval speed. 

Finally, to put a real world flavor on the test, I will repeate the two tests above with the containers loaded with classes. I expected the results to be the same - after all, it would mostly show how good the containers' retrieval strategies and build plans are, but OTOH I mind find some unexpected results in there.

* [Testing methodology](#methodology)
* [Retrieving singletons](#singletons)
* [New objects every call](#neweverytime)
* [Retrieving singletons - loaded containers](#singletons_loaded)
* [New objects every call - loaded containers](#neweverytime_loaded)
* [Conclusion](#tldr)


<A name="tldr"> </A>

## conclusion



[gitdi]: 
