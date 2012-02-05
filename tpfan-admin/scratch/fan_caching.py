#! /usr/bin/python
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

import sys
if not ('/usr/share/pyshared' in sys.path):
    sys.path.append('/usr/share/pyshared')

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

    # images to cache
    graph_cache_images = 360
    
    # variables    
    last_animate_time = 0    
    last_accel_time = 0    
    graph_cache_width = 0
    graph_cache_height = 0
    graph_cache = [ ] 
    
    def __init__(self, wanted_width, wanted_height):
        gtk.DrawingArea.__init__(self)
        self.set_events(gdk.EXPOSURE_MASK)
        self.connect("expose_event", self.expose)
        self.connect("size_allocate", self.size_allocate)
        
        self.set_size_request(wanted_width, wanted_height)

        self.fan_border_svg = rsvg.Handle(file = build.data_dir +  build.fan_border_filename)
        self.fan_blades_svg = rsvg.Handle(file = build.data_dir +  build.fan_blades_filename)

        self.last_animate_time = time.time()
        gobject.timeout_add(self.animate_interval, self.animate)   
        
        self.set_speed(0)
        
    def set_speed(self, speed):
        """sets the speed in rpm to show"""
        self.speed = speed       
        self.last_accel_time = time.time() 
        gobject.timeout_add(self.animate_interval, self.accelerate)
        
    def get_speed(self):
        """Returns the currently shown speed"""
        return self.speed    
        
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
            return True
        
    def animate(self):
        etime = time.time() - self.last_animate_time
        if self.angle_speed > 0.0:
            self.rotation += self.angle_speed * etime
            self.rotation = self.rotation % (2.0 * math.pi)
            self.queue_draw()        
        self.last_animate_time = time.time()
        return True
        
    def expose(self, widget, event):
        if len(self.graph_cache) == 0:
            self.cache_graphs()
        n = int(round(float(self.rotation) / (2 * math.pi) * float(self.graph_cache_images)))
        if n < len(self.graph_cache):
            pixmap = self.graph_cache[n] 
            #self.window.draw_pixbuf(None, pixmap, 0, 0, 0, 0)
            gc = self.window.new_gc()
            self.window.draw_drawable(gc, pixmap, 0, 0, 0, 0, -1, -1)
        
        return False
    
    def size_allocate(self, widget, allocation):
        """size has changed"""
        self.graph_cache = [ ]
        return True
        
    def cache_graphs(self):
        if self.window != None:
            print "caching"
            space = self.get_allocation()              
            self.graph_cache_width = space.width
            self.graph_cache_height = space.height
            self.graph_cache = [ ]
            for n in range(0, self.graph_cache_images):
                print n 
                rotation = 2.0 * math.pi * float(n) / float(self.graph_cache_images)
                pixmap = gdk.Pixmap(self.window, space.width, space.height)
                #pixbuf = gdk.Pixbuf(gdk.COLORSPACE_RGB, True, 8, space.width, space.height)
                context = pixmap.cairo_create()
                self.draw_fan(context, space, rotation)
                self.graph_cache.append(pixmap)
            print "done"
        
    def draw_fan(self, context, space, rotation):
        # scale content
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
        context.rotate(rotation)       
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
    
