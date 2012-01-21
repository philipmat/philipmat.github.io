---
title: New (Old) Web App Architecture
layout: post
snippet: An new approach to building web apps that has been around for quite some times.
---

We've been doing this for a while, more or less, in various shapes and forms, so it's nothing new.
We've been doing it as mash-ups and we've been doing it with AJAX and we've done it with web services, 
but we've only done mash-ups when we couldn't control the source of data, and we've done AJAX only to speed things up,
and web services - well, they're traditionally XML based, and by now we've mostly agreed that is somewhat ugly.

When we could control the source of data, we've reverted back to some server-side framework producing the UI code, 
and we worked hard to make that combination good, just like we worked hard before to make integrating web services easy.


## Why a New Way?

What we have right now - with Rails, and Django, and ASP.NET MVC, and PHP, and you name it - is better that everything we 
ever had before, but there are a few things that irk me about the current state of affairs:

- If I want to change your UI (and I don't mean cosmetically), it's almost guaranteed that I have to **learn your framework**.
At a minimum, I'll have to learn your templating language, but my point is that I cannot do much if I only know HTML and 
JavaScript. Conversely you will not be able to make use of my hypothetical UI skills unless I also happen to know your framework.
- It's **laborious to get your project to run**. Sometimes it's easy, most often it's not; I'll run into dependency issues, 
versioning issues, versioning of dependencies issues, and project setup issues when all I wanted to do was to make a minor 
UI change.
- I need to **run your whole stack** to be able to see and change your UI: database, modules (gems, eggs, dlls), services, etc. 
If any of your dependencies is truly external (say that SAP system you get your list of clients from) you most likely can 
kiss your off-lining goodbye, unless you were smart enough to provide a stub service that still serves relevant data.
- If your project provides a UI but doesn't provide a **separate API**, it's very difficult or at least impractical for me to consume your data. 
This is more difficult to accept in an enterprise where we're all supposed to be working towards the same goal. And building a separate API 
slows you down, and increases your maintenance costs because now you have two pieces of software you need to maintain, unless you were 
smart from the beginning and made *your* app consume *your* API.
- There's a clear boundary between the client - the web browser - and the server, with a good deal of data being sent 
back and forth, yet you mostly never **write tests for the communication between browser and server**. You don't do that 
for the same reason: it's difficult or impractical to consume what you send (GET), slightly easier to consume what you receive (POST, PUT, DELETE).
- In some setups it **takes time for a model change to propagate to the UI**, more so with compiled languages. 
Thor forbid if you need to make a DB change - now we have to wait for the DBA(s).
- It's hard to **scale your app** because building your UI often needs all the models it uses to have been loaded in 
the same thread/process. Most of the time, your apps, or at least the layers building the UI, are not designed or cannot handle different models coming from 
different sources.
- You are **building your UI sequentially**. Slowest buffalo wins: you have to wait for your slowest model to load before you can send your page to the browser.
Not that async building would always make a difference - sometimes you just have to wait for that drop-down to populate before 
you can successfully edit that record - but in a sync world it doesn't matter if the relevant data is fast and the irrelevant data 
loads slowly, because it all boils down to everything having to finish loading before you produce your UI.

As web developers we cringe at the thought of putting markup in the database, or having stored procedures generate HTML, but 
we have no problems with code generating HTML.
I'm not saying it's hypocrisy, [but it's the first word that comes to mind](http://www.amazon.com/Choke-Chuck-Palahniuk/dp/0385720920).

If you're a desktop developer, imagine your services spewing UI controls instead of just typical web service XML.
Imagine your `UIToolbar`, `NSButton`, `ContextMenuStrip`, or your `GridBagLayout` being the result of a 
web service call; I don't mean a UI control that you create in your UI layer based on a web service call,
but an actual object that you only deserialize and put on screen at (x,y). 
I get a shiver just writing this, but in the world of web apps it's something perfectly natural.

Why? Because we have a good templating language? Because we've always done it this way? 
Because everything comes from a server anyway?

Between mash-ups and web services, we've already solved a great deal of those issue. 
We just need to apply them rigorously and consistently.


## Proposal 

I propose that we [build the app][github] UI using static HTML (as in not produced by other code) and 
that we use only JSON to exchange business data, by means of the four HTTP verbs (GET,POST,PUT,DELETE), 
essentially turning your Rails/Django/ASP.NET MVC/PHP app into a lean-mean JSON producing/consuming machine. 

Loading the UI for displaying or editing an entity would take the following steps:

1. The browser requires from the web server `http://example.com/clients/1`. It receives a 
static HTML page representing the layout required to display the client and JavaScript code
that knows how to perform the next step.
2. The JavaScript code (e.g. jQuery) loads, perhaps from another server, `http://data.example.com/clients/1`,
the JSON representation of **Client(1)**.
3. The JSON values are displayed into the static layout (for example, using Knockout.JS).
4. Saving is performed by POSTing the updated JSON representation back to the originating data URL (`http://data.example.com/clients/1`).

If we consider that most pages fall into a few larger categories: display entity list, display one entity, edit one entity, etc. 
the first step can be further generalized by having it serve a more generic static template for the category and having it load 
more detailed template for the entity:

1. The browser navigates to `http://example.com/one_entity.html#clients/1`. It receives a static
HTML page representing the generic layout for displaying one entity and JavaScript code 
that knows how to load the detailed template, and how to load the entity data.
2. The JavaScript code loads `http://example.com/templates/client.html` and inserts it into a 
known placeholder node.
3. The JavaScript code then loads JSON from `http://data.example.com/clients/1` and populates the 
template received in step two.

![Diagram of how all this works](/media/images/new_webapp_architecture.png)

This latter formula allows us to focus on the details of what differs between various entity displays 
and maintain the same layout.


## Advantages

With this approach:

- If I want to change your UI, all I have to learn is your API, which is as little as looking at 
what **JSON objects** you send me.
- I don't need to get your project to run: all I need are the **static HTML files**. 
I can **serialize your JSON replies** to individual files and serve them as such. 
Sure, I won't be able to send them back, but at least I can navigate most of your app.
- I don't need to run your whole stack: all I need is a **web server**.
- You don't need to provide a separate API - your **web services are now your API**. I can integrate with 
your API just as easy as you can.
- We both can now **write and run tests for that client-server boundary**. By preserving the JSON you send me at one 
point in time I can make sure that any changes you made in your active code don't cause surprise 
midway through my development cycle. You too can serialize known replies to make sure that code changes elsewhere have not 
caused changes in the API.
- UI changes are in almost all cases as easy as a **page refresh**. You can make your model and DB changes later - 
as long as you send me the JSON structure we agreed on my UI will behave correctly.
- You can **scale your app through sharding at domain level**, different JSON sources coming from different servers, 
and I can make sure I will configure my URL(s) to account for that. That also means that if I want to get clients from 
that SAP server you don't have to write a bridge, I'll just use theirs (which hopefully provides a JSON interface).
- Because asynchronous tasks is something JavaScript is really good at, I can **load my interface asynchronously**:
I can load the list of clients from server 1, the list of countries from server 2, and current market prices for lolcats 
from server 3 without doing anything I wouldn't normally do in JavaScript. Actually making things synchronous in JS 
is sometimes the more complicated approach (ask NodeJS programmers).

On top of that:

- What you cache (JSON) became considerably smaller and any web server can already deal incredibly efficiently 
with static HTML.
- You can send an implementation team to a client site that doesn't have to know much beyond HTML and JavaScript, 
and let's be honest - that skill set comes in considerably cheaper.
- You can finally get that HTML5 guru that loathes working with ASP.NET. Because he won't have to. 
And he'll get to use his Mac (yay!).

Between libraries like jQuery and Knockout.JS (or Backbone.JS) we already have all the tools to make it happen. 
Chances are you already use them [with][aspnet_example] [your][rails_example] [app][java_example] - why not go all the way.

Notice that I was careful not to say the app is RESTful - that's because my proposal doesn't address the 
[fourth guiding principle](http://en.wikipedia.org/wiki/HATEOAS "Hypermedia as the Engine of Application State") of Fielding's 
cannon. That's something for you to decide (and I think [you should do it][curtis_rest]).

Here's a simple example, using Knockout.JS, to see what I'm talking about: [http://github.com/philipmat/webmvc/][github].

 
[github]: http://github.com/philipmat/webmvc/
[aspnet_example]: http://weblogs.asp.net/shijuvarghese/archive/2011/08/21/building-javascript-mvvm-apps-in-asp-net-mvc-using-knockoutjs.aspx
[rails_example]: https://workshops.thoughtbot.com/backbone-js-on-rails
[java_example]: http://geeks.aretotally.in/log4play-log4j-ui-mashed-up-with-play-framework-knockout-js-and-websockets
[curtis_rest]: http://curtis.schlak.com/2012/01/19/fieldings-rest.html
 

