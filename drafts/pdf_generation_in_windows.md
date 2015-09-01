---
title: Generating PDFs with C#
layout: post
---

When researching PDF generation in .Net,
the most common recommendation seems to be [iTextSharp][itextsharp].

It's a fine library, that's for sure, and it gives you 
lots of control over the content of the generated PDF,
to the smallest detail and the most advanced features.

However, it's also 2015 and writing code like the following:

{% highlight c# %}

PdfContentByte pcb = writer.DirectContent;
pcb.BeginText();
BaseFont font = BaseFont.CreateFont(BaseFont.HELVETICA, BaseFont.CP1252, false);
pcb.SetFontAndSize(font, 36);
pcb.ShowTextAligned(PdfContentByte.ALIGN_CENTER, "Hello", 280, 190, 0)
pcb.ShowTextAligned(PdfContentByte.ALIGN_CENTER, "World", 280, 680, 0)

{% endhighlight %}

reeks of the dark days of AWT.

Fortunatelly, there is a better, if perhaps surprising solution: 
Microsoft's [ReportViewer Controls][rptcontrol].

[itextsharp]: http://itextsharp/
[rptcontrol]: https://msdn.microsoft.com/en-us/library/ms251671.aspx
[template]: http://johnnycode.com/2010/03/05/using-a-template-to-programmatically-create-pdfs-with-c-and-itextsharp/
