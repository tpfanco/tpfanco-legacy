# Project To-Do List #

loose collection of ideas/known bugs for the experimental versions
  * remove python-dmidecode, we can get bios, vendor etc via /sys/class/dmi/id/
  * tpfand can't read profile files properly (profile\_override=False)
  * sensor\_names list indices are strings (must be integers)!
  * add ability to load arbitrary profile files
  * machine\_id in profile
  * failure of "modprobe -r thinkpad\_acpi" should trigger reboot
  * use default hwmon sensor if ibm\_thermal is not available : /sys/devices/virtual/hwmon/hwmon0/temp1\_input
  * tpfand should be able to ouptut debug messages to a log file or to syslog
  * correction factors for hwmon?
  * move tpfand from /usr/sbin to /usr/bin
  * pygtk require (Lucid and Squeeze/Wheezy)
  * switch to Python 3 and Gtk3?
  * Lucid support must be dropped at some point (EOL 04/2013 ??)
  * ~~systemd/upstart support~~ (basic systemd support is there, upstart support is not needed anymore, since Ubuntu will drop it soon)
  * python logging module for debug output
  * implement unit tests
  * update tpfan-admin translations
  * ~~use /usr/share/pyshared only on Debian-based systems~~ (kind of solved, need proper autoconf file though)
  * A lot of work to do in tpfan-admin ...
  * Put up a binary repository on my webspace for Fedora and Debian (with proper robots.txt)
  * A CLI version of tpfan-admin would be cool ...
  * One could implement something like an optional(!!!) overheating protection, for the case that a Thinkpad in standby suddenly turns of while lying in your bag. In this case the temperatures will rise rapidly and the fan will not be able to effectively cool the CPU. Tpfanco could then put the laptop back to standby, to prevent possible damage from overheating