#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on the back bias voltage.

import sys,time
sys.path.append('/home/ccd/ucd-scripts/lib')
import PowerSupplyConfig

supplies = PowerSupplyConfig.Power_Supplies()

check=supplies.check_connections() #check whether supplies are connected.
if check==True:
    bss=supplies.BSS_On()
else:
    print("REB5 Power shutdown failed due to connection issue.")
