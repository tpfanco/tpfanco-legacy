#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# tpfanco - controls the fan-speed of IBM/Lenovo ThinkPad Notebooks
# Copyright (C) 2011-2012 Vladyslav Shtabovenko
# Copyright (C) 2007-2008 Sebastian Urban
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject, gtk.gdk
import dbus, os
import gettext

import build, temperaturedialog

def read_preferences():
    """Reads user preferences from disk"""
    try:
        preffile = open(os.path.expanduser("~/" + build.pref_filename), "r")
        unit = preffile.readline().strip()
        do_animation = preffile.readline().strip()
        temperature_dialog.set_temperature_unit(unit)
        temperature_dialog.fanGraph.set_do_animation(do_animation == 'True')
        preffile.close()
    except IOError:
        temperature_dialog.set_temperature_unit('celcius')
        temperature_dialog.fanGraph.set_do_animation(False)
        
def write_preferences():
    """Writes user preferences to disk"""
    try:
        preffile = open(os.path.expanduser("~/" + build.pref_filename), "w")
        preffile.write(temperature_dialog.get_temperature_unit() + "\n")
        preffile.write(str(temperature_dialog.fanGraph.get_do_animation()) + "\n")
        preffile.close()            
    except IOError:
        pass
    
def celcius_to_fahrenheit(temp):
    """Converts temp from celcius to fahrenheit"""
    return float(temp) * 9./5. + 32. 

def celcius_to_celcius(temp):
    """Converts temp from celcius to celcius"""
    return temp

def multiply_list(lst, factor):
    """Multiplies every item in lst with the given factor"""
    return [x * factor for x in lst]

def init():
    global controller, act_settings, my_xml 
    global about_dialog, temperature_dialog
    global my_icon_list
    
    # i18n
    gtk.glade.bindtextdomain(build.gettext_domain, build.locale_dir)
    gtk.glade.textdomain(build.gettext_domain)
    
    # D-Bus
    system_bus = dbus.SystemBus()
    
    # try connecting to daemon
    try:
        controller_proxy = system_bus.get_object("org.thinkpad.fancontrol.tpfand", "/Control")
        controller = dbus.Interface(controller_proxy, "org.thinkpad.fancontrol.Control")
        act_settings_proxy = system_bus.get_object("org.thinkpad.fancontrol.tpfand", "/Settings")
        act_settings = dbus.Interface(act_settings_proxy, "org.thinkpad.fancontrol.Settings")
    except Exception, ex:
        print "Error connecting to tpfand: ", ex
        msgdialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                      _("Unable to connect to ThinkPad Fan Control daemon (tpfand).\n\n"
                                        "Please make sure you are running this program on a supported IBM/Lenovo ThinkPad, a recent thinkpad_acpi module is loaded with fan_control=1 and tpfand has been started."))
        msgdialog.set_title(_("ThinkPad Fan Control Configuration"))
        msgdialog.run()
        exit(1)
        
    # check required daemon version
    daemon_version = controller.get_version()
    if daemon_version < build.required_daemon_version:
        msgdialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                      _("The version of the ThinkPad Fan Control daemon (tpfand) installed on your system is too old.\n\n"
                                        "This version of tpfan-admin requires tpfand %s or later, however tpfand %s is installed on your system.") % (build.required_daemon_version, daemon_version))
        msgdialog.set_title(_("ThinkPad Fan Control Configuration"))
        msgdialog.run()
        exit(2)        

    # Load Glade file
    my_xml = gtk.glade.XML(build.data_dir + 'tpfan-admin.glade')
    
    # Load icons
    gtk.window_set_default_icon_from_file(build.data_dir + build.icon_filename)
    
    # Init dialogs        
    about_dialog = my_xml.get_widget('aboutDialog')
    temperature_dialog = temperaturedialog.TemperatureDialog()
    
    read_preferences()
