#!/usr/bin/env ccs-script

#REB5 POWER TESTING SCRIPT

#2023-Daniel Polin

#This script turns on the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.

import sys,time
sys.path.append('/home/ccd/ucd-scripts/lib')
import PowerSupplyConfig

supplies = PowerSupplyConfig.Power_Supplies()

check=supplies.check_connections() #check whether supplies are connected.
print("check",check)

read=supplies.read_volt()
print("read",read)

readp=supplies.read_volt(printresult=True)
print("readp",readp)

chv=supplies.check_volt()
print("chv",chv)

chvp=supplies.check_volt(BSS=False, printresult=True)
print("chvp",chvp)
#bss=supplies.Power_Setup()
#else:
#    print("REB5 Power shutdown failed due to connection issue.")
