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
import commands

# data directory
data_dir = "/usr/share/tpfan-admin/"

# path to executable that starts tpfan-admin
install_path = "/usr/bin/tpfan-admin"

# command to restart tpfan-admin as root (used via os.execvp)
if commands.getoutput('pidof kdm') == "":
  run_as_root_cmd = "gksu"
  run_as_root_args = ["gksu", "--message", "Change settings of ThinkPad Fan Control", install_path]
else:
  run_as_root_cmd = "kdesudo"
  run_as_root_args = ["kdesudo", "--comment", "Change settings of ThinkPad Fan Control", install_path]

# icon for window
icon_filename = "tpfan-admin-128x128.png"

# fan border picture
fan_border_filename = "fan_border.svg"

# fan blades picture
fan_blades_filename = "fan_blades.svg"

# name of per user preferences file
pref_filename = ".tpfan-admin"

# gettext domain
gettext_domain = "tpfan-admin"

# gettext locale directory
locale_dir = data_dir + "locales"

# profile submit enabled?
profile_submit_enabled = True

# profile submit url
#profile_submit_url = "http://www.gambitchess.org/tp-fan/profile_submit.py"
profile_submit_url = ""

# program to open url
#profile_url_opener = data_dir + "/open-url.sh"
profile_url_opener = ""

# required tpfand version
# ONLY CHANGE IF YOU KNOW WHAT YOU ARE DOING
required_daemon_version = "0.94"

# version
version = "0.96"
