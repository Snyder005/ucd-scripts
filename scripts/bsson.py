#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on/off the back bias voltage.


import PowerSupplyConfig


PowerSupplyConfig.power_bss_on()
print "Setting back bias switch on."

