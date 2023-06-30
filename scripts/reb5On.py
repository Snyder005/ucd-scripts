#!/usr/bin/env ccs-script

#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.
import PowerSupplyConfig

def power_reb5_on():

    supplies = PowerSupplyConfig.Power_Supplies()

    check=supplies.check_connections() #check whether supplies are connected.
    if check==True:
        reb=supplies.power_setup()
        print(reb)
    else:
        raise RuntimeError("REB5 Power shutdown failed due to connection issue.")

if __name__ == '__main__':

    power_reb5_on()
