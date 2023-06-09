#POWER SUPPLY CONFIG AND FUNCTION FILE

# This is the configuration and function definition file for REB5 and OTM power supplies in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand.
# 2022 Daniel Polin

import pyvisa, sys
import numpy as np
from time import sleep
import USBaddresses

###############################################################################
# Set the Baud rates. The pyvisa default is 9600, but the BK Precision 9130Bs run at 4800
Baud9130B=	4800
Baud1697=	9600
Baud9184=	57600
###############################################################################
#Set termination characters where required
BK9130Btermination='\n'
BK1697termination='\r'
BK9184termination='\r\n'

###############################################################################
#Set the ID names of the devices
ID9130B1 = "B&K Precision, 9130B, 802361023737520053, 1.10-1.04"
ID9130B2 = "B&K Precision, 9130B, 802361023737520051, 1.10-1.04"
OK1697 = "OK"
ID9184 = "B&K PRECISION,9184,373B15105,2.04,0"
###############################################################################
# Set the input voltages that go into the REB5 and OTM
V_OTM=		5	# OTM Digital Power
VP5=		5	# Digital
VP7=		8	# Analog
VP15=		15	# CLK High
VN15=		15	# CLK Low
VP_HTR=	12	# Heater
VP40=		38	# OD
IP40Max=	0.095	# OD max allowed current
VN70=		50	# Back Bias
VN70max=	60	# Back Bias maximum voltage
IN70max=	0.001	# Maximum Back Bias supply current
###############################################################################
# Set the delay time between activating different voltages
voltagedelaytime = 20	# delay time between voltages in seconds

###############################################################################
#Set the maximum acceptable difference between a set voltage and a measured readout to pass a check
maximum_voltage_difference = 0.33

###############################################################################
# Define the functions for the Power Supplies


class Power_Supplies(object):
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        # Open the Power supplies for pyvisa commands
        self.BK9130B_1 = self.rm.open_resource(USBaddresses.BK9130B1address)	# Open the Analog, Heater, and Digital Power Supply
        self.BK9130B_2 = self.rm.open_resource(USBaddresses.BK9130B2address)	# Open CLK Low, CLK High, and OTM Power Supply
        self.BK1697 = self.rm.open_resource(USBaddresses.BK1697address)	# Open the OD Power Supply
        self.BK9184= self.rm.open_resource(USBaddresses.BK9184address)	# Open the Back Bias Power Supply

        # Set the Correct Baud Rates 
        self.BK9130B_1.baud_rate = Baud9130B
        self.BK9130B_2.baud_rate = Baud9130B
        #BK1697.baud_rate = Baud1697  #same as default, no need to set
        self.BK9184.baud_rate = Baud9184

        #Set the correct termination characters
        self.BK9130B_1.write_termination=BK9130Btermination
        self.BK9130B_1.read_termination=BK9130Btermination
        self.BK9130B_2.write_termination=BK9130Btermination
        self.BK9130B_2.read_termination=BK9130Btermination
        self.BK1697.write_termination=BK1697termination
        self.BK1697.read_termination=BK1697termination
        #self.BK9184.write_termination=BK9184termination #BK9184 has default write but \r\n read termination for some reason
        self.BK9184.read_termination=BK9184termination
        
        # Set the power supplies to recieve remote commands
        self.BK9130B_1.write('SYSTem:REMote')
        self.BK9130B_2.write('SYSTem:REMote')
        try:
            self.BK1697.query('SESS00')
        except Exception as e:
            print("OD Error: ",e)
        self.BK9184.write('SYStem:REMote')
        return

    def check_connections(self):
        '''This function checks whether all four power supplies are responding to remote control.

        return: 
        Will return True if all are connected and print "All Power Supplies Connected". If any power supply is not connected, will return False and print which devices are not responding.'''

        FoundIDs=[]
        try:
            FoundIDs.append(self.BK9130B_1.query('*IDN?'))
        except Exception as e:
            FoundIDs.append("Not Found")
            print(e)
        try:
            FoundIDs.append(self.BK9130B_2.query('*IDN?'))
        except Exception as e:
            FoundIDs.append("Not Found")
            print(e)
        try:    
            FoundIDs.append(self.BK1697.query('SESS00'))
        except Exception as e:
            FoundIDs.append("Not Found")
            print(e)
        try:    
            FoundIDs.append(self.BK9184.query('*IDN?'))
        except Exception as e:
            FoundIDs.append("Not Found")
            print(e)
        IDlist=[ID9130B1,ID9130B2,OK1697,ID9184]
        if FoundIDs == IDlist:
            print("All Power Supplies Connected")
            return True
        else:
            if IDlist[0] != FoundIDs[0]:
                print("ERROR: BK9130_1 (Clocks) Not connected, please fix the address in USBaddresses.py.")
            if IDlist[1] != FoundIDs[1]:
                print("ERROR: BK9130_2 (CLocks) Not connected, please fix the address in USBaddresses.py.")
            if IDlist[2] != FoundIDs[2]:
                print("ERROR: BK1697 (OD) Not connected, please fix the address in USBaddresses.py.")
            if IDlist[3] != FoundIDs[3]:
                print("ERROR: BK9194 (BSS) Not connected, please fix the address in USBaddresses.py.")
            return False

    def Read_Volt(self,printresult=False):
        '''This function reads out the power supply voltages and returns them as a list.

        inputs: 
            printresult: By default set to 'False'. If printresult=True, it will print out the values.
        return: The power supply voltages in a list as [Analog, Heater, Digital, CLK Low, CLK High, OTM, OD, BSS]'''

        PWR1=self.BK9130B_1.query_ascii_values('MEAS:VOLT:ALL?')
        PWR2=self.BK9130B_2.query_ascii_values('MEAS:VOLT:ALL?')
        OD=self.BK1697.query_ascii_values('GETD00')
        self.BK1697.read()
        OD=[float(str(OD[0])[:-7])*10**-2]
        PWRBSS=self.BK9184.query_ascii_values('MEAS:VOLT?')
        volts=np.concatenate((np.array(PWR1),np.array(PWR2),np.array(OD),PWRBSS))
        if printresult==True:
            print('''Analog 		= '''+str(volts[0])+'''
Heater		= '''+str(volts[1])+'''
Digital		= '''+str(volts[2])+'''
CLK Low 	= '''+str(volts[3])+'''
CLK High 	= '''+str(volts[4])+'''
OTM 		= '''+str(volts[5])+'''
OD 		= '''+str(volts[6])+'''
BSS		= '''+str(volts[7]))
        if PWRBSS[0]>maximum_voltage_difference and min(volts[:-1])<maximum_voltage_difference:
            print("WARNING: BSS on but other voltages off. Shutting down BSS.")
            self.BK9184.write('OUT 0')
        return volts

    def Check_Volt(self,BSS=True, printresult=False):
        '''This function checks the difference between the set voltage values and the actual output values.

        inputs: 
            BSS: By default set to 'True'. If BSS=False, This function will compare BSS to 0V. This is useful if the back bias is supposed to be off.
            printresult: By default set to 'False'. If printresult=True, it will print out whether the check was passed and what the values read out were.
        
        return: Whether the maximum difference between the set voltages and the actual output is within the max allowed value. (True if it is)'''
        voltages=Power_Supplies.Read_Volt(self)
        inputs= np.array([VP7,VP_HTR,VP5,VP15,VN15,V_OTM,VP40,VN70])
        if BSS==False:
            inputs[7]=0
        diff=abs(voltages-inputs)
        maxdiff=max(diff)
        if maxdiff<maximum_voltage_difference:
            check_result= True
        else:
            check_result= False
        if printresult==True:
            print('''Analog 		= '''+str(voltages[0])+'''
Heater		= '''+str(voltages[1])+'''
Digital		= '''+str(voltages[2])+'''
CLK Low 	= '''+str(voltages[3])+'''
CLK High 	= '''+str(voltages[4])+'''
OTM 		= '''+str(voltages[5])+'''
OD 		= '''+str(voltages[6])+'''
BSS		= '''+str(voltages[7]))
        return check_result

    def Check_for_off_Volt(self,printresult=False):
        '''This function checks the difference between the actual output values and 0V for each.

        inputs: 
            printresult: By default set to 'False'. If printresult=True, it will print out whether the check was passed and what the values read out were.
        return: True if the voltages are all within the acceptable rance of zero.'''
        voltages=Power_Supplies.Read_Volt(self)
        inputs= np.array([0,0,0,0,0,0,0,0])
        diff=abs(voltages-inputs)
        maxdiff=max(diff)
        if maxdiff<maximum_voltage_difference:
            check_result= True
        else:
            check_result= False
        if printresult==True:
            print('''Analog 		= '''+str(voltages[0])+'''
Heater		= '''+str(voltages[1])+'''
Digital		= '''+str(voltages[2])+'''
CLK Low 	= '''+str(voltages[3])+'''
CLK High 	= '''+str(voltages[4])+'''
OTM 		= '''+str(voltages[5])+'''
OD 		= '''+str(voltages[6])+'''
BSS		= '''+str(voltages[7]))
        return check_result


    def Power_Setup(self):
        '''This function turns on the REB5 and OTM power supplies to the voltages according to the setings in the 'PowerSupplyConfig.py' file. It does not turn on the BSS supply

        result: turns on REB5 and OTM voltages. Returns true if it worked or shuts down and turns off if it did not.'''

        #rm = pyvisa.ResourceManager()

        #first check whether the voltages are already on.
        checkoff=Power_Supplies.Check_for_off_Volt(self)
        check=Power_Supplies.Check_Volt(self,BSS=False)
        checkBSS=Power_Supplies.Check_Volt(self,BSS=True)

        #if BSS is supposed to be False, make sure BSS gets turned off even if it passed the voltage check.

        #if voltages are not at set values or at 0V, turn them off in order.
        if check==False and checkoff==False and checkBSS==False:
            print('WARNING: Voltages at Unknown values! Shutting Down.')
            checkoff=Power_Supplies.Power_Shutdown(self)
            if checkoff==False:
                print('WARNING: Shutdown Failed!')
            return False
        if check==True or checkBSS==True:
            print("Voltages already on...")
            return True
        #if the voltages are not on, turn them on.	
        if checkoff==True:

            print('Activating REB Power Supply Voltages...')

            # Turn all voltages "ON" at 0V except OD which can only go to 1
            self.BK9130B_2.write('APPLY:VOLTage 0,0,0')
            self.BK9130B_1.write('APPLY:VOLTage 0,0,0')

            self.BK9130B_2.write('OUTPut 1')
            self.BK9130B_1.write('OUTPut 1')
            self.BK1697.query('SOUT001') #OD is just turned off

            # Turn on the Power Supply voltages

            #phase 1
            self.BK9130B_2.write('APPLY:VOLTage 0,0,'+str(V_OTM))
            self.BK9130B_1.write('APPLY:VOLTage 0,'+str(VP_HTR)+','+str(VP5))
            print('OTM, Digital, and Heater Voltages On...')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            Power_Supplies.Read_Volt(self,printresult=True)

            #phase 2
            self.BK9130B_1.write('APPLY:VOLTage '+str(VP7)+','+str(VP_HTR)+','+str(VP5))
            self.BK9130B_2.write('APPLY:VOLTage  '+str(VP15)+','+str(VN15)+','+str(V_OTM))
            self.BK1697.query('VOLT00'+str(VP40)+'0')
            print('Clock Voltages On...')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            Power_Supplies.Read_Volt(self,printresult=True)

            #phase 3
            self.BK1697.query('SOUT000')
            sleep(2)
            print('OD Voltage On...')

            finalcheck=Power_Supplies.Check_Volt(self,BSS=False,printresult=True)
        if finalcheck==True:
            print('REB Voltage Setup Complete.')
            return True
        else:
            print('WARNING: VOLTAGES ARE NOT CORRECT!')
            return False
    
    def BSS_On(self):
        '''This Function Turns on the BSS Supply
        
        return: True if on, False if not.'''
        check=Power_Supplies.Check_Volt(self,BSS=False)
        if check == True:
            self.BK9184.write('VOLT '+ str(VN70)+' \r')
            self.BK9184.write('OUT:LIM:VOLT '+str(VN70max))
            self.BK9184.write('OUT:LIM:CURR '+str(IN70max))
            errors=self.BK9184.query('SYS:ERR?')
            if errors=='0':
            	self.BK9184.write('OUT ON \r')
            else:
            	print("BSS Supply error: ",errors)
            sleep(0.5) #sleep to let voltage reach VN70 value
        check=Power_Supplies.Check_Volt(self,BSS=True)
        if check==True:
            print("BSS supply on.")
            return True
        else:
            print("ERROR: You must turn on CCD voltages before BSS!")
            return False
        
    def BSS_Off(self):
        '''This Function Turns off the BSS Supply
        
        return: True if off, False if not.'''
        '''This Function Turns on the BSS Supply
        
        return: True if on, False if not.'''
        self.BK9184.write('OUT 0')
        self.BK9184.write('VOLT 0')
        sleep(0.2) #wait for voltage to turn off
        checkoff=Power_Supplies.Check_for_off_Volt(self)
        check=Power_Supplies.Check_Volt(self,BSS=False)
        if check==True or checkoff==True:
            print("BSS supply off.")
            return True
        
        else:
            print("WARNING: BSS Not shut down properly or other voltages incorrect!")
            return False

    def Power_Shutdown(self):
        '''This function zeroes and shuts off all REB and OTM power supplies.'''
        #rm = pyvisa.ResourceManager()
        voltages = Power_Supplies.Read_Volt(self)
        checkoff=Power_Supplies.Check_for_off_Volt(self)

        if checkoff==False:  
            print("Shutting down voltages...")

            # Set Back Bias to 0V	
            self.BK9184.write('VOLT 0')
            self.BK9184.write('OUT 0')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            read=Power_Supplies.Read_Volt(self,printresult=True)
            if read[7]<maximum_voltage_difference:
                print('Back Bias Off...')
            else:
                print('ERROR: Failed to shut down BSS! Exiting.')
                return False

            #Set OD to 0V
            self.BK1697.query('SOUT001')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            read=Power_Supplies.Read_Volt(self,printresult=True)
            if read[6]<maximum_voltage_difference:
                print('OD Off...')
            else:
                print('ERROR: Failed to shut down OD! Exiting.')
                return False

            #Set CLK High, CLK Low, and Analog voltages to 0 
            self.BK9130B_2.write('APPLY:VOLTage 0,0,'+str(voltages[5]))
            self.BK9130B_1.write('APPLY:VOLTage 0,'+str(voltages[1])+','+str(voltages[2]))
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            read=Power_Supplies.Read_Volt(self,printresult=True)
            if read[0]<maximum_voltage_difference and read[3]<maximum_voltage_difference and read[4]<maximum_voltage_difference:
                print('CLK High, CLK Low, and Analog Off...')
            else:
                print('ERROR: Failed to shut down! Exiting.')
                return False

            #Set OTM, Digital and Heater voltages to 0.
            self.BK9130B_2.write('APPLY:VOLTage 0,0,0')
            self.BK9130B_1.write('APPLY:VOLTage 0,0,0')

            #Turn all voltages "Off"
            self.BK9130B_2.write('OUTPut 0')
            self.BK9130B_1.write('OUTPut 0')
            sleep(4)
            checkoff=Power_Supplies.Check_for_off_Volt(self,printresult=True)
        if checkoff==True:
            print('All Voltages Off')
            return True
        else:
            print('WARNING: VOLTAGES ARE NOT CORRECT! SHUTDOWN DID NOT COMPLETE CORRECTLY!')
            return False
