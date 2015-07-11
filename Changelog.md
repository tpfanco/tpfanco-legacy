# 2014-04-19 #
tpfan-admin (0.96.4)
  * change shebangs to python2.7, fix problems with debian packages
tpfand (0.95.3)
  * change shebangs to python2.7, fix problems with debian packages
tpfand-profiles (0.90.0)
  * add new profile for T400 (2768Z1B) (thanks to Arvid R.)

# 2012-06-27 #
tpfan-admin (0.96.3)
  * accept kdesudo as an alternative to gksudo

# 2012-06-03 #
tpfand-profiles (20120603)
  * small correction to the L420 profile (thanks to Torsten R.)

# 2012-05-21 #
tpfand-profiles (20120521)
  * add new profile for L420 (78545HG) (thanks to Torsten R.)

# 2012-04-28 #
tpfand-profiles (20120428)
  * add new profile for X121e (3045-6RG) (thanks to Ingo H.)

# 2012-03-05 #
tpfand-profiles (20120305)
  * add new profile for X300 (6478-14G) (thanks to Oliver D.)

# 2012-01-11 #

tpfan-admin (0.96.2)
  * remove interval mode
  * don't show disconnected sensors

tpfand (0.95.2)
  * fix fan pulsing on T410s (thanks to Shad for testing!)
  * remove interval mode
  * add debug mode. To activate stop tpfand ('sudo /etc/init.d/tpfand stop') and  run 'sudo /usr/sbin/tpfand --debug'

tpfand-profiles (20120111)
  * remove some profiles that contained the from now on unsuppored interval mode

# 2012-01-05 #
> tpfand-profiles (20120105)
    * add new profile for T410s (thanks to Gregor K.)
    * add new profile for X220 (thanks to gru3n3r)
    * fix [issue 5](https://code.google.com/p/tpfanco/issues/detail?id=5) (thanks to dhahler)
> > 4
# 2011-09-17 #

> tpfand (0.95-ubuntu3)
    * fix incorrect treatment of disconnected sensors

# 2011-09-03 #

> tpfand (0.95-ubuntu2)
    * first public release of the Tpfanco project
    * fixed [Launchpad Bug #623718](https://bugs.launchpad.net/tp-fan/+bug/623718). Ubuntu Lucid, Ubuntu Maverick and Ubuntu Natty are officially supported
    * fixed [Launchpad Bug #575199](https://bugs.launchpad.net/tp-fan/+bug/575199). Use dmidecode instead of hal
    * fixed [Launchpad Bug #480700](https://bugs.launchpad.net/tp-fan/+bug/480700). Install modules to /usr/pyshared/ instead of /usr/lib/python2.5/site-packages
    * fixed [Launchpad Bug #450670](https://bugs.launchpad.net/tp-fan/+bug/450670). Set polling interval from 2 s to 4 s.This should save up to 10 wakeups.

> tpfan-admin (0.96-ubuntu2)
    * first public release of the Tpfanco project
    * Ubuntu Lucid, Ubuntu Maverick and Ubuntu Natty are officially supported
    * fixed [Launchpad Bug #480700](https://bugs.launchpad.net/tp-fan/+bug/480700). Install modules to /usr/pyshared/ instead of /usr/lib/python2.5/site-packages
    * better KDE support. If KDM is detected, tpfan-admin uses kdesudo instead of gksudo
    * profiles for submitting now get saved in the /tmp/tpfand-profile directory. You must manually email the profile to the Tpfanco project

> tpfand-profiles (20110901-ubuntu2)
    * first public release of the Tpfanco project
    * add new profile for Z61m