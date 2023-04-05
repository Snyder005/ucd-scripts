#POWER SUPPLY CONFIG AND FUNCTION FILE

# This is the configuration and function definition file for REB5 and OTM power supplies in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand.
# 2022 Daniel Polin

import pyvisa
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
BK1697termination='\r'

###############################################################################
# Set the input voltages that go into the REB5 and OTM
V_OTM=		5	# OTM Digital voltage
VP5=		5	# Digital voltage
VP7=		8	# Analog voltage
VP15=		15	# CLK High voltage
VN15=		15	# CLK Low voltage
VP_HTR=		12	# Heater voltage
VP40=		38	# OD voltage
VN70=		50	# Back Bias voltage

###############################################################################
# Set the delay time between activating different voltages
voltagedelaytime = 20	# delay time between voltages in seconds

###############################################################################
#Set the maximum acceptable difference between a set voltage and a measured readout to pass a check
maximum_voltage_difference = 0.2

###############################################################################
# Define the functions for the Power Supplies

	
def Read_Volt(printresult=False):
	'''This function reads out the power supply voltages and returns them as a list.
	
	inputs: 
		printresult: By default set to 'False'. If printresult=True, it will print out the values.
	return: The power supply voltages in a list as [Analog, Heater, Digital, CLK Low, CLK High, OTM, OD, BSS]'''
	#rm = pyvisa.ResourceManager()
	# Open the Power supplies for pyvisa commands
	BK9130B_1 = rm.open_resource(USBaddresses.BK9130B1address)	# Open the Analog, Heater, and Digital Power Supply
	BK9130B_2 = rm.open_resource(USBaddresses.BK9130B2address)	# Open CLK Low, CLK High, and OTM Power Supply
	BK1697 = rm.open_resource(USBaddresses.BK1697address)	# Open the OD Power Supply
	BK9184= rm.open_resource(USBaddresses.BK9184address)	# Open the Back Bias Power Supply

	# Set the Correct Baud Rates and termination characters
	BK9130B_1.baud_rate = Baud9130B
	BK9130B_2.baud_rate = Baud9130B
	#BK1697.baud_rate = Baud1697
	BK9184.baud_rate = Baud9184
	
	BK1697.write_termination=BK1697termination
	BK1697.read_termination=BK1697termination
	
	# Set the power supplies to recieve remote commands
	BK9130B_1.write('SYSTem:REMote')
	BK9130B_2.write('SYSTem:REMote')
	BK1697.query('\rSESS00')
	BK9184.write('SYStem:REMote')
	
	PWR1=BK9130B_1.query_ascii_values('MEAS:VOLT:ALL?')
	PWR2=BK9130B_2.query_ascii_values('MEAS:VOLT:ALL?')
	OD=BK1697.query_ascii_values('GETD00')
	OD=[float(str(OD[0])[:-7])*10**-2]
	PWRBSS=BK9184.query_ascii_values('MEAS:VOLT?')
	volts=np.concatenate((np.array(PWR1),np.array(PWR2),np.array(OD),np.array(PWRBSS)))
	if printresult==True:
		print('''Analog 	= '''+str(volts[0])+'''
Heater		= '''+str(volts[1])+'''
Digital	= '''+str(volts[2])+'''
CLK Low 	= '''+str(volts[3])+'''
CLK High 	= '''+str(volts[4])+'''
OTM 		= '''+str(volts[5])+'''
OD 		= '''+str(volts[6])+'''
BSS 		= '''+str(volts[7]))
	return volts
	
def Check_Volt(BSS=True, printresult=False):
	'''This function checks the difference between the set voltage values and the actual output values.
	
	inputs: 
		BSS: By default set to 'True'. If BSS=False, This function will compare BSS to 0V. This is useful if the back bias is supposed to be off.
		printresult: By default set to 'False'. If printresult=True, it will print out whether the check was passed and what the values read out were.
	return: Whether the maximum difference between the set voltages and the actual output is within the max allowed value. (True if it is)'''
	voltages=Read_Volt()
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
		print('''Analog 	= '''+str(voltages[0])+'''
Heater		= '''+str(voltages[1])+'''
Digital	= '''+str(voltages[2])+'''
CLK Low 	= '''+str(voltages[3])+'''
CLK High 	= '''+str(voltages[4])+'''
OTM 		= '''+str(voltages[5])+'''
OD 		= '''+str(voltages[6])+'''
BSS 		= '''+str(voltages[7]))
	return check_result
	
def Check_for_off_Volt(printresult=False):
	'''This function checks the difference between the actual output values and 0V for each.
	
	inputs: 
		printresult: By default set to 'False'. If printresult=True, it will print out whether the check was passed and what the values read out were.
	return: True if the voltages are all within the acceptable rance of zero.'''
	voltages=Read_Volt()
	inputs= np.array([0,0,0,0,0,0,0,0])
	diff=abs(voltages-inputs)
	maxdiff=max(diff)
	if maxdiff<maximum_voltage_difference:
		check_result= True
	else:
		check_result= False
	if printresult==True:
		print('''Analog 	= '''+str(voltages[0])+'''
Heater		= '''+str(voltages[1])+'''
Digital	= '''+str(voltages[2])+'''
CLK Low 	= '''+str(voltages[3])+'''
CLK High 	= '''+str(voltages[4])+'''
OTM 		= '''+str(voltages[5])+'''
OD 		= '''+str(voltages[6])+'''
BSS 		= '''+str(voltages[7]))
	return check_result
	
	
def Power_Setup(BSS=False):
	'''This function turns on the REB5 and OTM power supplies to the voltages according to the setings in the 'PowerSupplyConfig.py' file.
	
	inputs: 
		BSS: By default set to 'False'. if BSS=True, it will also set the back bias voltages.
	result: turns on REB5 and OTM voltages.'''
	
	#rm = pyvisa.ResourceManager()
	
	#first check whether the voltages are already on.
	check=Check_Volt(BSS=BSS)
	checkoff=Check_for_off_Volt()
	
	#if BSS is supposed to be False, make sure BSS gets turned off even if it passed the voltage check.
	
	#if voltages are not at set values or at 0V, turn them off in order.
	if check==False and checkoff==False:
		checkoff=Power_Shutdown()
		if checkoff==False:
			print('WARNING: Startup Aborted!')
	if check==True:
		print("Voltages already on...")
		
	
	#if the voltages are not on, turn them on.	
	if checkoff==True:

		print('Activating REB Power Supply Voltages...')
        
		# Open the Power supplies for pyvisa commands
		BK9130B_1 = rm.open_resource(USBaddresses.BK9130B1address)	# Open the Analog, Heater, and Digital Power Supply
		BK9130B_2 = rm.open_resource(USBaddresses.BK9130B2address)	# Open CLK Low, CLK High, and OTM Power Supply
		BK1697 = rm.open_resource(USBaddresses.BK1697address)	# Open the OD Power Supply
		BK9184= rm.open_resource(USBaddresses.BK9184address)	# Open the Back Bias Power Supply 
        
		# Set the Correct Baud Rates
		BK9130B_1.baud_rate = Baud9130B
		BK9130B_2.baud_rate = Baud9130B
		#BK1697.baud_rate = Baud1697
		BK9184.baud_rate = Baud9184
		
		BK1697.write_termination=BK1697termination
		BK1697.read_termination=BK1697termination
	
		#Set the maximum current values
		BK9130B_2.write('APPLY:VOLTage 0,0,0')
		BK9130B_1.write('APPLY:VOLTage 0,0,0')
		#BK9184.write('VOLT 0')
		ODcur0=str(IP40_MAX).split('.')[0]
		ODcur1=('%s' % float('%.2g' % float(str(IP40_MAX).split('.')[1]))).split('.')[0][:2]
		BK1697.query('CURR00'+ODcur0+ODcur1)
		
		# Turn all voltages "ON" at 0V except OD which can only go to 1
		BK9130B_2.write('APPLY:VOLTage 0,0,0')
		BK9130B_1.write('APPLY:VOLTage 0,0,0')
		BK9184.write('VOLT 0')
		BK9130B_2.write('OUTPut 1 \r')
		BK9130B_1.write('OUTPut 1 \r')
		BK1697.query('SOUT001') #OD is just turned off
		BK9184.write('OUT 1\r')
	
		# Turn on the Power Supply voltages
	
		#phase 1
		BK9130B_2.write('APPLY:VOLTage 0,0,'+str(V_OTM)+' \r')
		BK9130B_1.write('APPLY:VOLTage 0,'+str(VP_HTR)+','+str(VP5)+' \r')
		print('OTM, Digital, and Heater Voltages On...')
		sleep(voltagedelaytime)
		Read_Volt(printresult=True)
	
		#phase 2
		BK9130B_1.write('APPLY:VOLTage '+str(VP7)+','+str(VP_HTR)+','+str(VP5)+' \r')
		BK9130B_2.write('APPLY:VOLTage  '+str(VP15)+','+str(VN15)+','+str(V_OTM)+' \r')
		BK1697.query('VOLT00'+str(VP40)+'0')
		print('Clock Voltages On...')
		sleep(voltagedelaytime)
		Read_Volt(printresult=True)

		#phase 3
		BK1697.query('SOUT000')
		sleep(2)
		Read_Volt(printresult=True)
		print('OD Voltage On...')
	
		if BSS==True:
			sleep(voltagedelaytime)
		
			#phase 4
			BK9184.write('VOLT '+str(VN70)+' \r')
			sleep(4)
			print('Back Bias Voltage On...')
	if BSS==False:
		print('Back Bias Voltage not supplied due to BSS=False.')
	voltages=Read_Volt(printresult=True)
	finalcheck=Check_Volt(BSS=BSS)
	if finalcheck==True:
		print('REB Voltage Setup Complete.')
		return True
	else:
		print('WARNING: VOLTAGES ARE NOT CORRECT!')
		return False
	

def Power_Shutdown():
	'''This function zeroes and shuts off all REB and OTM power supplies.'''
	#rm = pyvisa.ResourceManager()
	voltages = Read_Volt()
	checkoff=Check_for_off_Volt()
	
	if checkoff==False:   
		# Open the Power supplies for pyvisa commands
		BK9130B_1 = rm.open_resource(USBaddresses.BK9130B1address)	# Open the Analog, Heater, and Digital Power Supply
		BK9130B_2 = rm.open_resource(USBaddresses.BK9130B2address)	# Open CLK Low, CLK High, and OTM Power Supply
		BK1697 = rm.open_resource(USBaddresses.BK1697address)	# Open the OD Power Supply
		BK9184= rm.open_resource(USBaddresses.BK9184address)	# Open the Back Bias Power Supply 
        
		# Set the Correct Baud Rates
		BK9130B_1.baud_rate = Baud9130B
		BK9130B_2.baud_rate = Baud9130B
		#BK1697.baud_rate = Baud1697
		BK9184.baud_rate = Baud9184
		
		BK1697.write_termination=BK1697termination	
		BK1697.read_termination=BK1697termination
	
		print("Shutting down voltages...")
	
		# Set Back Bias to 0V	
		BK9184.write('VOLT 0')
		sleep(voltagedelaytime)
		print('Back Bias Off...')
		Read_Volt(printresult=True)
	
		#Set OD to 0V
		BK1697.query('SOUT001')
		sleep(voltagedelaytime)
		print('OD Off...')
		Read_Volt(printresult=True)
	
		#Set CLK High, CLK Low, and Analog voltages to 0 
		BK9130B_2.write('APPLY:VOLTage 0,0,'+str(voltages[5])+' \r')
		BK9130B_1.write('APPLY:VOLTage 0,'+str(voltages[1])+','+str(voltages[2])+' \r')
		sleep(voltagedelaytime)
		print('CLK High, CLK Low, and Analog Off...')
		Read_Volt(printresult=True)
	
		#Set OTM, Digital and Heater voltages to 0.
		BK9130B_2.write('APPLY:VOLTage 0,0,0 \r')
		BK9130B_1.write('APPLY:VOLTage 0,0,0 \r')
		
		#Turn all voltages "Off"
		BK9130B_2.write('OUTPut 0 \r')
		BK9130B_1.write('OUTPut 0 \r')
		BK9184.write('OUT 0 \r')
		sleep(4)
		Read_Volt(printresult=True)
		checkoff=Check_for_off_Volt()
	elif checkoff==True:
		print('All Voltages Off')
		return True
	else:
		print('WARNING: VOLTAGES ARE NOT CORRECT! SHUTDOWN DID NOT COMPLETE CORRECTLY!')
		return False
