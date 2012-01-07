#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# tp-fancontrol - controls the fan-speed of IBM/Lenovo ThinkPad Notebooks
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
import gtk, gtk.glade, gobject
from gtk import gdk
import math

import globals

class Thermometer(gtk.DrawingArea):
    
    max_temp = 90.
    min_temp = 10.
    scale_interval = 10.
    animate_interval = 30
    animate_step = 0.3
    unit = "°C"
    
    # maps temperatures to fan levels
    triggers = { 0: 0 }
    
    shown_temp = min_temp
    temperature = min_temp
    
    hysteresis_temp = None
    hysteresis_level = None
    
    sensor_name = ""
    sensor_name_x = 0
    sensor_name_y = 0
    sensor_name_width = 0
    sensor_name_height = 0
    sensor_id = 0

    translate_x = 5
    translate_y = 5
    
    Rkreis = 14.0
    Rrohr = 6.0
    wanted_height = int(2 * Rkreis + 15) 
    
    draw_temperature_unit = False
    draw_triggers = True
    
    dragging = False
    mouse_over_temp = None  
    
    temp_convert_func = None  
    
    decimals = 1
    
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.set_events(gdk.EXPOSURE_MASK | gdk.POINTER_MOTION_MASK | gdk.POINTER_MOTION_HINT_MASK |
                        gdk.BUTTON_MOTION_MASK | gdk.BUTTON_PRESS_MASK | gdk.BUTTON_RELEASE_MASK)
        self.connect("expose_event", self.expose)
        self.connect("motion_notify_event", self.motion_notify_event)
        self.connect("button_press_event", self.button_press_event)
        self.connect("button_release_event", self.button_release_event)

        self.normal_cursor = gdk.Cursor(gdk.ARROW)
        self.move_cursor = gdk.Cursor(gdk.SB_H_DOUBLE_ARROW)
        self.cross_cursor = gdk.Cursor(gdk.CROSS)
        self.hand_cursor = gdk.Cursor(gdk.HAND2)

        self.trigger_names = { 0: _("off"),
                               2: _("15%"),
                               3: _("30%"),
                               4: _("45%"),
                               5: _("60%"),
                               6: _("75%"),
                               7: _("90%"),
                               8: _("100%"),
                               255: _("hw-ctrld"),
                               256: _("full")}
        
        # build popup menu
        self.popup_menu = gtk.Menu()
        self.trigger_popup_menu_items = { }
        keys = self.trigger_names.keys()
        keys.sort()
        for id in keys:
             item = gtk.MenuItem(self.trigger_names[id])
             self.trigger_popup_menu_items[id] = item
             self.popup_menu.append(item)
             item.connect_object("activate", self.popup_menu_event, str(id))
             item.show()
             
        seperator = gtk.SeparatorMenuItem()
        self.popup_menu.append(seperator)
        seperator.show()
        
        self.popup_menu_split = gtk.MenuItem(_("Split"))
        self.popup_menu.append(self.popup_menu_split)
        self.popup_menu_split.connect_object("activate", self.popup_menu_event, 'split')
        self.popup_menu_split.show()
             
        self.popup_menu_remove = gtk.MenuItem(_("Remove"))
        self.popup_menu.append(self.popup_menu_remove)
        self.popup_menu_remove.connect_object("activate", self.popup_menu_event, 'remove')
        self.popup_menu_remove.show()
        
        self.sensor_name_dialog = globals.my_xml.get_widget('sensornameDialog')
        self.sensor_name_entry = globals.my_xml.get_widget('entrySensorName')
        self.sensor_name_entry_title = globals.my_xml.get_widget('labelTitle')
        
        self.set_temp_convert_func(lambda T: T, 0)
        self.set_temperature(50)
        self.verify_level_order(False)
        
        self.set_size_request(100, self.wanted_height)   
        
    def set_temp_convert_func(self, func, decimals):
        """sets the function that converts the temperature from celcius"""
        self.temp_convert_func = lambda T: func(T)
        self.decimals = decimals
        self.queue_draw()
        
    def set_show_triggers(self, show):
        """Sets if triggers should be shown"""
        self.draw_triggers = show
        self.queue_draw()
        
    def set_sensor_name(self, name):
        """Sets the sensor name to show"""
        if self.sensor_name != name:
            self.sensor_name = name
            self.queue_draw()
        
    def get_sensor_name(self):
        """returns the sensor name"""
        return self.sensor_name
        
    def set_temperature(self, temp):
        """Sets the temperature to show"""
        if self.temperature != temp:
            self.temperature = temp
            gobject.timeout_add(self.animate_interval, self.animate_temperature)
        
    def get_temperature(self):
        """Returns the currently shown temperature"""
        return self.temperature
    
    def set_hysteresis_temperature(self, temp, level):
        """Sets the hysteresis turn off temperature and level"""
        if self.hysteresis_temp != temp or self.hysteresis_level != level:
            self.hysteresis_temp = temp
            self.hysteresis_level = level
            self.queue_draw()
    
    def set_triggers(self, trig):
        """Sets the fan level triggers"""
        self.triggers = trig
        self.verify_level_order(False)
        self.queue_draw()
        
    def get_triggers(self):
        """Gets the fan level triggers"""
        return self.triggers  
    
    def end_animation(self):
        """Ends temperature animation"""
        self.shown_temp = self.temperature
        
    def popup_menu_event(self, event):
        if event == 'split':
            next_temp, dummy = self.get_key_higher_than(self.triggers, self.current_popup_temperature)
            if next_temp == None:
                temp = self.current_popup_temperature + 3
            else:
                temp = round((self.current_popup_temperature + next_temp) / 2.0)
            if temp >= self.min_temp and temp <= self.max_temp:
                self.triggers[temp] = 0
            self.verify_level_order(False)
        elif event == 'remove':
            if len(self.triggers.keys()) > 2: 
                del self.triggers[self.current_popup_temperature]
            self.verify_level_order(False)
        else:
            level = int(event)
            from_right = level < self.triggers[self.current_popup_temperature] 
            self.triggers[self.current_popup_temperature] = level
            self.verify_level_order(from_right)
        self.queue_draw()
        self.emit('trigger_changed')
        
    def verify_level_order(self, from_right):
        if 0 not in self.triggers.keys() or self.triggers[0] != 0:
            self.triggers[0] = 0
            self.emit('trigger_changed')
        if len(self.triggers.keys()) < 2:
            self.triggers[self.min_temp + 5] = 255
            self.emit('trigger_changed')
            
        temps = self.triggers.keys()
        if from_right:
            temps.sort(cmp=lambda x,y: -cmp(x,y))
            min_level = 256
            for temp in temps:
                if self.triggers[temp] <= min_level:
                    min_level = self.triggers[temp]
                else:
                    self.triggers[temp] = min_level
                    self.emit('trigger_changed')
        else:
            temps.sort(cmp=lambda x,y: cmp(x,y))
            max_level = 0
            for temp in temps:
                if self.triggers[temp] >= max_level:
                    max_level = self.triggers[temp]
                else:
                    self.triggers[temp] = max_level
                    self.emit('trigger_changed')
        
    def motion_notify_event(self, widget, event):
        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.state
            
        x -= self.translate_x
        y -= self.translate_y
            
        cursor = self.normal_cursor
        temp = self.pos_to_temp(x)
        if y >= self.Rkreis - self.Rrohr and y <= self.Rkreis + self.Rrohr and temp >= self.min_temp and temp <= self.max_temp:
            if self.dragging:
                self.drag_temp = min(self.drag_max_temp, max(self.drag_min_temp, temp))
                cursor = self.move_cursor
                self.queue_draw()
            else:
                if y >= self.Rkreis - self.Rrohr and y <= self.Rkreis + self.Rrohr:
                    self.mouse_over_temp = round(temp)
                    temp, level = self.get_key_lower_than(self.triggers, self.mouse_over_temp)            
                    if self.mouse_over_temp in self.triggers:
                        cursor = self.move_cursor                        
                    elif temp:
                        cursor = self.hand_cursor
                    else:
                        cursor = self.normal_cursor
        else:
            self.mouse_over_temp = 0
                        
        if x >= self.sensor_name_x and x <= self.sensor_name_x + self.sensor_name_width and y <= self.sensor_name_y and y >= self.sensor_name_y - self.sensor_name_height:
            self.mouse_over_sensor_name = True
            cursor = self.hand_cursor
        else:
            self.mouse_over_sensor_name = False

        self.window.set_cursor(cursor)
        return True
               
    def button_press_event(self, widget, event):
        if event.button == 1 and self.mouse_over_temp and not self.dragging and self.mouse_over_temp in self.triggers:
            # start dragging
            self.dragging = True
            self.drag_temp = self.mouse_over_temp
            self.drag_min_temp, dummy = self.get_key_lower_than(self.triggers, self.drag_temp)
            if self.drag_min_temp == None:
                self.drag_min_temp = self.min_temp
            self.drag_max_temp, dummy = self.get_key_higher_than(self.triggers, self.drag_temp)
            if self.drag_max_temp == None:
                self.drag_max_temp = self.max_temp                 
            self.drag_level = self.triggers[self.drag_temp]
            del self.triggers[self.drag_temp]
        elif event.button == 1 and self.mouse_over_sensor_name:
            # change sensor name
            self.sensor_name_entry_title.set_text(_("Name for temperature sensor %d") % self.sensor_id)
            self.sensor_name_entry.set_text(self.sensor_name)
            self.sensor_name_entry.grab_focus()
            self.sensor_name_entry.select_region(0,100)
            self.sensor_name_dialog.set_transient_for(self.dialog_parent)
            if self.sensor_name_dialog.run() == 1:      # OK was pressed
                self.sensor_name = self.sensor_name_entry.get_text()
                self.queue_draw()   
                self.emit('name_changed')
            self.sensor_name_dialog.hide()
        elif event.button == 1 and self.mouse_over_temp and not self.dragging:
            temp, level = self.get_key_lower_than(self.triggers, self.mouse_over_temp)
            if temp:
                # show popup menu
                self.current_popup_temperature = temp
                for id in self.trigger_popup_menu_items.iterkeys():
                    self.trigger_popup_menu_items[id].set_sensitive(not id == level)
                self.popup_menu_remove.set_sensitive(len(self.triggers) > 2)
                self.popup_menu.popup(None, None, None, event.button, event.get_time())

        return True                
    
    def button_release_event(self, widget, event):
        if event.button == 1 and self.dragging:
            self.dragging = False
            goal_temp = round(self.drag_temp)
            if goal_temp in self.triggers:
                if goal_temp == self.drag_min_temp:
                    self.triggers[goal_temp] = self.drag_level                
            else:
                self.triggers[goal_temp] = self.drag_level
            self.mouse_over_temp = round(self.drag_temp)   
            self.emit('trigger_changed')                    
        return True    
        
    def animate_temperature(self):
        if abs(self.shown_temp - self.temperature) < self.animate_step:
            self.shown_temp = self.temperature
            self.queue_draw()
            return False
        else:
            if self.shown_temp < self.temperature:
                self.shown_temp += self.animate_step
            else:
                self.shown_temp -= self.animate_step
            self.queue_draw()
            return True
        
    def expose(self, widget, event):
        self.context = widget.window.cairo_create()
        self.context.rectangle(event.area.x, event.area.y,
                               event.area.width, event.area.height)
        self.context.clip()
        self.draw(self.context)
        
        return False
    
    def draw(self, context):
        space = self.get_allocation()
        self.Lrohr = space.width - 2 * self.Rkreis - self.Rrohr - 20    
        
        Rrohr = self.Rrohr        
        scale_length = 6
        scale_space = 2
        phi = math.asin(Rrohr / self.Rkreis)       
        phi_empty = math.asin((Rrohr * 2.) / self.Rkreis)
        
        context.translate(self.translate_x, self.translate_y)
        
        # fill
        if self.shown_temp >= self.min_temp:
            context.arc(self.Rkreis, self.Rkreis, self.Rkreis, phi, 2 * math.pi - phi)      
            context.line_to(self.temp_to_pos(self.shown_temp), self.Rkreis - Rrohr)
            context.line_to(self.temp_to_pos(self.shown_temp), self.Rkreis + Rrohr)
        else:
             context.arc(self.Rkreis, self.Rkreis, self.Rkreis, phi_empty, 2 * math.pi - phi_empty)      
        context.set_source_rgb(1, 0, 0)
        context.fill()
                
        # draw temperatures
        context.new_path()
        text = ("%." + str(self.decimals) + "f") % self.temp_convert_func(self.temperature)
        x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = context.text_extents(text)
        context.move_to(self.Rkreis - text_width/2.0, self.Rkreis + text_height/2.0)
        context.set_source_rgb(0, 0, 0)
        context.show_text(text)
        context.stroke()
        
        # draw sensor name
        context.new_path()
        text = self.sensor_name
        x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = context.text_extents(text)
        self.sensor_name_x = 2 * self.Rkreis
        if len(text.strip()) > 0:
            self.sensor_name_y = self.Rkreis + Rrohr + scale_space + text_height            
            self.sensor_name_width = text_width
            self.sensor_name_height = text_height
        else:
            self.sensor_name_y = self.Rkreis + Rrohr + scale_space +  10
            self.sensor_name_width = 30
            self.sensor_name_height = 10              
        context.move_to(self.sensor_name_x, self.sensor_name_y)
        context.set_source_rgb(0, 0, 1)
        context.show_text(text)
        context.stroke()       
        context.set_source_rgb(0, 0, 0)     
        
        # draw unit
        if self.draw_temperature_unit:
            context.new_path()
            text = self.unit
            x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = context.text_extents(text)
            context.move_to(2 * self.Rkreis + self.Lrohr - text_width/2, self.Rkreis - Rrohr - scale_space)
            context.show_text(text)
            context.stroke()            
        
        # draw scale
        for i in range(1, int(math.ceil((self.max_temp + 1 - self.min_temp) / self.scale_interval))):
            n = i * self.scale_interval + self.min_temp
            context.new_path()
            context.move_to(self.temp_to_pos(n), self.Rkreis + Rrohr)
            context.rel_line_to(0, +scale_length)
            context.set_source_rgb(0, 0, 0)
            context.stroke()         
            
            text = ("%." + str(self.decimals) + "f") % self.temp_convert_func(n)
            x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = context.text_extents(text)
            context.move_to(self.temp_to_pos(n) - text_width / 2, self.Rkreis + Rrohr + scale_length + text_height + scale_space)
            context.show_text(text)
            context.stroke()
            
        if self.draw_triggers:
            if self.hysteresis_temp != None:
                # find matching temperature for fan level
                temps = [x for x in self.triggers.keys() if self.triggers[x] == self.hysteresis_level]
                if len(temps) > 0:
                    temp = temps[0]
                    # draw hysteresis trigger        
                    context.new_path()
                    context.move_to(self.temp_to_pos(self.hysteresis_temp - 0.5), self.Rkreis - Rrohr)
                    context.line_to(self.temp_to_pos(temp), self.Rkreis - Rrohr)
                    context.line_to(self.temp_to_pos(temp), self.Rkreis + Rrohr)
                    context.line_to(self.temp_to_pos(self.hysteresis_temp - 0.5), self.Rkreis + Rrohr)
                    context.set_source_rgba(0.9, 0.9, 0, 0.5)
                    context.fill()   
                            
            # draw trigger markers
            draw_triggers = self.triggers.copy()
            if self.dragging and (round(self.drag_temp) not in draw_triggers or round(self.drag_temp) == self.drag_min_temp):
                draw_triggers[self.drag_temp] = self.drag_level
            temp, level = self.get_key_higher_than(draw_triggers, -1)
            first = True
            while temp != None:
                if temp >= self.min_temp:
                    # draw marker
                    context.new_path()
                    context.move_to(self.temp_to_pos(temp), self.Rkreis - Rrohr)
                    context.rel_line_to(0, 2 * Rrohr)
                    context.set_source_rgb(0, 0, 1)
                    context.stroke()
        
                    # draw marker temperature
                    text = ("%." + str(self.decimals) + "f") % self.temp_convert_func(round(temp))
                    x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = context.text_extents(text)
                    context.move_to(self.temp_to_pos(temp) - text_width / 2, self.Rkreis - Rrohr - scale_space)
                    context.set_source_rgb(0, 0, 0)
                    context.show_text(text)
                    context.stroke()
                
                # draw level text
                new_temp, new_level = self.get_key_higher_than(draw_triggers, temp)
                if new_temp != None:
                    level_pos = (new_temp + max(temp, self.min_temp)) / 2.
                    avail_width = self.temp_to_pos(new_temp) - self.temp_to_pos(max(temp, self.min_temp)) - 3
                else:
                    level_pos = (self.max_temp + max(temp, self.min_temp)) / 2.
                    avail_width = self.temp_to_pos(self.max_temp) - self.temp_to_pos(max(temp, self.min_temp)) - 3
                
                text = self.trigger_names[level]                
                font_size = 9 + 1
                text_width = 99999
                old_font_matrix = context.get_font_matrix()
                while font_size > 1 and text_width > avail_width:
                    font_size = font_size - 1
                    context.set_font_size(font_size)
                    x_bearing, y_bearing, text_width, text_height, x_advance, y_advance = context.text_extents(text)
                
                context.move_to(self.temp_to_pos(level_pos) - text_width / 2, self.Rkreis + text_height / 2)
                if first:
                    context.set_source_rgb(0, 0, 0)
                    first = False
                else:
                    context.set_source_rgb(0, 0, 1)
                context.show_text(text)
                context.stroke()           
                context.set_font_matrix(old_font_matrix)
                    
                temp, level = new_temp, new_level  
                
        # border
        context.arc(self.Rkreis, self.Rkreis, self.Rkreis, phi, 2 * math.pi - phi)      
        context.line_to(2 * self.Rkreis + self.Lrohr, self.Rkreis - Rrohr)
        context.arc(2 * self.Rkreis + self.Lrohr, self.Rkreis, Rrohr, 3./2. * math.pi, 1./2. * math.pi)
        context.close_path()     
        context.set_source_rgb(0, 0, 0)
        context.stroke()                             

    def get_key_lower_than(self, dict, higher_bound):
        highest_key = None
        highest_value = None
        for key, value in dict.iteritems():
            if key < higher_bound and (highest_key == None or key > highest_key):
                highest_key, highest_value = key, value
        return highest_key, highest_value
            
    def get_key_higher_than(self, dict, lower_bound):
        lowest_key = None
        lowest_value = None
        for key, value in dict.iteritems():
            if key > lower_bound and (lowest_key == None or key < lowest_key):
                lowest_key, lowest_value = key, value
        return lowest_key, lowest_value           

    def temp_to_pos(self, temp):
        if temp < self.min_temp:
            return self.temp_to_pos(self.min_temp)
        elif temp > self.max_temp:
            return self.temp_to_pos(self.max_temp)
        else:
            return 2 * self.Rkreis + (temp - self.min_temp) * self.Lrohr / (self.max_temp - self.min_temp)
        
    def pos_to_temp(self, pos):
        return (pos - 2 * self.Rkreis) / (self.Lrohr / (self.max_temp - self.min_temp)) + self.min_temp
        
# Register signals
gobject.signal_new('trigger_changed', Thermometer, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
gobject.signal_new('name_changed', Thermometer, gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        
# Test case
def main():
    window = gtk.Window()
    widget = Thermometer()
    
    window.add(widget)
    window.resize(600, 200)
    window.connect("destroy", gtk.main_quit)
    window.show_all()
    
    gtk.main()
    
if __name__ == "__main__":
    main()
    
