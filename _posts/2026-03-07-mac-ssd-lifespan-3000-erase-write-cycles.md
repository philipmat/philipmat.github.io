---
layout: post
title: "How long will my Mac’s SSD last? About 3000 erase-write cycles"
tags: [ssd, mac, storage, smartmontools]
snippet: "Modern Mac SSDs typically endure about 3,000 erase-write cycles; monitor total data written with iostat or smartctl, keep 10–25% free, and avoid VM swap to extend lifespan."
---

<blockquote>

**Key points**

* SSDs wear out differently from hard disks.
* Expect modern Mac internal SSDs to wear out after at least 3,000 erase-write cycles.
* To monitor wear, measure the total data written to the SSD.
* Expect an internal SSD to wear out when that total reaches 3,000 times the total capacity of the SSD.
* For a given amount of data written to an SSD, the larger the total capacity of the SSD, the slower it will wear out.
* Keep at least 10% of the SSD free at all times, with 15-25% even better.
* Ensure your Mac has sufficient memory to never use VM swap space.
</blockquote>

hoakley in [How long will my Mac’s SSD last?](https://eclecticlight.co/2026/02/26/how-long-will-my-macs-ssd-last/)

How to find out where I am in that cycle? 

## [Version 1](https://apple.stackexchange.com/a/336675): use `iostat` and some math.

```sh
$ iostat -Id disk0
              disk0
    KB/t xfrs   MB
   19.02 36987892 686874.89
```
The MB column is "total number of megabytes transferred" (since the disk was installed).

So 686.87 GB, in my case. My disc is 1TB and that means I'm not even fully through one of those 3k cycles.  
This seems low and hurts my developer pride, so let's try another approach.

## [Version 2](https://apple.stackexchange.com/a/336688): using `smartmontools`

[smartmontools](https://www.smartmontools.org/) is an open source project and can be installed using `brew install smartmontools`.

It installs multiple utilities and the one that's of interest is `smartctl`:

```sh
$ smartctl -a disk0
...
Available Spare:                    100%
Available Spare Threshold:          99%
Percentage Used:                    1%
Data Units Read:                    217,642,465 [111 TB]
Data Units Written:                 70,672,272 [36.1 TB]
...
```

Much more "respectable" numbers. The 36.1 TB is about 1% of those 3000 x 1 TB, and it's also conveniently displayed in the "Percentage Used" column.

"Available Spare" is the percentage of the remaining spare capacity available for use. As the SSD wears down this could see a decrease, although the _Disk Utility_ might continue to report the same size for the disk.

(Thanks [MacWorld](https://www.macworld.com/article/334283/how-to-m1-intel-mac-ssd-health-terminal-smartmontools.html) for the instructions and descriptions.)
