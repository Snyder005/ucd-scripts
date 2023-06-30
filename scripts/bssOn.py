#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on the back bias voltage.
import PowerSupplyConfig

def power_bss_on():
    supplies = PowerSupplyConfig.Power_Supplies()

    check=supplies.check_connections() #check whether supplies are connected.
    if check==True:
        bss=supplies.bss_on()
        print(bss)
    else:
        raise RuntimeError("BSS power on failed due to connection issue.")

def __name__ == '__main__':

    power_bss_on()
