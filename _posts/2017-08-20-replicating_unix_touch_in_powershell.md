---
title: Touch Command in PowerShell
snippet: Replicating the Unix `touch` command in PowerShell
layout: post
---

The two simplest use cases for the `touch` command are to:

1. Create one or more files, if they don't exist;
2. Update the access date or modification date of files without changing their content.

To replicate these two cases in PowerShell, we make use of
the [`LastWriteTime`](https://msdn.microsoft.com/en-us/library/system.io.filesysteminfo.lastwritetime.aspx)
property of a `FileSystemInfo` object, as well as creating an empty file if
one does not exist at the specified path.

You can add the following code to the `Microsoft.PowerShell_profile.ps1` file in
your `<Users>\Documents\WindowsPowerShell\` folder:

<script src="https://gist.github.com/philipmat/1841540bd05ebb98bec402e6b387ff56.js"></script>

You can now call it with either: `Update-File file1.txt file2.txt` or
`touch file1.txt file2.txt`.

## Couple of Points Worth Making

We name the function `Update-File` following the PowerShell pattern or verb-noun pair for commands
and the *Data Verbs* section of
[Approved Verbs for Windows PowerShell Commands](https://msdn.microsoft.com/en-us/library/ms714428.aspx#Data%20Verbs).

We set pass the `-Encoding ascii` to the `Out-File` command
as the default encoding for `Out-File` is UTF-16
and some \*nix transplant tools have troubles handling UTF-16 files
because of the two byte-markers at the beginning of the file
(for example *webpack* when bundling files).

Finally, credit goes to [this answer](https://superuser.com/a/571154)
on StackExchange's *superuser*.