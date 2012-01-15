---
title: New (Old) Web App Architecture
layout: post
snippet: An new approach to building web apps that has been around for quite some times.
---

We've been doing this for a while, more or less, in various shapes and forms, so it's nothing new.
We've been doing it as mash-ups and we've been doing it with AJAX and we've done it with web-services, 
but we've only done mash-ups when we couldn't control the source of data, and we've done AJAX only to speed things up,
and web-services - well, they're traditionally XML based, and by now we've mostly agreed that is somewhat ugly.

When we could control the source of data, we've reverted back to some server-side framework producing the UI code, 
and we worked hard to make that combination good, just like we worked hard before to make integrating web-services easy.

What we have right now, with Rails, and Django, and ASP.NET MVC, and PHP, and you name it, it better that everything we 
ever had before, but there are a few things that irk me about the current state of affairs:

- If I want to change your UI (and I don't mean cosmetically), it's almost guaranteed that I have to **learn your framework**.
At a minimum, I'll have to learn your templating language, but my point is that I cannot do much if I only know HTML and 
JavaScript.
- It's **laborious to get your project to run**. Sometimes it's easy, most often it's not; I'll run into dependency issues, 
versioning issues, versioning of dependency issues, and project setup issues when all I wanted to do was to make a minor 
UI change.
- I need to **run your whole stack** to be able to see and change your UI: database, modules (gems, eggs, dlls), services, etc. 
If any of your dependencies is truly external (say that SAP system you get your list of clients from) you most likely can 
kiss your off-lining goodbye, unless you were smart enough to provide a stub service that still serves relevant data.
- If your project provides a UI but doesn't provide a **separate API**, it's very difficult or at least impractical for me to consume your data. 
This is more difficult to accept in an enterprise where we're all supposed to be working towards the same goal. And building a separate API 
slows you down, and increases your maintenance costs because now you have two pieces of software you need to maintain, unless you were 
smart and made your app consume your API.
- There's a clear boundary between the client - the web browser - and the server, with a good deal of data being sent 
back and forth, yet you mostly never **write tests for the communication between browser and server**. You don't do that 
for the same reason: it's difficult or impractical to consume what you send (GET), slightly easier to consume what you receive (POST, PUT, DELETE).
- In some setups it **takes time for a model change to propagate to the UI**, more so with compiled languages. 
- It's hard to **scale your app** because building your UI often needs all the models it uses to have been loaded in 
the same thread/process. Most of the time, your apps are not designed or cannot handle different models coming from 
different sources.
- You're **building your UI sequentially**. Slowest buffalo wins: you have to wait for your slowest model to load before you can send your page to the browser.
Not that async building would always make a difference - sometimes you just have to wait for that drop-down to populate before 
you can successfully edit that record - but it a sync world it doesn't matter if the relevant data is fast and the irrelevant data 
loads slowly, because it all boils down to everything having to finish loading before you produce your UI.

If you've ever built an n-tier desktop app, imagine your services spewing UI controls instead of just XML. 
Imagine your `UIToolbar`, `NSButton`, `ContextMenuStrip`, or your `GridBagLayout` being the result of a 
web-service call; not something that you create in your desktop app a result of data from the web-service,
but an actual object that you only deserialize and put on screen at (x,y). 
I get a shiver just writing this, but in the world of web apps it's something perfectly natural.

Why? Because we have a good templating language? Because we've always done it this way? 
Because everything comes from a server anyway?


