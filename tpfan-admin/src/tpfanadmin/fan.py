#! /usr/bin/env python
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
import gtk, gtk.glade, gobject, cairo, rsvg
from gtk import gdk
import math, time

import globals, build

class Fan(gtk.DrawingArea):
    """rotating fan graphic"""
    
    # speed
    speed = 0
    
    # speed that is currently shown
    shown_speed = 0
          
    # Rotation of shown graphic
    rotation = 0
    angle_speed = 0

    # Accel/Decel rates
    accel_rate = 0.01
    decel_factor = 0.5   
    accel_stop_diff = 0.0001
    animate_interval = 33
    
    # graphics 
    fan_border_svg = None
    fan_blades_svg = None
    
    # variables    
    last_animate_time = 0    
    last_accel_time = 0    
    do_animation = False
    
    def __init__(self, wanted_width, wanted_height):
        gtk.DrawingArea.__init__(self)
        self.set_events(gdk.EXPOSURE_MASK | gdk.BUTTON_PRESS_MASK)
        self.connect("expose_event", self.expose)
        self.connect("button_press_event", self.button_press_event)
        
        self.set_tooltip_text(_("Click to turn fan animation on/off"))                  
        
        self.set_size_request(wanted_width, wanted_height)

        self.fan_border_svg = rsvg.Handle(file = build.data_dir +  build.fan_border_filename)
        self.fan_blades_svg = rsvg.Handle(file = build.data_dir +  build.fan_blades_filename)
        
        self.set_speed(0)
        
    def set_speed(self, speed):
        """sets the speed in rpm to show"""
        self.speed = speed       
        self.last_accel_time = time.time() 
        gobject.timeout_add(self.animate_interval, self.accelerate)
        
    def get_speed(self):
        """Returns the currently shown speed"""
        return self.speed    
    
    def button_press_event(self, widget, event):
        """Mouse was clicked"""
        self.set_do_animation(not self.get_do_animation())
        globals.write_preferences()
        
    def get_do_animation(self):
        return self.do_animation
    
    def set_do_animation(self, val):
        self.do_animation = val
        if self.do_animation:
            self.last_animate_time = time.time()
            # start timers
            gobject.timeout_add(self.animate_interval, self.animate)              
            gobject.timeout_add(self.animate_interval, self.accelerate)
        
    def accelerate(self):
        if abs(self.shown_speed - self.speed) < self.accel_stop_diff:
            self.shown_speed = self.speed 
            self.angle_speed = 2 * math.pi * self.shown_speed * 60.0
            return False
        else:
            etime = time.time() - self.last_accel_time
            if self.shown_speed < self.speed:
                self.shown_speed += self.accel_rate * etime
                if self.shown_speed > self.speed:
                    self.shown_speed = self.speed
            else:
                self.shown_speed -= self.shown_speed * self.decel_factor * etime
                if self.shown_speed < self.speed:
                    self.shown_speed = self.speed
            self.angle_speed = 2 * math.pi * self.shown_speed * 60.0
            self.last_accel_time = time.time()
            return self.do_animation
        
    def animate(self):
        etime = time.time() - self.last_animate_time
        if self.angle_speed > 0.0:
            self.rotation += self.angle_speed * etime
            self.rotation = self.rotation % (2.0 * math.pi)
            self.queue_draw()        
        self.last_animate_time = time.time()
        return self.do_animation
        
    def expose(self, widget, event):
        self.context = widget.window.cairo_create()
        self.context.rectangle(event.area.x, event.area.y,
                               event.area.width, event.area.height)
        self.context.clip()
        self.draw(self.context)       
        return False
    
    def cache_graphs(self):
        self.graph_cache = [ ]
    
    def draw(self, context):
        # scale content
        space = self.get_allocation()       
        avail_size = min(space.width, space.height)
        svg_size = max(self.fan_border_svg.props.width, self.fan_border_svg.props.height)
        factor = float(avail_size) / float(svg_size)
        context.translate((space.width - self.fan_border_svg.props.width * factor) / 2.0,
                          (space.height - self.fan_border_svg.props.height * factor) / 2.0)
        context.scale(factor, factor)
        
        # draw fan border        
        self.fan_border_svg.render_cairo(context)
        
        # draw fan blades
        center_x, center_y = svg_size / 2.0, svg_size / 2.0        
        context.translate(center_x, center_y)      
        context.rotate(self.rotation)       
        context.translate(-self.fan_blades_svg.props.width / 2.0, -self.fan_blades_svg.props.height / 2.0)
        self.fan_blades_svg.render_cairo(context)
                
                
# Test case
def main():
    window = gtk.Window()
    widget = Fan(200 ,200)
    #widget.shown_speed = 0.05
    widget.set_speed(0.05)
    
    #widget.set_speed(0)
    
    window.add(widget)
    window.resize(600, 200)
    window.connect("destroy", gtk.main_quit)
    window.show_all()
    
    gtk.main()
    
if __name__ == "__main__":
    main()
    
