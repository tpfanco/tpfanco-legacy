# tpfand without tpfan-admin #

If you prefer not to use tpfan-admin, it's also possible to configure tpfand without it. To change tpfand configuration you need to edit /etc/tpfand.conf

## tpfand.conf options ##

**enabled** = [True/False]
This option enables or disables fan control. If enabled is set to False, tpfand will do nothing and let BIOS control the fan.

**override\_profile** = [True/False]
This option is relevant only if you installed tpfand-profiles and a profile is available for your machine. Setting override\_profile to True will allow tpfand to use the supplied profile. Setting it to False means that you want to specify your own trigger settings and ignore existing profile

**hysteresis** = [0-10]
This option influences the behavior of tpfand when the temperature goes down. Let's suppose that you set a trigger on the CPU temperature such that, for temperatures lower than 45°C, the fan speed is set to Level 1. As soon as the temperature gets higher, the fan is switched to Level 2. After the fan has been activated, the CPU temperature will usually go down and at some point reach the 45°C threshold. When hysteresis is set to 0, tpfand will switch to Level 1 immediately after the temperature drops below 45°C. If hysteresis is set to x, tpfand will keep the current fan level until the temperature becomes (45-x)°C. For instance, if you set it to 5, the fan will not switch to Level 1 until the temperature becomes lower than 40°C. Such behavior can greatly help to prevent fan pulsing, and it's recommended to keep hysteresis at something between 3 and 6. The default value is 3.

## trigger settings ##
Triggers are set using the following syntax:
[[Sensor number](.md)]. [[Sensor name](.md)] = [Temperature:Fan level] [Temperature:Fan level] [Temperature:Fan level] ...
Sensor number corresponds to the position of the sensor /proc/acpi/ibm/thermal. Sensor name is a description of the sensor. Temperature defines the starting point of an interval and Fan level specifies the fan regime in this interval. Fan level accepts following variables:<br>
<table><thead><th> 0 </th><th> fan is off </th></thead><tbody>
<tr><td> 2 </td><td> fan level 1 </td></tr>
<tr><td> 3 </td><td> fan level 2 </td></tr>
<tr><td> 4 </td><td> fan level 3 </td></tr>
<tr><td> 5 </td><td> fan level 4 </td></tr>
<tr><td> 6 </td><td> fan level 5 </td></tr>
<tr><td> 7 </td><td> fan level 6 </td></tr>
<tr><td> 8 </td><td> fan level 7 </td></tr>
<tr><td> 254 </td><td> disengaged </td></tr>
<tr><td> 255 </td><td> auto (fan is controlled by the BIOS) </td></tr>
<tr><td> 256 </td><td> full speed </td></tr></tbody></table>

If you're not familiar with the thinkpad_acpi fan levels, please visit<br>
<a href='http://www.thinkwiki.org/wiki/How_to_control_fan_speed'>http://www.thinkwiki.org/wiki/How_to_control_fan_speed</a>

<h2>Example</h2>
Below you can find a working example of tpfand.conf<br>
<br>
<pre><code>enabled = True<br>
override_profile = True<br>
<br>
0. Sensor 0 = 0:0 55:2 60:255 <br>
1. Sensor 1 = 0:0 55:2 60:255 <br>
2. Sensor 2 = 0:0 40:2 45:4 50:255 <br>
3. Sensor 3 = 0:255 <br>
4. Sensor 4 = 0:0 40:2 45:255 <br>
5. Sensor 5 = 0:255 <br>
6. Sensor 6 = 0:0 40:2 45:255 <br>
7. Sensor 7 = 0:255 <br>
8. Sensor 8 = 0:0 50:2 55:255 <br>
9. Sensor 9 = 0:0 55:2 60:255 <br>
10. Sensor 10 = 0:0 56:2 60:4 65:255 <br>
11. Sensor 11 = 0:255 <br>
12. Sensor 12 = 0:255 <br>
13. Sensor 13 = 0:255 <br>
14. Sensor 14 = 0:255 <br>
15. Sensor 15 = 0:255 <br>
<br>
hysteresis = 3<br>
</code></pre>


