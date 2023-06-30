#!/usr/bin/env ccs-script

#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns off the REB5 Power supplies in the correct order. This includes the BSS voltage.
import PowerSupplyConfig

def power_reb5_off():
    supplies = PowerSupplyConfig.Power_Supplies()

    check=supplies.check_connections() #check whether supplies are connected.
    if check==True:
        reb=supplies.power_shutdown()
        print(reb)
    else:
        raise RuntimeError("REB5 Power shutdown failed due to connection issue.")
