# Frequently asked questions #


# Where is the source code? #
To get the latest source code just check out the SVN repository of the project:
```
svn checkout http://tpfanco.googlecode.com/svn/trunk/ tpfanco-read-only 
```
Also be sure to take a look at the [Downloads section](http://code.google.com/p/tpfanco/downloads/list?can=1&q=&colspec=Filename+Summary+Uploaded+ReleaseDate+Size+DownloadCount) where you'll find tarballs and files specific to Debian packaging.

# What are the changes compared to the last version of Sebastian Urban's tp-fan? #
The initial release was uploaded to the SVN repo as it is without much comments.
Let's suppose you want to see the changes in **tpfand\_0.95-ubuntu2\_all.deb** compared to the original source **tpfand\_0.95.orig.tar.gz**. Just [download](http://code.google.com/p/tpfanco/downloads/list?can=1&q=&colspec=Filename+Summary+Uploaded+ReleaseDate+Size+DownloadCount)
**tpfand\_0.95-ubuntu2.debian.tar.gz**, extract it and check the patches folder. It lists all the changes in diff format.

# How can I submit my profile to the project? #
Start tpfan-admin and click **Submit profile**. After you hit **Yes** your profile will be saved to _/tmp/tpfand-profile/_. Please email the file to [mailto:DFEW.Entwickler@gmail.com](mailto:DFEW.Entwickler@gmail.com)  as it is.
It will be reviewed and then probably included to the tpfand-profiles package.

# Does this work with notebooks other than IBM/Lenovo Thinkpad? #
No. tp-fan controls the fan speed via thinkpad\_acpi kernel module which is only available for IBM/Lenovo Thinkpads.

# Does this work with my Thinkpad XYZ? #
This depends on whether your Thinkpad is supported by the thinkpad\_acpi kernel module. Check if the thinkpad\_acpi module is loaded at all
```
lsmod | grep thinkpad_acpi
```
and if not, try to load it by hand
```
sudo modprobe thinkpad_acpi
```
If that fails, tpfand will not work with your Thinkpad.


# I can't see any difference between certain fan levels like 15% and 30% #
Different Thinkpads have different fan levels. For example, on a Thinkpad Z61m setting 15% and 30% result into the identical fan speed. The same goes for 45% and 60%. This is a hardware limitation and not a bug of tp-fan.


# Tpfanco is acting weird. What can I do? #
If tpfanco is acting weird on your Thinkpad and you **are** sure that this is not because you configured it wrong, you might try to run tpfand in debug mode. While
running in debug mode tpfand will provide a lot of additional information that might help you to understand what's going wrong. To activate the debug mode, you must first stop tpfand daemon and then run tpfand by hand with "--debug" option
```
sudo /etc/init.d/tpfand stop
sudo /usr/sbin/tpfand --debug
```
To return to the normal operating mode, press Ctrl-C and run
```
sudo /etc/init.d/tpfand start
```

# Why do I have to restart my system after installing tp-fan packages? #
Most Thinkpads running Ubuntu usually have the thinkpad\_acpi module loaded by default. In order to be able to control the fan, tpfand requires that this module is loaded with a special parameter "fan\_control=1". To achieve this, tpfand creates a file _/etc/modprobe.d/tpfand.conf_ with the following content
```
options thinkpad_acpi fan_control=1
```
Thus, next time thinkpad\_acpi module will be loaded, it will automatically have the necessary parameter. Older tp-fan installers used to unload the module and then load it again via
```
modprobe -r thinkpad_acpi
modprobe thinkpad_acpi
```
In this case the module gets reloaded with the correct parameter and tpfand can start working without reboot. The bad thing about this behavior is that if for some reason the _modprobe -r_ fails, the whole tpfand installation will ultimately fail too. In particular, certain Ubuntu flavours (e.g. Xubuntu) don't allow to unload thinkpad\_acpi claiming that the module is in use. That's why the new installer will not attempt to reload the module but just ask the user to reboot.

If you really know what you're doing and you'd like to dodge a reboot, you can of course reload the module itself and then reload tpfand.
```
sudo rmmod thinkpad_acpi
sudo modprobe thinkpad_acpi
sudo /etc/init.d/tpfand restart
```


# How can I contact the developers? #
You can drop me an email to [mailto:DFEW.Entwickler@gmail.com](mailto:DFEW.Entwickler@gmail.com). My preferred languages are English and German. I can also read French and Russian but it might take some time for me to answer you in those languages ;)

For German speaking users a support thread in German ThinkPad-Forum.de is available:

[Projektvorstellung: Tpfanco - Wartung und Paketierung von tp-fan](http://thinkpad-forum.de/threads/121896-Projektvorstellung-Tpfanco-Wartung-und-Paketierung-von-tp-fan)