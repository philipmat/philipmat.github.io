---
title: Mac-like Key Remapping For Windows Users
snippet: AutoHotkey script to remap rearrange Ctrl, Alt, and Win to be more like Mac's Cmd/Option, including cursor movement.
layout: post
has_tldr: true
---

If you're like me, bouncing frequently between OS X and Windows and liking the Mac keyboard layout better, you might find yourself wanting to have the same keyboard layout in Windows as you do on the Mac, mainly having the `Control` key, which in Windows is roughly the equivalent of Mac's `Command ⌘` key, right next to the spacebar.

I'm talking about having this:

![Windows keyboard layout](/media/images/keyboard_win.jpg)

Be more like this:

![Mac keyboard layout](/media/images/keyboard_mac.jpg)

Actually, the end result will make your keyboard look like this:

![Windows keyboard remapped](/media/images/keyboard_win_new.jpg)

(Looooots of `Ctrl` keys on that way - yes, they're that important.)

I'm going to assume that you landed here because you already want to do this, so I'll touch the how part first. 
If you're wondering why, then you can skip to [Ergonomics](#ergonomics)

## Two ways: AutoHotkey or Scan-code Map

In Windows, scan-codes [map the hardware key codes to virtual keys][scancode], in other words when you press the hardware key `58`, Windows knows you pressed the left `Ctrl` key:

> In Microsoft Windows operating systems, PS/2-compatible scan codes provided 
> by an input device are converted into virtual keys, which are 
> propagated through the system in the form of Windows messages. 

These maps are controlled by Registry keys. You can dick with them yourself, but I highly recommend you use an app; I had great success with KeyTweak, which I liked because it gave me a visual layout of the keyboard and a list of keys, not hex codes, to select from. It supports normal keys, as well as special "media" keys. Scan-code maps are low-level, effective, and they work in (almost) every app. They do have some limitations, which you should be aware of:

* Changes require a system reboot;
* The maps are at system level and apply to all users (cannot use on a server where multiple folks log in, unless you're trying to mark your territory in a passive-aggressive way);
* No per-app mapping;
* Not possible to create maps on a per-keyboard basis (may be relevant if you use a laptop or different language layouts);
* It can only map the keyboard, you cannot remap mouse buttons;
* One-to-one key mapping - cannot use in or override chords.

If all you want is to turn `CapsLock` into a `Ctrl` key or even swap `Alt` and `Ctrl` around, scan-code maps are a great solution. If you'd like to take it to the next level, namely cursor movement, then you need to use [AutoHotkey][ahk]. Just be aware that AHK is an addictive, slippery slope.

You can find my AHK script on [github][gist], but I'll try within the next paragraphs to explain it a bit, in case you were curious. Let's start with the basics, ensure only one instance of this script runs, and map `CapsLock` to `Ctrl`:

	Capslock::Ctrl	
	; Alternative
	; Capslock::Win

Next: get the `Ctrl` in the right place, next to the spacebar, and use the left `Win` key for `Alt`; on the right side of the spacebar, we'll just swap `Ctrl` and `Alt` (if you're unfortunate to have a `Win` key on the right as well, just change it accordingly).

	LAlt::Ctrl
	LWin::Alt
	RAlt::Ctrl
	RCtrl::Alt

You could've gotten this far with scan-codes alone, but this is where AHK shines. I want to also emulate the OS X cursor movement [because I think it makes more sense](#ergonomics): `Alt+Left/Right` moves across words, `Cmd+Left/Right` moves to the beginning/end of line, `Cmd+Up/Down` moves to the beginning/end of document; of course, instead of `Cmd` we'll use `Ctrl`:

	!Right::Send {Blind}^{Right}
	^Right::Send {Blind}{End}
	!+Right::Send {Blind}^+{Right}
	^+Right::Send {Blind}+{End}
	
	!Left::Send {Blind}^{Left}
	^Left::Send {Blind}{Home}
	!+Left::Send {Blind}^+{Left}
	^+Left::Send {Blind}+{Home}
	
	^Up::Send {Blind}^{Home}
	^Down::Send {Blind}^{End}
	^+Up::Send {Blind}^+{Home}
	^+Down::Send {Blind}^+{End}

`!Right::Send {Blind}^{Right}` means that when `Alt+Right` is pressed AHK should send `Ctrl+Right`, thus moving the cursor right one word. `^+Right::Send {Blind}{End}` means that when `Ctrl+Shift+Right` is pressed AHK should send `Shift+End`, thus selecting to the end of the line. `{Blind}` allows us to keep pressing the arrows while holding down the modifier:
> When `{Blind}` is the first item in the string, the program avoids releasing 
	Alt/Control/Shift/Win if they started out in the down position. 
	For example, the hotkey `+s::Send {Blind}abc` would send ABC rather than 
	abc because the user is holding down the Shift key.

The key to invoke the application switcher, a.k.a. `Alt+Tab` has now physically moved one key to the left. Fortunately, OS X uses `Cmd+Tab` as shortcut, which means we can use the same physical shortcut as we used to before remapping the keys:
	
	LAlt & Tab::AltTabMenu

Finally, if you move between Lion and Windows, you might miss the (more) natural scrolling that the former introduced:

	#MaxHotkeysPerInterval 400
	WheelDown::WheelUp
	WheelUp::WheelDown

The [`#MaxHotkeysPerInterval 400`](http://www.autohotkey.com/docs/commands/_MaxHotkeysPerInterval.htm) tells AHK to accept up to 400 events in an observation interval, i.e. `#HotkeyInterval` - typically about 2 seconds, without displaying a warning; I found it necessary with Logitech's "hyper-fast scrolling" mice.


<A name="ergonomics"> </A>

## Ergonomics

I probably don't need to tell you that when it comes to modifier keys, the `Shift` is used the most (whether you write code or just text), followed by `Ctrl` and `Alt`. Using this Wikipedia page on [Table of keyboard shortcuts][shortcuts] as guide, we get the following stats:

* Windows:
    * `Ctrl` used in 52 shortcuts
    * `Alt` - 31
    * `Win` - 26
* OS X: 
    * `Ctrl` shows up in 27 shortcuts
    * `Alt`/`Option` - 3 (not quite correct as a good deal of OS X shortcuts use `Option` as a modifier on the main `Cmd+Key` action).
    * `Cmd` - 62

Now, let's do a little exercise; see which key is easier to locate and press: `Alt` - which is placed left and right to the `Space` and thus within the reach of either of your thumbs, or `Ctrl` - which, on the left side, is *maybe* in the corner of your keyboard, or maybe to the right of the `Fn` key that so many manufactures (including Apple) like to place in the corner where you expected to find `Ctrl` (on the right side, it's crap-shoot). Compare the contorted position of your hand pressing `Ctrl` with your pinky vs the relaxed position of your hand pressing `Alt` with your thumb.

(On a personal note, it's nagging me that 20% of my fingers - my two thumbs - are really in charge of a single key: the spacebar.)

The OS X layout makes a lot more sense to me: use your thumbs for the most common modifier - `Ctrl` on Windows and `Cmd` on OS X, thus not only making your hand more comfortable but also removing the 20% inefficiency.

As there's a good deal of muscle memory around using your pinky for `Ctrl` combos, you could use ancient Unix wisdom and turn your `CapsLock` into another `Ctrl` key (unless you have a burning need to be [cool](http://www.urbandictionary.com/define.php?term=caps%20lock) on the Internet).

The arrow key movement in OS X also makes more sense to me, at least from the perspective of being consistent and having everything in the same place. If you need to move anywhere in a document, one hand is on the arrow group, the other over the modifiers; you don't need to do the kind of key jockeying that Windows has you do between the arrow group and the Home/End/Page Up/Page Down group.

<A name="tldr"> </A>

## Conclusion

Given the frequency of use, the `Ctrl` key should be placed in a more prominent position. Both your thumbs are in charge or but one key, so why not make them more useful and relieve some of the contortion the normal placement of the `Ctrl` key forces your hand in.

You should consider switching your `Ctrl` and `Alt` and `Win` keys even if you're not a Mac-head because the layout is friendlier on your hands. Yes, there's muscle memory involved, but - maybe a testament to the benefit of the new layout - you'll find yourself acclimated to it in but a few days. 

You can find my [AutoHotkey][ahk] script on [github][gist]. Please feel free to contribute any addition you'd like. 

[ahk]: http://www.autohotkey.com/
[gist]: https://gist.github.com/1566393
[shortcuts]: http://en.wikipedia.org/wiki/Table_of_keyboard_shortcuts
[scancode]: http://msdn.microsoft.com/en-us/windows/hardware/gg463447 
