---
title: .Net DI container speed test
layout: post
---

When doing some performance testing recently, I've noticed that one of the hotspots in code was a repeated call to our **Dependency Injection (DI)** aka **Inversion of Control (IoC)** container.

I mostly prefer the constructor flavor of injection, but when [working with legacy code](http://www.amazon.com/Working-Effectively-Legacy-Michael-Feathers/dp/0131177052) the [Service Locator](http://martinfowler.com/articles/injection.html#ADynamicServiceLocator) is a good pattern to use for breaking dependencies and it is one easier to understand by all other participants. 

In my performance testing scenarios the timings of individual queries to our **Service Locator** were insignificant in themselves, but the container was getting queried a lot; that prompted my curiosity about how various DI containers perform the most commont task which is required of them: retrieving objects.

[My tests][gitdi] concerned themselves almost exclusively with the DI speed (memory efficiency was not even a secondary concern and, to be honest, I don't even know how to measure that with any kind of precision).  

In my findings, the numbers tell only a quarter of the story; the rest is told by the *consistent* differences in timings between the containers.

I've limited my testing to the latest version of the six major containers of the .Net world: [Autofac v2.4.5.724][autofac], [Castle.Windsor v2.5.3][castle], [Ninject v2.2.0.0][ninject], [Spring.Net v1.3.1][spring], [StructureMap v2.6.1][smap], and [Microsoft Unity v2.1.0.0][unity]. 

* [Testing methodology](#methodology)
* [Retrieving singletons](#singletons)
* [Transient objects](#transient)
* [Retrieving singletons - loaded containers](#singletons_loaded)
* [Transient objects - loaded containers](#transient_loaded)
* [Conclusion](#tldr)


<A name="methodology"> </A>
## testing methodology

I believe there are two scenarios that can be measured with enough accuracy: retrieving the same instance on each call, i.e. **singleton scope**, and retrieving a new instance on each call aka **transient scope**. All containers allow more advance construction methodes, e.g. single instance per thread or per HTTP request, but I don't have enough confidence in my abilities to come up with a clear scenario that would produce measurements that are a) accurate, b) relevant, and c) somewhat equivalent across containers. However, I think that the story the numbers tell for the **singleton** and **transient** scenarios are somewhat indicative of the other usage scenarios.

Resolving singletons tests the container's raw retrieval speed and its registration internals. Creating new objects on each call tests the container's build plan and the strategies it uses to create objects.

In both cases my program will load and configure all the containers then perform 10 runs of a loop requesting the same object a large number of times (10k and 100k) then average those 10 runs. I will refer to these two as the **10x10k run** and respectively the **10x100k run**. So that's four combinations so far: **singleton 10x10k**, **singleton 10x100k**, **transient 10x10k**, **transient 10x100k**.

I will restart my test virtual machine before each of the four scenarios and then I will run the test program three times. I will post the numbers from both the first and third run from each scenario.

Finally, to put a real world flavor on the test, I will repeat the four test scenarios with the containers loaded with some significant number classes to simulate a container under some load and make 10k and 100k request of a limited number of objects randomly selected. I don't think any container performs any kind of heuristic analysis of the requests with intent to provide a quicker resolution path for those objects requested more/most often, though I wish they did.

I'd like to make a note about variants of a phrase I frequently use: "most containers", "all containers", "almost all containers"; when doing so in 98% of cases I really mean *all containers but* __Spring.Net__, for the latter has a container so awful to configure and work with that I feel sorry for people that have to deal with it.  
Look, I'm not a smart guy and, worse, I'm easily frustrated too, but honestly I have spent more time trying to write the test cases for **Spring.Net** than all the other *five* containers combined. I'm hoping that [Spring.Net CodeConfig][scodeconfig] will bring some degree of sanity to the mess that **Spring.Net** config files are.  
Also *.Net Framework 2.0* has been out for almost 6 - **six!** years and **Spring.Net** still doesn't support generics properly. You can rationalize that any which way you please, but seriously, in 2011 instead of having to write a straightforward `container.Get<IDummy>()` I have to write `(IDummy) container.GetObject( typeof(IDummy).Name )`?! Painful. Too painful. /rant

<A name="singletons"> </A>
## retrieving singletons

I believe this to be the most common case in construction of **DI trees** and it's after all just an optimization of the **transient** scenario. I don't think I need to have an instance of **SalesTaxCalculator** created for each call, I'm better off creating it once per configuration key (e.g. state or country) and storing it as a singleton easily retrievable by that configuration key. Of course, for something like a webservice connection you want the opposite: a new connection on each call.

Retrieving **singletons** is a case of configuring the containers and telling them to store an object once retrieved and created and return the same object on each subsequent call. Here are the results:

<A name="transient"> </A>
## Transient objects
The transient scope is most common with classes that control access to limited resources: database connection, webservice requests, etc. My gut feeling is that in most cases these type of classes will have either creation or use costs that outweigh the container's, but nevertheless I thought it makes for an interesting test case because it tells us how efficient each container's build plan is. I don't expect any of the containers to use [the very slow][ayendecreation] `Activator.CreateInstance`, but there are various strategies that can be employed to create new objects.

As the test focuses on object creation I chose the route of constructing an object with one constant parameter, rather than the more complex but more realistic case of a class that gets injected with other dependencies, which themselves might be dynamically resolved at that point.

The results are, as expected, a good deal slower than the **singleton scope** scenario:



<A name="singletons_loaded"> </A>
## Retrieving singletons - loaded containers

Based on what I've seen of their respective source code, each container takes different approaches to storing class registration and as such when a resolution is performed each will use a different strategy to either retrieve an existing instance or create a new one. I believe this test will attempt to show how well each container's approach scales when the container has a good deal of objects registered and created.
 
I don't know what is a realistic number of classes that a container would be saddled with, so I've picked pretty numbers. I'll load the container with 666 classes registered for 222 interfaces (two discriminators for each interface), and pre-instantiate a bit over 80% of those classes, let's say 550 classes. I will then make 10k and respectively 100k random requests to resolve those 80%.


<A name="transient_loaded"> </A>
## Transient objects - loaded containers

This is the same cases as above, except no classes are pre-instantiated and the 10k and 100k requests are across the entire 666 spectrum.


<A name="tldr"> </A>
## conclusion

Syntactically all containers are roughly the same - one can easily move from one to the next with little training, the only *significant* differentiator that I observed was elegance of configuration, but that's hardly something 


[gitdi]: 
[autofac]:
[castle]:
[ninject]:
[spring]:
[scodeconfig]:https://github.com/SpringSource/spring-net-codeconfig
[smap]:
[unity]:
[ayendecreation]: http://ayende.com/blog/3167/creating-objects-perf-implications
