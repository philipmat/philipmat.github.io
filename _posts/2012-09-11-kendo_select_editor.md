---
title: Kendo Grid Select Editor
layout: post
---

I'm going to assume you're reading this post because you'd like to find out
how to use a regular HTML SELECT as an editor in a [Kendo grid](http://demos.kendoui.com/web/grid/index.html), 
and that you already know why you want to do that - you just had a 
hard time figuring out how to.

If you just want to see the code and don't care about the explanation, 
[here is a jsFiddle](http://jsfiddle.net/8CWcF/10/) to play with,
also a [gist](https://gist.github.com/3695638) for your forking pleasure.

If you wonder why you'd want to do it, read the [Why would I want to do that?](#why)
section that come back for the how.

I see two primary scenarios for using a SELECT aka drop-down list.

## Simple Field - Extra Info

This would be the case where, for example, your model contains a field to store 
the user login (e.g. *foo*), but when displaying the drop-down to select the user 
you'd like to also list their name (e.g. *foo - Foo Frye*).

Let us assume you have the mapping of login to full name in an array of objects, 
and for genericality's sake let's assume it has a format similar to the following:

    var nameList = [
      { Login: 'foo', Description: 'foo - Foo Frye' },
      ...
    ]

When you create your grid and specify the columns, you have the chance to pass in a function 
that would create a custom editor instead of the text box the grid gives you by default:

{% highlight javascript %}
$('#grid').kendoGrid({
  ...
  dataSource: {
    data: [
      { ..., Login: 'foo', ... }
    ]
  }
  columns: [
    ...
    {
      field: 'Login',
      editor: function(container, options) {
        var s = $('<select ' +
                  ' data-bind="source: listSource.list, ' +
                    'value: ' + options.field + '" ' + 
                  ' data-text-field="Description"' + 
                  ' data-value-field="Login"' + 
                  '/>')
        options.model.listSource = kendo.observable({list: nameList})
        s.appendTo(container)
      }
    }
    ...
{% endhighlight %}


What's going on here?

1. We create a drop-down `$('<select/>')`
2. Using the `data-bind` attribute we tell Kendo to use a specific `source`
   for the drop-down and to write the selected `value` to the underlying
   model's field (here `options.field == 'Login'`).
3. We tell it to use the *Description* property of each element in the 
   `source` for the text portion, and the *Login* field for the `value`.
   This would be as if we had an `<option value="foo">foo - Foo Frye</option>`.
4. We create a `kendo.observable` containing the list of names.
5. We append the HTML select to the container, which, if you're curious,
   is the actual grid cell (`TD`).

There are only two tricky parts here and they both gravitate towards the 
use of the `source` directive: `options.model` is the object from your data source that correspond to the 
grid row; the `source: listSource.list` will look for a property called *listSource*
on the grid row/object/model and expect it to    
a) be a kendo.observable and    
b) contain a sub-object named *list*.



## Complex Field

What if your *Login* field was a complex object, maybe similar to one 
of the entries in `nameList`? If this was the case, how would you go 
about displaying it in a SELECT, but have it write back to your field
the same complex object, not just a simple string.

The code looks similar, in a way even simpler:


{% highlight javascript %}
$('#grid').kendoGrid({
  ...
  dataSource: {
    data: [
      { Complex: { Login: 'foo', Description: 'foo - Foo Frye' } },
    ]
  }
  columns: [
    ...
    {
      field: 'Complex',
      editor: function(container, options) {
        var s = $('<select ' +
                  ' data-bind="source: listSource.list, ' +
                    'value: ' + options.field + '" ' + 
                  ' data-text-field="Description"' + 
                  '/>')
        options.model.listSource = kendo.observable({list: nameList})
        s.appendTo(container)
      }
    }
    ...
{% endhighlight %}

The most significant difference from the simple example is the 
absence of the `data-text-value` attribute. This causes the entire 
underlying record to be written back into the *Complex* model field.

That's it. If there was a simpler way to do this, I couldn't find it.


<a name="why"> </a>
## Why Would I Want to Do This?

If you use Telerik's excellent Kendo stack, you already have access to a nice 
drop-down editor that is part of the suite. The Kendo UI demos even show you
[how to use the Kendo DropDownList](http://demos.kendoui.com/web/grid/editing-custom.html) 
as a custom editor, and use it you should for it has a plethora of features.

For all its niceness, the DropDownList is built upon styled UL/LI elements, 
and that means it is missing a few features that a normal drop-down would have,
chiefly the ability to use keyboard navigation and the two 
significant advantages that come with it: using keys to trigger and navigate the 
list (Alt-Down on Windows and Spacebar on Mac), and type-to-select when focused
(for example typing **Tex** or **TT** to select **Texas** in a list of states).

That and the fact that it doesn't play 100% nice with [Twitter Bootstrap](http://twitter.github.com/bootstrap/),
in the sense that the styles don't quite match. Oh, and on a mobile browser you don't
get the native picker.

Fortunately, the Kendo grid allows you to specify a custom editor for a column;
unfortunately, the Kendo stack tends to make use of and wrap your SELECT in a 
`kendo.observable` type of object. I suspect that this is the main reason 
why examples of using normal HTML inputs with the Kendo grid tend to be scarce on the web.

