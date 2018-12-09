---
layout: post
title: Replicating macOS's say command in Windows
---

Is `say`, macOS has a wonderful command line utility
which I found to be useful to use in conjuction
with long-running processes or even debugging
to help draw attention, more so that typical beeping
would do.

In short, `say` speaks text - is a Text-to-Speech (TTS)
program.

    say "Hello, there"

I wanted something similar on Windows and while
there's no direct equivalent, luckily .NET
provides an entire host of utilities through
the [System.Speech.Synthesis][s.s.s] namespace.

The `say` command has a [number of parameter][say],
mostly dealing with technical attributes such
as voice selection (the speaker), output of spoken text,
quality, e.t.c.

For this example, we'll stick with the default voice
of the speech synthesizer. As such, the solution
is really simple using a Powershell script:

```powershell
[cmdletbinding()]
param(
    [Parameter(Position = 1, Mandatory = $true)]
    [String]
    $message
)
Add-Type -AssemblyName System.Speech
$synth = New-Object -TypeName System.Speech.Synthesis.SpeechSynthesizer
$synth.Speak($message)
```

The `Position`-al parameter binding allow us to either call it directly:

    say.ps1 'Hello there'

Or pass is with a switch argument:

    say.ps1 -message 'Hello there'

I wish Visual Studio still had the ability to call
macros on breakpoint because the code could
translate into a one-liner in C#:

```csharp
new System.Speech.Synthesis.SpeechSynthesizer()
  .Speak("Breakpoint hit");
```

As such, one would have to wrap it first into
a method that can then get called when a breakpoint
is hit.

![Debug action with speech synthesis](/media/images/debug_say.jpg)

It would be interesting to replicate the rest of the commands,
in particular the voices since that would also
allow for proper I18N speech synthesis.

[say]: https://ss64.com/osx/say.html
[s.s.s]: https://docs.microsoft.com/en-us/dotnet/api/system.speech.synthesis
[synth]: https://docs.microsoft.com/en-us/dotnet/api/system.speech.synthesis.speechsynthesizer