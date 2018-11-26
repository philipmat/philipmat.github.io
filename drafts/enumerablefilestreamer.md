---
layout: post
title: Enumerating Directly to a FileResult
---

ASP.NET Core controllers [have a series][file]
of file method that deal with returning files to the browser.

The methods can be grouped in three categories,
all returning a `FileResult`:

* returning a file specified by path: `File(String, ...)` and friends;
* returning an array of bytes making up a file contents:
  `File(byte[], ...)`, etc;
* returning a file whose content is read from a stream:
  `File(Stream, ...)`, etc.

As of v2.1 there's over 20 `File(...)` methods supporting the various scenarios
of these 3 categories.

What is missing, likely because it doesn't fit
with the simplicity of types used in the other signatures,
is the ability to write an enumeration
directly to the output stream and do so with minimum memory usage.

An good example would be to serve the results of a query
as CSV.

There are certain ways to work with the existing methods,
for example we could write the enumeration to a file
and then use on of the `File(string, ...)` methods
to serve the file.  
Another approach would be to write it into a stream, in
memory (`MemoryStream`), re-setting the stream position to 0
and using the `File(Stream, ...)` signatures.

Both of those approaches are inefficient in that they either
perform unneeded I/O or use unnecessary memory.

In either of these cases, the more efficient approach
would be enumerating/iterating through the records
rather than materializing the entire dataset,
and writing them out to the response stream
one by one.

To do so we'll construct our own implementation
of the abstract `FileResult` class. The source
of inspiration is the fact that each of the `File`
methods mentioned above returns their own
type of `FileResult`: `FileContentResult`,
`FileStreamResult`, etc.

Our implementation, `EnumerableFileResult` will accept an `IEnumerable`
and will write its elements one by one to the `Response.Body`
stream (`System.IO.Stream`).

However `EnumerableFileResult` would not know
how to write the elements to the stream, so it will
delegate that resposibility to an adapter class,
one implementing an proposed `IStreamWritingAdapter` interface.

To make the this whole implementation even more flexible,
we'll consider allowing the adapter to write a header,
for example the column names, and since we're there
allow it to write a footer too (maybe the total record count?).

The `IStreamWritingAdapter` looks like the following:

```csharp
public interface IStreamWritingAdapter<T>
{
    string ContentType { get; }

    Task WriteHeaderAsync(Stream stream);

    Task WriteAsync(T item, Stream stream);

    Task WriteFooterAsync(Stream stream, int recordCount);
}
```

The `ContentType` ties the adapter to the file type,
after all they're in synca, and allows the adapter
to inform the `FileResult` parent of the MIME content-type
of the content dispatched to the caller.

To recap:

* `EnumerableFileResult<T>` inherits from `FileResult`;
  * Accepts an `IEnumerable<T>`;
  * Uses an `IStreamWritingAdapter<T>` to write each
    element of the enumeration to a `Stream`.

```csharp
class EnumerableFileResult<T> : FileResult
{
    private readonly IEnumerable<T> _enumeration;
    private readonly IStreamWritingAdapter<T> _writer;

    public EnumerableFileResult(
        IEnumerable<T> enumeration,
        IStreamWritingAdapter<T> writer)
        : base(writer.ContentType)
    {
        _enumeration = enumeration ?? throw new ArgumentNullException(nameof(enumeration));
        _writer = writer ?? throw new ArgumentNullException(nameof(writer));
    }

    public override async Task ExecuteResultAsync(ActionContext context)
    {
        SetContentType(context);
        SetContentDispositionHeader(context);

        await WriteContentAsync(context).ConfigureAwait(false);
    }

    private async Task WriteContentAsync(ActionContext context)
    {
        var body = context.HttpContext.Response.Body;
        await _writer.WriteHeaderAsync(body).ConfigureAwait(false);
        int recordCount = 0;
        foreach (var item in _enumeration)
        {
            await _writer.WriteAsync(item, body).ConfigureAwait(false);
            recordCount++;
        }

        await _writer.WriteFooterAsync(body, recordCount);

        await base.ExecuteResultAsync(context).ConfigureAwait(false);
    }
    ...
}
```

The usage is fairly straighforward; within a controller
or a page handler, we return an instance of the
`EnumerableFileResult` initialized with the enumeration
and the writer:

```csharp
public IActionResult OnDownload() {
    IEnumerable<Person> people = GetPeople();
    return new EnumerableFileResult<Person>(
        people,
        new PeopleToCsvWriter()) {
            FileDownloadName = "People.csv"
    };
}
```

I've [provided on GitHub][gh] a fully functioning example.

Simply clone and run the application and notice
that the memory usage of the application while
generating 100k or even 1M records is fairly
small and constant past the initial load.


[file]: https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.mvc.controllerbase.file?view=aspnetcore-2.1
[inspiration]: https://stackoverflow.com/a/22834363
[fileresult]: https://docs.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.mvc.fileresult?view=aspnetcore-2.1
[gh]: https://github.com/philipmat/EnumerableStreamFileResult
