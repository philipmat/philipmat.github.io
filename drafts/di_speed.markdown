---
title: .Net DI container speed test
layout: post
---

When doing some performance testing recently, I've noticed that one of the hotspots in code was a repeated call to our **Dependency Injection (DI)** aka **Inversion of Control (IoC)** container.

<!-- I mostly prefer the constructor flavor of injection, but when [working with legacy code](http://www.amazon.com/Working-Effectively-Legacy-Michael-Feathers/dp/0131177052) the [Service Locator](http://martinfowler.com/articles/injection.html#ADynamicServiceLocator) is a good pattern to use for breaking dependencies and it is one easier to understand by all other participants. -->

In those scenarios the timings of individual queries to our [Service Locator](http://martinfowler.com/articles/injection.html#ADynamicServiceLocator) were insignificant individually, but the container was getting queried a lot which added it added quickly to a notable amount higher up the call chain. That was enough to prompt me to examine how various DI containers perform the most common task which is required of them: retrieving objects.

[My tests][gitdi] concerned themselves almost exclusively with the DI speed (memory efficiency was not even a secondary concern and, to be honest, I don't even know how to measure that with any kind of precision).  

In my findings, the numbers tell only a quarter of the story; the rest is told by the *consistent* differences in timings between the containers. There's also at least one significant surprise, bordering, to be honest, on the brink of WTF?!.

I've limited my testing to the latest version of the six major containers of the .Net world: [Autofac v2.4.5.724][autofac], [Castle.Windsor v2.5.3][castle], [Ninject v2.2.0.0][ninject], [Spring.Net v1.3.1][spring], [StructureMap v2.6.1][smap], and [Microsoft Unity v2.1.0.0][unity]. 


* [Testing methodology](#methodology)
* [Retrieving singletons](#singletons)
* [Transient objects](#transient)
* [Retrieving singletons - loaded containers](#singletons_loaded)
* [Transient objects - loaded containers](#transient_loaded)
* [Conclusion](#tldr)


<A name="methodology"> </A>
## testing methodology

I believe there are two scenarios that can be measured with enough accuracy: retrieving the same instance on each *resolve* call, i.e. **singleton scope**, and retrieving a new instance on each call aka **transient scope**. All containers allow more advance construction methodes, e.g. single instance per thread or per HTTP request, but I don't have enough confidence in my abilities to come up with a clear sequence that would produce measurements that are a) accurate, b) relevant, and c) somewhat equivalent across containers. However, I think the **singleton** and **transient** stories are somewhat indicative of the other usage scenarios.

Resolving singletons tests the container's raw retrieval speed and its registration internals. Creating new objects on each call tests the container's build plan and the strategies it uses to match up objects.

In both cases my program will load and configure all the containers (warm-up) then perform 10 runs of a loop requesting the same object a large number of times (10k and 100k) then average those 10 runs. I will refer to these two as the **10k run** and respectively the **100k run**. So that's four combinations so far: **singleton 10k**, **singleton 100k**, **transient 10k**, **transient 100k**.

I am running this in a virtual machine which I will restart before each of the four scenarios and then I will run the test program three times. I will post the numbers from both the first and third run, but will favor the 3rd run for figures and charts.

Finally, to put a <strike>less fake</strike> real world flavor on the test, I will repeat the four test scenarios with the containers loaded with some significant number classes in order to simulate a container under some presure and make 10k and 100k request of a limited number of objects randomly selected. I don't think any container performs any kind of heuristic analysis of the requests with intent to provide a quicker resolution path for those objects requested more/most often, though I wish they did.

I'd like to make a note about variants of a phrase I frequently use: "most containers", "all containers", "almost all containers"; when doing so in 98% of cases I really mean *all containers but* __Spring.Net__, for the latter has a container so awful to configure and work with that I feel sorry for people that have to deal with it.  
Look, I'm not a smart guy and, worse, I'm easily frustrated too, but honestly I have spent more time trying to write the test cases for **Spring.Net** than all the other *five* containers combined. I'm hoping that [Spring.Net CodeConfig][scodeconfig] will bring some degree of sanity to the mess that **Spring.Net** config files are.  
Also, *.Net Framework 2.0* has been out for almost 6 - **six!** years and **Spring.Net** still doesn't support generics properly. You can rationalize that any which way you please, but seriously, in 2011 instead of having to write a straightforward `container.Get<IDummy>()` I have to write `(IDummy) container.GetObject( typeof(IDummy).Name )`?! Painful. Too painful. /rant

<A name="singletons"> </A>
## retrieving singletons

I believe this to be the most common case in construction of **DI trees** and it's after all just an optimization of the **transient** scenario. I don't think I need to have an instance of **SalesTaxCalculator** created for each call, I'm better off creating it once per configuration key (e.g. state or country) and storing it as a singleton easily retrievable by that configuration key. Of course, for something like a webservice connection you want the opposite: a new connection on each call.

Retrieving **singletons** is a case of configuring the containers and telling them to store an object once retrieved and created and return the same object on each subsequent call. 

    :               10k - 1st  10k - 3rd  100k - 1st  100k - 3rd
    ------------------------------------------------------------
    Autofac                15         14         688         635
    Castle.Windsor         22         23         807         790
    Ninject               123        121       2,616       2,558
    Spring.Net             17         16       1,982       1,935
    StructureMap           21         21         212         205
    Unity                  93         98         992         996

             Min           15         14         212         205
             Max          123        121       2,616       2,558
             Median        22         22         900         893



The median across containers for 10k `Resolve` calls is around 20 milliseconds. **Ninject** is 8.6 times slower than the faster container, **Autofac**, and **Unity** close on its heels at 7x the speed. The 100k run only serves to make the gap more obvious, **StructureMap** takes the crown while **Ninject** clocks in a whooping 12.5x slower. Surprisingly, the second fastest container in the 10k run, **Spring.Net** now is the second slowest (9.4x slower).

<A name="transient"> </A>
## transient objects
The transient scope is most common with classes that control access to limited resources: database connection, webservice requests, etc. My gut feeling is that in most cases these type of classes will have either creation or use costs that outweigh the container's, but nevertheless I thought it makes for an interesting test case because it tells us how efficient each container's build plan is. I don't expect any of the containers to use [the very slow][ayendecreation] `Activator.CreateInstance`, but there are various strategies that can be employed to create new objects.

As the test focuses on object creation I chose the route of constructing an object with one constant parameter, rather than the more complex but more realistic case of a class that gets injected with other dependencies, which themselves might be dynamically resolved at that point.

The results are, as expected, a good deal slower than the **singleton scope** scenario, except for **StructureMap** that captures once more the crown:

    :               10k - 1st  10k - 3rd  100k - 1st  100k - 3rd
    ------------------------------------------------------------
    Autofac                64         64         710         634
    Castle.Windsor         80         80         845         797
    Ninject               255        253       2,575       2,678
    Spring.Net            189        185       1,856       1,874
    StructureMap           21         21         202         192
    Unity                 109         99       1,008         956
    					
             Min           21         21          202        192
             Max          255        253        2,575      2,678
             Median        95         90          927        877


I expected the 100k test to repeat the story of the singleton and to increase 10 times from the 10k figures, yet instead the numbers came close to those of the 100k singleton run, for all containers.
**Ninject** sticks to its guns and manages once more to be 12x slower than the fastest container in the 10k race - **StructureMap**, and almost 14x slower in the 100k run. Worthy mention of suckage: my "friend" **Spring.Net** managed slowness factors of 8.8 and 9.8 relative to **StructureMap**. 

<A name="singletons_loaded"> </A>
## retrieving singletons - loaded containers

Based on what I've seen of their respective source code, each container takes different approaches to storing class registration and as such when a resolution is performed, each container will use a different strategy to either retrieve an existing instance or create a new one. I believe this test will attempt to show how well each container's approach scales when the container has a good deal of objects registered and created. 
 
I don't know what is a realistic number of classes that a container would be saddled with, so I've picked pretty numbers. I'll load the container with 666 classes registered for 222 interfaces (three name discriminators for each interface). I will then make 10k and respectively 100k random requests, pairs of interface/discriminator, to resolve those registrations.

On one hand I would expect the figures to be a bit slower, but not by much. The containers should have efficient ways to sift through the registrations to find the proper resolutions.


    :               10k - 1st  10k - 3rd  100k - 1st  100k - 3rd
    ------------------------------------------------------------
    Autofac                25         23         166         163
    Castle.Windsor         35         39         342         328
    Ninject               128        133       1,053       1,040
    Spring.Net             59         36         223         229
    StructureMap          114        118         289         348
    Unity               6,012      5,945      62,278      59,292
    				
             Min           25         23         166         163
             Max        6,012      5,945      62,278      59,292
             Median        87         79         316         338 


What the?! What just happened!? Are those **Unity** numbers real? It cannot be that it showed figures that are **258.5** and respectively a whooping **363.8** times slower than **Autofac**. By contrast, it makes the usual suspect, **Ninject**, look like Formula-1 car.

Unfortunately it is true. I was so stupefied by the result that I had to try two different approaches on three different machines. They all posted similar numbers.

<A name="transient_loaded"> </A>
## transient objects - loaded containers

You can probably anticipate how quickly I moved on to the next test. **Unity** has put an okay performance in the transient test, recording number on par with the other two usually fast containers: **Autofac** and **Windsor**.
Alas, from running the test, which took forever and three cookies, I could tell there was no redemption. And sure enough:

    :               10k - 1st  10k - 3rd  100k - 1st  100k - 3rd
    ------------------------------------------------------------
    Autofac                73         74         806         645
    Castle.Windsor          99         98       1,164         941
    Ninject               248        247       2,683       2,338
    Spring.Net            230        226       2,346       2,157
    StructureMap          118        116         324         312
    Unity               6,077      5,918      60,142      58,971
    				
             Min           73         74         324         312
             Max        6,077      5,918      60,142      58,971
             Median       174        171       1,755       1,549 


<A name="tldr"> </A>
## conclusion

I've plotted the results to get a better glance at what just took place. I had to force a max value on the milliseconds axxis seeing how **Unity**  completely blew the scales.

The chart of timings by task gives us a focused view and paints the relative behavior of containers within those groups:
![10k by task](/media/images/di_10k_task.jpg)
![100k by task](/media/images/di_100k_task.jpg)

Notice how **Autofac**, **Windsor**, and **StructureMap** behave consistently well, **Ninject** behaves consistently badly (although that's an exaggeration), whereas **Spring.Net** and **Unity** are highly irregular in their numbers.

Plotting the same numbers by container shows the areas of strength and weakness of each participant:
![10k by container](/media/images/di_10k_container.jpg)
![100k by container](/media/images/di_100k_container.jpg)

We also get to see quirks, such as four out of six containers showing a dip in the "singleton loaded" test

Syntactically all containers are roughly the same syntactically and in feature parity - one can easily move from one to the next with little training, the only *significant* differentiator that I observed was elegance of configuration, but that's hardly something to hang your project onto.

### tl;dr for the conclusion

Here's my personal take, from both seeing these numbers, working with the containers (not just for the purpose of this test), and being somewhat aware of what tells them apart: **[StructureMap][smap]** gets some interesting and unique features due to [Jeremy Miller](http://codebetter.com/jeremymiller/)'s interest in web development - I wouldn't hesitate picking **StructureMap** if I were building a web app; my favorite is **[Autofac][autofac]**, which is small, incredibly powerful, and yet very elegant to use. In stark contrast to **Spring.Net**, I think I spent the least amount of time trying to figure out how to use **Autofac** - mostly everything seemed obvious. Even the more advanced features, some of which the other containers are either barely now getting them or still dreaming of them, are very straighforward and easy to pick up.

**[Castle.Windsor][castle]** is the pretty much the veteran in here, yet it managed to stay nimble. It's got one of the [smartest guys](http://ayende.com/blog) in the industry behind it. It has a few quirks here and there, and it's not the most elegant to work with. With both **StructureMap** and **Autofac** in play, I honestly cannot conjure a good reason to pick **Windsor** over them, unless you are using the rest of the **[Castle](http://www.castleproject.org)** framework.

At the opposite side of the spectrum: **[Spring.Net][spring]**. A very powerful framework, especially if you come from Java, its IoC container is just horrible to work with. I've always left it for then end and punished myself for eating too many cookies by forcing me to complete the wrapper classes for the tests. I am aware of the [CodeConfig][scodeconfig] project and its attempt to bring some sanity and an alternative to the hideous XML configuration files that **Spring.Net** otherwise employs. It's not only has spotty and slow performance, it's actually quite unpleasant to work with. Microsoft's **[Unity][unity]** is not a bad DI containers; it used to be meh at version 1.2, but starting with 2.0 - which took a very long time to come to light - it's quite nice to work with. That is until you see the numbers and quite honestly that's offputting, no many how many injection and extension features it offers. Finally, **Ninject** - cool name, awesome website, bad performance. It's not the most elegant to work with either; I would use it if the alternative was **Spring.Net** - I honestly can't see any other reason why.

Alright, we're done. The [sourcecode][gitdi] is on github and once you read it you're probably want to [contact me](/contact.html) and laugh at something stupid I did in there. Or just want to talk about those hard to believe **Unity** numbers.



[gitdi]: https://github.com/philipmat/di_speed "DI Speed on github" 
[autofac]: http://code.google.com/p/autofac/
[castle]: http://docs.castleproject.org/Windsor.MainPage.ashx
[ninject]: http://ninject.org/
[spring]: http://www.springframework.net/
[scodeconfig]:https://github.com/SpringSource/spring-net-codeconfig
[smap]: http://structuremap.net/structuremap/
[unity]: http://unity.codeplex.com/
[ayendecreation]: http://ayende.com/blog/3167/creating-objects-perf-implications
