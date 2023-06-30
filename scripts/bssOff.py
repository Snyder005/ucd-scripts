#!/usr/bin/env ccs-script
#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns off the back bias voltage.
import PowerSupplyConfig

def power_bss_off():
    supplies = PowerSupplyConfig.Power_Supplies()

    check=supplies.check_connections() #check whether supplies are connected.
    if check==True:
        bss=supplies.bss_off()
        print(bss)
    else:
        raise RuntimeError("BSS supply shutdown failed due to connection issue.")

if __name__ == '__main__':

    power_bss_off()
