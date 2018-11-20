---
layout: post
title: Converting to Base64 in Powershell
---

There are a variety of ways to send a file to Web end-point and encode it
in the the process. For [example](https://stackoverflow.com/a/31341055),
using `Invoke-RestMethod -InFile` ([docs][i-rm]):

    C:\PS> Invoke-RestMethod -Uri http://example.com `
      -Method Post -ContentType 'multipart/form-data' `
      -InFile c:\temp\test.txt

However, if we want/need to include one or more files as part of a larger JSON payload,
perhaps with other information for each file, we will need to convert the file(s) to Base64.

To do so, we'll make use of .Net functionality, in particular the
`System.Convert.ToBase64String` method and the
`System.Web.Script.Serialization.JavaScriptSerializer` class (see note).

```ps
# define parameters
Param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile
)

$content = [System.IO.File]::ReadAllBytes($InputFile)
$base64String = [System.Convert]::ToBase64String($content)

# Load System.Web.Extensions
Add-Type -AssemblyName System.Web.Extensions
$jsonSerializer = New-Object System.Web.Script.Serialization.JavaScriptSerializer
$json = $jsonSerializer.Serialize(@{ content = $base64String })

Write-Output -InputObject $json

# writes: {"content":"dGVzdAOK"}

```

For a full, proper script, with multiple parameters (writing to a file, copying to clipboard)
see this [ConvertTo-Base64.ps1 gist][gist].

**Note**: I chose `System.Web.Extensions` over the more common `Json.Net`
because I didn't want to have to download/nuget a dependency;
`JavaScriptSerializer` proves sufficient for this task.

[i-rm]: https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-restmethod?view=powershell-5.
[gist]: https://gist.github.com/philipmat/90937a7044be734d4811e44eaf19f61a
