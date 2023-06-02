#!/usr/bin/env ccs-script

#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.

import sys,time
sys.path.append('/home/ccd/ucd-scripts/lib')
import PowerSupplyConfig

supplies = PowerSupplyConfig.Power_Supplies()

check=supplies.check_connections() #check whether supplies are connected.
if check==True:
    reb=supplies.power_setup()
    print(reb)
else:
    print("REB5 Power shutdown failed due to connection issue.")
