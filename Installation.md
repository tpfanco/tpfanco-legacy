# Source code #

The source code is available from our
[subversion repository](https://code.google.com/p/tpfanco/source/checkout)

# Binary Packages #

Since Google Code doesn't allow binary downloads anymore, I cannot provide packages on this site.

At the moment only deb packages are available. If you use Ubuntu or a Ubuntu-based distribution, use our official
[PPA](https://launchpad.net/~vl-sht/+archive/tpfanco) on Launchpad. Currently we support Ubuntu 12.04, 13.10 and 14.04.

If you use Debian, just download the packages from the [PPA](https://launchpad.net/~vl-sht/+archive/tpfanco) and install them one by one

# Using tpfanco #
After you install the tpfanco packages, you need to reboot your system.  Then open tpfan-admin and click **Unlock**. Select **Control system fan by software**. If there's no profile for your Thinkpad you will have to configure fan speeds by hand

# Possible confusements #

When installing _tpfand_ you might see this error
```
Fatal error: unable to set fanspeed, enable watchdog or read temperature
            Please make sure you are root and a recent
            thinkpad_acpi module is loaded with fan_control=1
                                                                        [fail]
```

And if you try to run tpfan-admin you will probably see this:
```
Unable to connect to ThinkPad Fan Control daemon (tpfand).

Please make sure you are running this program on a supported IBM/Lenovo ThinkPad,
a recent thinkpad_acpi module is loaded with fan_control=1 and tpfand has been started.
```

These errors are normal if you're installing _tpfan_ and _tpfan-admin_ for the first time. As long as the packages are installed without errors, there is nothing to be worried about. Just restart your system and all should be fine. Check the [FAQ](http://code.google.com/p/tpfanco/wiki/FAQ?ts=1315049475&updated=FAQ#Why_do_I_have_to_restart_my_system_after_installing_tp-fan_packa) for more information on why you need to restart.


# Other Linux flavors #

Currently, I don't have any plans to officially support not Debian-based distributions. The reason is that I simply do not have time to create
and test packages for the numerous distributions out there.

If you're brave, you might try to make tpfand and tpfan-admin work with your distro, but there are no warranties. Beware of debianisms!

First of all, you must install python bindings for dmidecode (usually called python-dmidecode). Without it, tpfand will not work. Unfortunately it seems that apart from Ubuntu/Debian only few other distributions like Fedora, CentOS and OpenSuse have this package in their repositories. At least, I couldn't find python-dmidecode for Mageia, Gentoo, Sabayon or Arch.

After you successfully installed python-dmidecode on your system, you can try to install tpfand
```
svn checkout http://tpfanco.googlecode.com/svn/trunk/ tpfanco-read-only
cd tpfanco-read-only/tpfand
sudo make install
/etc/init.d/tpfand restart
```
Depending on the errors you get, you will probably have to modify the tpfand init script or other parts of the package. Good luck!

# Gentoo (thanks to Maik P.) #
first check if a previous version of tpfand is running, if so kill it:
```
killall tpfand (as root))
```
install python-dmidecode:
```
wget https://launchpad.net/ubuntu/+archive/primary/+files/python-dmidecode_3.10.11.orig.tar.gz
tar -xf python-dmidecode_3.10.11.orig.tar.gz
cd python-dmidecode-3.10.11
sudo make install
```
install tpfand:
```
svn checkout http://tpfanco.googlecode.com/svn/trunk/ tpfanco-read-only
cd tpfanco-read-only/tpfand
sudo make install
sudo tpfand start
```
install tpfan-admin:
```
cd ../tpfan-admin/
```
change Makefile for python2.7 line 19 and 20 into (first two lines
below install: all)
```
install -d ${DESTDIR}/usr/lib/python2.7/site-packages/tpfanadmin
install -m 644 src/tpfanadmin/*
${DESTDIR}/usr/lib/python2.7/site-packages/tpfanadmin
```
as user run
```
make
```
then, as root run
```
make install
```
If the installation process is successful, you should run
```
tpfan-admin
```
as root to activate and configure tpfanco