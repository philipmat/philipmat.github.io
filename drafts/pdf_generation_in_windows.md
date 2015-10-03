---
title: Generating PDFs with C#
layout: post
---

When researching PDF generation in .Net,
the most common recommendation seems to be [iTextSharp][itextsharp].

It's a fine library, that's for sure, and it gives us 
lots of control over the content of the generated PDF,
to the smallest detail and the most advanced features.

However, it's also 2015 and writing code like the following:

```
{% highlight c# %}

PdfContentByte pcb = writer.DirectContent;
pcb.BeginText();
BaseFont font = BaseFont.CreateFont(BaseFont.HELVETICA, BaseFont.CP1252, false);
pcb.SetFontAndSize(font, 36);
pcb.ShowTextAligned(PdfContentByte.ALIGN_CENTER, "Hello", 280, 190, 0)
pcb.ShowTextAligned(PdfContentByte.ALIGN_CENTER, "World", 280, 680, 0)

{% endhighlight %}
```

reeks of the dark days of AWT.

Fortunatelly, there is a better, if perhaps surprising solution: 
Microsoft's [ReportViewer Controls][rptcontrol].

Generating decent-looking PDFs involves a good deal of pixel-pushing,
and this is where ReportViewer shines: it has a designer built right
into Visual Studio *TODO: versions??*

*TODO: screenshot of designer*

The good news don't stop there. ReportViewer it's easy to work with,
it has both web and WinForms versions, and it persists its definition
into a VCS-friendly XML file (as friendly as XML can be to VCS) 
with an `.rdlc` extension. Advanced features include: programmability,
sub-reports, ability to include external reports (good for sharing common headers/footers),
group-by functionality, filtering, and pretty much anything you came 
to expect from a middle-of-the-road reporting solution. 

Due to its heritage, working with reports shines when directly connected
to a database, but in disconnected mode ReportViewer Controls are just
as useful.

Let's look at it in a bit more detail. Some of the instructions below
may be sequential, but they won't be detailed step-by-step descriptions.
I assume that if you read this, you are somewhat familiar with the subject.

What I do have to help with, is a few sample projects that show the end results
of these instructions: [philipmat/reportviewersamples][ghrepview].

## Working with ReportView Controls

At runtime, the RVC can feed of pretty much any IEnumerable, but 
to better take advantage of the designer, we should back the report
with a typed dataset (*ugh* is about right, but bear with me - it's
really not that horrible).
 
[Project 1][ghrepview1] shows such a setup. It's an ASP.NET MVC app
that'll end up generating a PDF file.

To start with, I created a typed dataset with a table having a few columns.

I then create a new `.rdlc` file and begin designing my report in Visual Studio.

To hopefully surprise you, we will be using a SQLite database loaded with some
demo data. The data is loaded into the typed dataset, the typed dataset is 
passed into the report and then we just rended the report and get the PDF output
as bytes.

{% highlight c# %}

{% endhighlight }

## Subreports

Sub-reports are typically used to insert common tables and components into existing report. 
Another use, perhaps not as obvious, is to add common header and footers 
for our reports.

The sub-reports are reports in their own righ and thus somewhat 
independent of the parent report. Sub-reports are not loaded and 
rendered when the parent report is created, but rather when they 
"come into view". Of course, this is more relevant to displaying 
reports in the UI and not relevant to PDF generation
as the entire document gets rendered in order to paginate properly.

However, the mechanics of providing data to the sub-reports stem 
from this specific nature of the sub-reports: instead of the main 
report injecting data into the sub-reports, we handle at the 
ReportViewer control level an event that gets triggered when our 
subreports get loaded.

{% highlight c# %}

{% endhighlight %} 


## Controlling visual elements

A good deal of properties of the elements in a report can be controlled at rendering time based on 
the data within the backing datasets. More than than, those properties can be bound to 
complex expressions using the power of Visual Basic **.NET??** and quite an extensive library of functions.

Let's look at just three common properties we can control.

### Value 

Binding the value is as simple as writing `=Field!FieldName`. Let's make it interesting.

In the following example, we'd like the *Quantity* column to combine the actual quantity, 
displayed with thousands separator and two decimals, 
with the unit of measure, e.g. *1,234.50 gal*. 
In addition, if the field is null, we'd like to display *(None)*.  

To do this, we'll open up the property editor and 
set the value of the field to the following expression.

[property editor image]

{% highlight vb %}

{% endhighlight %}

### Conditional formatting

Building upon the example above, we'd like to format the *Quantity* so that it displays
in red if any of the values are negative.

In the property editor window, we'll use the ??? field's expression editor:

{% highlight vb %}

{% endhighlight %}

### Visibility

We can control the visibility of an object the same way we controlled its formatting - 
it's just a property after all. This could be made more useful in combination with a 
panel on which we put our controls.

For example, if our client doesn't have a separate billing address set up, 
we'd like to hide all the secondary fields and labels associated with it:
address, phone, etc. To do so, we'll add all those fields to a panel and
set the panel's ??? property based on whether a combination of fields are 
null or not.

[block image]

And the visibility property is set to: `=IIF()`. 

## Errors and Warnings

There seem to be several classes of warning and errors related to the ReportViewer control.

There's a set that show up during compilation, for example:

     ???Sample error
	 
It might be useful to pay attention to some of these, 
but likely most of them are either intentional (overlaps) or have no 
adverse effects.


The `RenderToPdf` method returns through an `out` parameter warning (and errrors???) 
resulted from running the report.

{% highlight c# %}

{% endhighlight %}

While these may be interesting during development and testing phase, 
since they're not actionable by the user, nor do they provide 
a reasonable way to recover from them, I'm not really sure what 
their real-world usefulness is.

A third class of errors come from field processing; 
when that happens the rendered field will simple read `#ERROR#`. 

This is a more insidious class of errors as beyond not being 
user actionable, they might also require specific data setups 
in order to produce them during the QA process. 

## Loading Reports

There are three ways we can load reports: from files, 
from embedded resources, and from binary streams. 

{% highlight c# %}

// load from file
// load from embedded resource
// load from binary data 

{% endhighlight %}

Each mode has obvious trade-offs which need to be considered 
once the project is deployed. However, one important consideration
is whether the report include sub-reports, because the manner in which 
these sub-reports are included   


## Report (Pre)Viewer



[itextsharp]: http://itextsharp/
[rptcontrol]: https://msdn.microsoft.com/en-us/library/ms251671.aspx
[template]: http://johnnycode.com/2010/03/05/using-a-template-to-programmatically-create-pdfs-with-c-and-itextsharp/
[ghrepview]: https://github.com/philipmat/reportviewer
[ghrepview1]: https://github.com/philipmat/reportviewer