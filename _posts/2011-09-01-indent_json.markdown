---
title: Three ways to indent JSON
layout: post
---

Python comes with a [JSON encoder and decoder](http://docs.python.org/library/json.html) you can use to prettify messy JSON code.

## on the command line

If you have an unindented JSON file:  

`cat ugly.json | python -mjson.tool > pretty.json`

(May I recommend the wonderful [DTerm](http://itunes.apple.com/us/app/dterm/id415520058?mt=12) to run commands from almost any app you might be in?)

## from within VIM

Using filter commands, `!`, replace the text with its formatted version, filtered through the same Python command:  

`:%!python -mjson.tool`

Since it's VIM, you can replace as little or as much as needed; see [Use filter commands to process text](http://vim.wikia.com/wiki/Use_filter_commands_to_process_text) for more information.

## with a service

Create an Automator service and use the *Run Shell Script* action to process the input text (make sure to select the *Output replaces selected text* checkbox), once again using Python:

![Automator service](/media/images/json_workflow.png)

Since Automator automatically saves services to the `~/Library/Services/` directory, it'll become available to you instantly, and it'll allow you to go from this:   
![Unindented JSON code](/media/images/json_0.png)

to this:  
![Indented JSON code](/media/images/json_1.png)



