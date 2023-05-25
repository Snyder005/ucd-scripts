#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.

import sys,time
sys.path.append('/home/ccd/ucd-scripts/lib')
import PowerSupplyConfig

supplies = PowerSupplyConfig.Power_Supplies()

check=supplies.check_connections() #check whether supplies are connected.
print('0',check)

read=supplies.Read_Volt()
print('1',read)
'''
time.sleep(1)

readprint=supplies.Read_Volt(printresult=True)
print('2',readprint)

cvbsson=supplies.Check_Volt(BSS=True)
print('3',cvbsson)

cvbssonp=supplies.Check_Volt(BSS=True,printresult=True)
print('4',cvbsson)

cvbssoff=supplies.Check_Volt(BSS=False)
print('5',cvbssoff)

checkoff=supplies.Check_for_off_Volt()
print('6',checkoff)

checkoffp=supplies.Check_for_off_Volt(printresult=True)
print('7',checkoffp)

#on=supplies.Power_Setup()
#print('8',on)

bss=supplies.BSS_On()
print('9',bss)

bss0=supplies.BSS_Off()
print('10',bss0)

off=supplies.Power_Shutdown()
print('11',off)'''
