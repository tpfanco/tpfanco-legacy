# Project News #

## 2014-04-19 ##

Now we have an official Ubuntu PPA at Launchpad
https://launchpad.net/~vl-sht/+archive/tpfanco

## 2014-03-17 ##
The experimental branch of tpfand now has some basic systemd support. Since I recently switched to Fedora from Ubuntu this was a necessity for me. I will monitor how stable this works on my X200 with Fedora 20, but since I rarely use the laptop now, it make take some time to discover bugs. I know that I need to write a proper autoconf to account for distros with sysvinit or systemd, but for now please just use "make install-sysvinit" or "make install-systemd" respectively. tpfan-admin is still not working with the new tpfand :(

## 2013-08-31 ##
Even though there was not much activity recently, I'm still working on the tpfanco in my spare time. The most changes will be occuring in the experimental branch, because the new code there is still not mature enough to be declared stable. I was also thinking that it would be nice to have some kind of compatibility list for the current and older ThinkPad models, in order to know which models have "/proc/acpi/ibm/thermal" and which not. Such a list might be also helpful for other fan control projects. I will see how to implement this in a good way.

## 2012-05-20 ##
The project is alive and doing fine. At the moment I'm very busy finishing my college studies, but I've also been working on fixing [Issue 1](https://code.google.com/p/tpfanco/issues/detail?id=1) and [Issue 2](https://code.google.com/p/tpfanco/issues/detail?id=2). So far, [Issue 2](https://code.google.com/p/tpfanco/issues/detail?id=2) is almost fixed, but [Issue 1](https://code.google.com/p/tpfanco/issues/detail?id=1) requires a significant code rewrite of tpfan-admin, which I haven't done yet. I'm also thinking about adding sensors for SMART and NVidia graphics, but don't expect this to happen too soon.