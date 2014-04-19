#! /usr/bin/python2.7
# -*- coding: utf-8 -*-
#
# tpfanco - controls the fan-speed of IBM/Lenovo ThinkPad Notebooks
# Copyright (C) 2011-2012 Vladyslav Shtabovenko
# Copyright (C) 2007-2009 Sebastian Urban
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

import sys
if not ('/usr/share/pyshared' in sys.path):
    sys.path.append('/usr/share/pyshared')

import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject
import sys, os, dbus, urllib

import build, thermometer, fan, globals   

class ArgumentException(Exception):
    def __init__(self):
        pass

class TemperatureDialog:
    """main configuration dialog"""
    
    # True if we have admin rights and can change settings
    unlocked = False
    
    # True while controls are updated to show the current settings
    updating = False
    
    # Width of thermometers
    thermometer_width = 600
    
    # factor for fan speed to animation rotation speed translation 
    fan_graph_rpm_factor = 0.00001
    
    # desired window height, if screen permits it
    desired_height = 680
    
    # reserved screen height
    reserved_screen_height = 50
    
    # disclaimer accepted?
    disclaimer_accepted = False
    
    # manual configuration is currently enabled?
    override = False
        
    disclaimer_text = _("By enabling software control of the system fan, you can damage " 
                        "or shorten the lifespan of your notebook.\n\n" 
                        "IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING "
                        "WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR "
                        "REDISTRIBUTE THE PROGRAM, BE LIABLE TO YOU FOR DAMAGES, "
                        "INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING "
                        "OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED "
                        "TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY "
                        "YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER "
                        "PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE "
                        "POSSIBILITY OF SUCH DAMAGES.\n\n"
                        "Are you sure that you want to enable software control of the system fan?")
    
    override_off_warning_text = _("By disabling manual configuration your custom settings "
                                  "will be lost.\n\n"
                                  "Are you sure that you want to disable the manual configuration?")
    
    profile_submit_text = _("Submitting your fan profile to the developers of ThinkPad Fan Control "
                            "allows them to integrate it into the next version of this software.\n\n"
                            "%s\n\n"
                            "Please make sure that your notebook is quiet and not overheating "
                            "with your current settings.\n\n"
                            "Are you sure that you want to submit your profile now?")
    
    profile_model_known_text = _("A fan profile for your notebook model already exists. "
                                 "Please only submit your custom fan profile if it leads to better results "
                                 "than the non-manual configuration of ThinkPad Fan Control on "
                                 "your notebook.")
    
    profile_model_unknown_text = _("No fan profile exists for your notebook at this time. "
                                   "Your submission is appreciated.")
    
    def __init__(self):
        self.window = globals.my_xml.get_widget('temperatureDialog')
        
        self.cbEnable = globals.my_xml.get_widget('checkbuttonEnable')
        self.cbEnable.connect('toggled', self.enable_changed, None)
        
        self.cbOverride = globals.my_xml.get_widget('checkbuttonOverride')
        self.cbOverride.connect('toggled', self.override_changed, None)
        
        #self.hsIntervalDuration = globals.my_xml.get_widget('hscaleIntervalDuration')
        #self.hsIntervalDuration.connect('value-changed', self.options_changed, None)
        
        #self.hsIntervalDelay = globals.my_xml.get_widget('hscaleIntervalDelay')
        #self.hsIntervalDelay.connect('value-changed', self.options_changed, None)
        
        self.hsHysteresis = globals.my_xml.get_widget('hscaleHysteresis')
        self.hsHysteresis.connect('value-changed', self.options_changed, None)

        self.swThermometers = globals.my_xml.get_widget('scrolledwindowThermometers')
        
        self.vbThermometers = globals.my_xml.get_widget('vboxThermometers')
        self.thermos = [ ]
        for n in range(0, globals.act_settings.get_sensor_count()):
            therm = thermometer.Thermometer()
            therm.sensor_id = n
            therm.dialog_parent = self.window
            therm.set_size_request(self.thermometer_width, therm.wanted_height)
            therm.connect('trigger-changed', self.triggers_changed, n)
            therm.connect('name-changed', self.sensor_name_changed, n)
            self.thermos.append(therm)
            self.vbThermometers.pack_start(therm)
            
        self.rbCelcius = globals.my_xml.get_widget('radiobuttonCelcius')
        self.rbFahrenheit = globals.my_xml.get_widget('radiobuttonFahrenheit')
        self.rbFahrenheit.set_group(self.rbCelcius)
        self.rbCelcius.connect('toggled', self.temperature_unit_changed, None)
            
        self.eModel = globals.my_xml.get_widget('entryModel')
        self.eProfile = globals.my_xml.get_widget('entryProfile')  
        self.tvProfileComments = globals.my_xml.get_widget('textviewProfileComments')
        
        self.aFanGraph = globals.my_xml.get_widget('alignmentFanGraph')
        self.fanGraph = fan.Fan(65, 65)
        self.aFanGraph.add(self.fanGraph)
        self.fanGraph.show()
        self.lSpeed = globals.my_xml.get_widget('labelSpeed')
        self.lSpeed.set_size_request(145, -1)
        
        self.dActionArea = globals.my_xml.get_widget('dialog-action_area')
        
        self.bAbout = globals.my_xml.get_widget('buttonAbout')
        self.bAbout.connect('clicked', self.about_clicked, None)
        self.dActionArea.set_child_secondary(self.bAbout, True)
        
        self.bSubmitProfile = globals.my_xml.get_widget('buttonSubmitProfile')
        self.bSubmitProfile.connect('clicked', self.submit_profile_clicked, None)
        self.dActionArea.set_child_secondary(self.bSubmitProfile, True)
        if not build.profile_submit_enabled:
            self.bSubmitProfile.hide()
        
        self.bUnlock = globals.my_xml.get_widget('buttonUnlock')
        #self.bUnlock.connect('clicked', self.unlock_clicked, None)
        # TODO: PolicyKit integration once Python binding become available
        
        self.bClose = globals.my_xml.get_widget('buttonClose')

        self.update_model_info()
        self.update_limits()
        self.refresh_monitor()
        
        for therm in self.thermos:
            therm.end_animation()
        
        gobject.timeout_add(5000, self.refresh_monitor)
        
        # calculate initial size
        width, height = self.window.get_size()
        screen_height = gtk.gdk.screen_height()
        height = min(screen_height - self.reserved_screen_height, self.desired_height)
        self.window.resize(width, height)
        
    def about_clicked(self, widget, data=None):
        """About was clicked"""
        ctext = _("Monitors the temperature and controls the \n"
                  "fan-speed of IBM/Lenovo ThinkPad Notebooks")
        text = _("Daemon (tpfand) version: %s\nGTK+ configuration UI (tpfan-admin) version: %s\n\n") % (globals.controller.get_version(), build.version) + ctext
        globals.about_dialog.set_comments(text)
        globals.about_dialog.set_transient_for(self.window)
        globals.about_dialog.set_logo(None)
        globals.about_dialog.run()
        globals.about_dialog.hide()
        
    def submit_profile_clicked(self, widget, data=None):
        """Submit profile... was clicked"""
        if globals.act_settings.is_profile_exactly_matched():
            submit_text = self.profile_submit_text % self.profile_model_known_text
        else:
            submit_text = self.profile_submit_text % self.profile_model_unknown_text
        submit_dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_QUESTION,
                                          buttons=gtk.BUTTONS_YES_NO,
                                          message_format=submit_text)
        if submit_dialog.run() == gtk.RESPONSE_YES:
            profile = globals.act_settings.get_profile_string()            
            model_info = globals.act_settings.get_model_info()
            path = '/tmp/tpfand-profile/' + model_info['vendor'].lower() + '_' + model_info['id'].lower()
            if not os.path.exists('/tmp/tpfand-profile'):
              os.makedirs('/tmp/tpfand-profile')            
            f = open(path,'w')            
            f.write(str(profile))
            f.close()            
        submit_dialog.destroy()
        
    def check_unlocked(self):
        """Checks, if we have admin rights"""
        # try calling set_settings to see if it is allowed
        try:
            # we have to put something in the settings dict, otherwise we get a
            # "Unable to guess signature from an empty dict" error from DBus, 
            # so we just try to set a non-existant setting 
            globals.act_settings.set_settings({'dummy': 0})
            self.unlocked = True
        except dbus.exceptions.DBusException:
            # not allowed
            self.unlocked = False            
        
    def update_sensor_names(self):
        """Updates the shown sensor names from the settings"""
        if not self.updating:    
            self.updating = True
            names = globals.act_settings.get_sensor_names()
            for n in range(0, len(self.thermos)):
                therm = self.thermos[n]
                therm.set_sensor_name(names[n])
            self.updating = False
                
    def update_triggers(self):
        """Updates the shown triggers from the settings"""
        if not self.updating:    
            self.updating = True
            triggers = globals.act_settings.get_trigger_points()
            for n in range(0, len(self.thermos)):
                therm = self.thermos[n]
                therm.set_triggers(triggers[n])
            self.updating = False
            
    def update_temperature_unit(self):
        """Updates the temperature unit"""
        if not self.updating:
            self.updating = True
            if self.temperature_unit == 'celcius':
                self.rbCelcius.set_active(True)
                cfunc = globals.celcius_to_celcius
                decs = 0
            elif self.temperature_unit == "fahrenheit":
                self.rbFahrenheit.set_active(True)
                cfunc = globals.celcius_to_fahrenheit
                decs = 1
            else:
                print "Unknown temperature unit: ", self.temperature_unit
            
            for therm in self.thermos:
                therm.set_temp_convert_func(cfunc, decs)           
            
            self.updating = False
            
    def update_settings(self):
        """Updates the shown options from the settings"""
        if not self.updating:
            self.updating = True
            opts = globals.act_settings.get_settings()
            if bool(opts['enabled']) == True:
                self.disclaimer_accepted = True
            self.cbEnable.set_active(bool(opts['enabled']))
            self.cbOverride.set_active(bool(opts['override_profile']))
            #self.hsIntervalDuration.set_value(opts['interval_duration'] / 1000.0)
            #self.hsIntervalDelay.set_value(opts['interval_delay'] / 1000.0)
            self.hsHysteresis.set_value(opts['hysteresis'])
            self.update_sensitivity()
            if self.cbOverride.get_active() == True:
                self.eProfile.set_text(_("No profile is used because you enabled manual configuration."))
                comment = ""
            else:
                self.eProfile.set_text(self.profile_list)
                comment = globals.act_settings.get_profile_comment()
            self.tvProfileComments.get_buffer().set_text(comment)            
            self.updating = False
        
    def update_limits(self):
        """Updates the limits for the settings"""
        if not self.updating:
            self.updating = True
            self.hsHysteresis.set_range(*globals.act_settings.get_setting_limits('hysteresis'))
            #self.hsIntervalDelay.set_range(*globals.multiply_list(globals.act_settings.get_setting_limits('interval_delay'), 1.0/1000.0))
            #self.hsIntervalDuration.set_range(*globals.multiply_list(globals.act_settings.get_setting_limits('interval_duration'), 1.0/1000.0))
            self.updating = False
        
    def update_model_info(self):
        """Updates the shown model info"""
        model_info = globals.act_settings.get_model_info()
        self.eModel.set_text("%s %s (%s)" % (model_info['vendor'], model_info['name'], model_info['id']))
        loaded_profiles = globals.act_settings.get_loaded_profiles()
        if len(loaded_profiles) == 1:
            lp = str(loaded_profiles[0])
        else:
            # skip generic if profiles are loaded
            lp = ""
            for x in loaded_profiles[1:]:
                if lp != "":
                    lp += ", "
                lp += str(x) 
        self.profile_list = lp
                
    def run(self):
        """shows the temperature dialog"""
        self.check_unlocked()
        self.update_settings()
        self.update_sensor_names()
        self.update_triggers()
        self.update_sensitivity()
        retval = 0 # 1 = close, 2 = unlock
        while (not (retval == 1 or retval == 2 or retval == gtk.RESPONSE_DELETE_EVENT)):
            retval = self.window.run()
        self.window.destroy()
        if retval == 2:
            # ugly hack: will be removed when PolicyKit bindings for Python
            #            become available
            # try running ourselves as root
            os.execvp(build.run_as_root_cmd, build.run_as_root_args)
        
    def update_sensitivity(self):
        """sets if settings are changeable"""
        if self.unlocked:
            self.bUnlock.set_label(_("Unlocked"))
            self.bUnlock.set_sensitive(False)
            if self.cbEnable.get_active():
                self.cbOverride.set_sensitive(True)
                self.set_profile_override_controls_sensitivity(self.cbOverride.get_active())
            else:
                self.cbOverride.set_sensitive(False)
                self.set_profile_override_controls_sensitivity(False)
        else:
            self.bUnlock.set_label(_("Unlock"))
            self.bUnlock.set_sensitive(True)     
            self.cbEnable.set_sensitive(False)       
            self.cbOverride.set_sensitive(False)
            self.set_profile_override_controls_sensitivity(False)        
        
        self.bSubmitProfile.set_sensitive(self.cbOverride.get_active())
        
        for therm in self.thermos:
            therm.set_show_triggers(self.cbEnable.get_active())
                                                    
    def set_profile_override_controls_sensitivity(self, override):
        """sets if profile settings are configurable by user"""
        #for control in [self.hsIntervalDuration, self.hsIntervalDelay, self.hsHysteresis] + self.thermos:
        for control in [self.hsHysteresis] + self.thermos:
            control.set_sensitive(override)
          
    def set_temperature_unit(self, unit):
        if unit == 'celcius':
            self.temperature_unit = 'celcius'
        elif unit == 'fahrenheit':
            self.temperature_unit = 'fahrenheit'
        else:
            raise ArgumentException()
        self.update_temperature_unit() 
        globals.write_preferences()
    
    def get_temperature_unit(self):
        return self.temperature_unit
    
    def temperature_unit_changed(self, widget, data=None):
        if self.rbCelcius.get_active():
            self.temperature_unit = 'celcius'
        else:
            self.temperature_unit = 'fahrenheit'
        self.update_temperature_unit()
        globals.write_preferences()   
        
    def enable_changed(self, widget, data=None):
        """the user has changed the enabled option"""
        # show disclaimer
        if self.unlocked and self.cbEnable.get_active() and not self.disclaimer_accepted:
            disclaimer_dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_WARNING,
                                                  buttons=gtk.BUTTONS_YES_NO,
                                                  message_format=self.disclaimer_text)
            if disclaimer_dialog.run() == gtk.RESPONSE_YES:
                self.disclaimer_accepted = True
            else:
                self.cbEnable.set_active(False)  
            disclaimer_dialog.destroy()          
        self.options_changed(widget, data)
        
    def override_changed(self, widget, data=None):
        """the user has changed the override option"""
        # show warning
        if self.override and not self.cbOverride.get_active():
            warning_dialog = gtk.MessageDialog(parent=self.window, type=gtk.MESSAGE_WARNING,
                                               buttons=gtk.BUTTONS_YES_NO,
                                               message_format=self.override_off_warning_text)
            if warning_dialog.run() != gtk.RESPONSE_YES:
                self.cbOverride.set_active(True)  
            warning_dialog.destroy()
        self.override = self.cbOverride.get_active()          
        self.options_changed(widget, data)        
        
    def options_changed(self, widget, data=None):
        """the user has changed an option"""
        if self.unlocked and not self.updating:
            opts = { }
            opts['enabled'] = int(self.cbEnable.get_active())
            opts['override_profile'] = int(self.cbOverride.get_active())
            if self.cbOverride.get_active():
                #opts['interval_duration'] = self.hsIntervalDuration.get_value() * 1000.0
                #opts['interval_delay'] = self.hsIntervalDelay.get_value() * 1000.0
                opts['hysteresis'] = self.hsHysteresis.get_value()
            globals.act_settings.set_settings(opts)
            globals.controller.reset_trips()
        self.update_settings()
        self.update_triggers()
        self.update_sensor_names()
        
    def triggers_changed(self, widget, sensor_id):
        """the user has changed a trigger temperature"""
        if self.unlocked and not self.updating:
            therm = self.thermos[sensor_id]
            triggers = globals.act_settings.get_trigger_points()
            triggers[sensor_id] = therm.get_triggers()
            globals.act_settings.set_trigger_points(triggers)
            globals.controller.reset_trips()
        self.update_triggers()
        self.refresh_monitor()
        
    def sensor_name_changed(self, widget, sensor_id):
        """the user has changed a sensor name"""
        if self.unlocked and not self.updating:
            therm = self.thermos[sensor_id]
            names = globals.act_settings.get_sensor_names()
            names[sensor_id] = therm.get_sensor_name()
            globals.act_settings.set_sensor_names(names)
        self.update_sensor_names()
        
    def refresh_monitor(self):
        """Refreshes the temperature/fan monitor"""
        # temperatures
        temps = globals.controller.get_temperatures()
        hys_temps, hys_levels = globals.controller.get_trip_temperatures(), globals.controller.get_trip_fan_speeds()
        for n in range(0, len(temps)):
            if abs(temps[n]) in [-128, 128, 0]:
                self.thermos[n].hide()
            else:
                self.thermos[n].show()
                self.thermos[n].set_temperature(temps[n])
                if n in hys_temps:
                    self.thermos[n].set_hysteresis_temperature(hys_temps[n], hys_levels[n])
                else:
                    self.thermos[n].set_hysteresis_temperature(None, None)

        # fan speed
        try:
            fan_state = globals.controller.get_fan_state()
            rpm = fan_state['rpm']
            try:
                level = " (" + self.thermos[0].trigger_names[fan_state['level']] + ")"
            except:
                level = ""
            self.fanGraph.set_speed(rpm * self.fan_graph_rpm_factor)
            self.lSpeed.set_text(_("%d RPM%s") % (rpm, level))
        except:
            self.lSpeed.set_text(_("Unknown"))
        
        return True
    
        
        
