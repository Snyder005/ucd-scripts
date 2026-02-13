#!/usr/bin/env ccs-script

#POWER SUPPLY CONFIG AND FUNCTION FILE

# This is the configuration and function definition file for REB5 and OTM power supplies in the UC Davis Tempest, Rubin Observatory Optical beam simulator test stand.
# 2022 Daniel Polin

from xyz.froud.jvisa import JVisaResourceManager
import java.lang.Exception as JException
from java.lang import String
import sys
from time import sleep
import USBaddresses

###############################################################################
#Set the ID names of the devices
ID9130B1 = "B&K Precision, 9130B, 802361023737520053, 1.10-1.04"
ID9130B2 = "B&K Precision, 9130B, 802361023737520051, 1.10-1.04"
OK1697 = "OK"

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

###############################################################################
# Set the delay time between activating different voltages
SETTLE_TIME = 20	# delay time between voltages in seconds

###############################################################################
#Set the maximum acceptable difference between a set voltage and a measured readout to pass a check
TOLERANCE = 0.33

###############################################################################

class BKPrecision1697(object):

    def __init__(self, resource_name):
        rm = JVisaResourceManager()
        self.instrument = rm.openInstrument(resource_name)
        self.instrument.setSerialBaudRate(9600)
        self.instrument.setWriteTerminator('\r')
        self.instrument.setReadTerminationCharacter('\r')
        self.instrument.queryString('SESS00')

    @classmethod
    def fromProperties(cls, properties_file, name='bk1697'):
        properties = Properties()
        with FileInputStream('instruments.properties') as f:
            properties.load(f)

        resource_name = properties['{0}/address'.format(name)]
        return cls(resource_name)

    def isConnected(self):
        try:
            self.instrument.queryString('SESS00')
        except (JException, Exception):
            return False
        return True

    def getVoltage(self):
        response = self.instrument.queryString('GETD00')
        voltage = float(response)*10**-7
        return voltage

    def setOutputState(self, state):
        if isinstance(state, bool):
            self.instrument.queryString('SOUT00{0:d}'.format(state))
        else:
            raise ValueError('Not a boolean value: {0}'.format(state))

    def setVoltage(self, voltage): # Make formatter for arbitrary voltages
        self.instrument.queryString('VOLT00{0}0'.format(voltage))

class BKPowerSupply(object):

    def __init__(self, resource_name, baud_rate=None, write_terminator=None, read_terminator=None):
        rm = JVisaResourceManager()
        self.instrument = rm.openInstrument(resource_name)
        if baud_rate is not None:
            self.instrument = setSerialBaudRate(baud_rate)
        if write_terminator is not None:
            self.instrument = setWriteTerminator(write_terminator)
        if read_terminator is not None:
            self.instrument = setReadTerminationCharacter(read_terminator)
        self.instrument.write('SYSTEM:REMOTE')

    def isConnected(self):
        try:
            self.getIDN()
        except (JException, Exception):
            return False
        return True

    def getIDN(self):
        idn = self.instrument.queryString('*IDN?')
        return idn
       
class BKPrecision9184(BKPowerSupply):

    def __init__(self, resource_name, voltage_limit=None, current_limit=None):
        super().__init__(resource_name, baud_rate=57600, write_terminator='\r\n')
        if voltage_limit is not None:
            self.setVoltageLimit(voltage_limit)
        if current_limit is not None:
            self.setCurrentLimit(current_limit)

    def getVoltage(self):
        voltage = float(self.instrument.queryString('MEASURE:VOLTAGE?')
        return voltage

    def getCurrent(self):
        """Get power supply current.

        Returns
        -------
        current : `float`
            Power supply current.
        """
        current = float(self.instrument.queryString('MEASURE:CURRENT?'))
        return current

    def getOutput(self):
        state = self.instrument.write('OUTPUT?')
        return state

    def setVoltage(self, voltage):
        """Set power supply voltage.

        Parameters
        ----------
        voltage : `float`
            Power supply voltage.
        """
        self.instrument.write('SOURCE:VOLTAGE {0:.3f}'.format(voltage))

    def setVoltageLimit(self, voltage_limit):
        """Set power supply voltage limit.

        Parameters
        ----------
        voltage_limit : `float`
            Power supply voltage limit.
        """
        self.instrument.write('OUTPUT:LIMIT:VOLTAGE {0:.3f}'.format(voltage_limit)

    def setCurrentLimit(self, current_limit):
        """Set power supply current limit.
    
        Parameters
        ----------
        current_limit : `float`
            Power supply current limit.
        """
        self.instrument.write('OUTPUT:LIMIT:CURRENT {0:.3f}'.format(current_limit))

    def setOutput(self, state):
        if isinstance(state, bool):
            self.instrument.write('OUTPUT {0:d}'.format(state))
        else:
            raise ValueError('Not a boolean value: {0}'.format(state))

class BKPrecision9130B(BKPowerSupply):

    def __init__(self, resource_name):
        super().__init__(resource_name, baud_rate=4800, write_terminator='\n', read_terminator='\n')

    def getVoltages(self):
        response = self.instrument.queryString('MEASURE:VOLTAGE:ALL?')
        voltages = tuple(float(voltage) for voltage in response.split(','))
        return voltages

    def getOutput(self, state):
        state = self.instrument.queryString('OUTPUT:STATE?')
        return state

    def setVoltages(self, voltages):
        self.instrument.write('APPLY:VOLTAGE {0},{1},{2}'.format(*voltages))

class REBPower(object):
    
    def __init__(self, resource_names):
        self.bk9130b_1 = BKPrecision9130B(resource_names[0])
        self.bk9130b_2 = BKPrecision9130B(resource_names[1])
        self.bk1697 = BKPrecision1697(resource_names[2])

    @classmethod
    def fromProperties(cls, properties_file):
        properties = Properties()
        with FileInputStream('instruments.properties') as f:
            properties.load(f)
    
        resource_names = (properties['bk9130b1/address'],
                          properties['bk9130b2/address'],
                          properties['bk1697/address'])
        return cls(resource_names)

    def checkConnections(self):
        is_connected = (self.bk9130b_1.isConnected(),
                        self.bk9130b_2.isConnected(),
                        self.bk1697.isConnected())
        return is_connected

    def getOutputState(self):
        pass # make sure this isn't a pointer!

    def getVoltages(self):
        pass # get output voltages

    def verifyVoltages(self):
        pass # check difference between set voltage and output voltage

    def powerOn(self):
    
        # check if voltages are on

        # if voltages in unknown state turn them off

        # set bk9130 voltages to 0V and set to on
        self.bk9130b_1.setVoltages((0, 0, 0))
        self.bk9130b_2.setVoltages((0, 0, 0))

        # set bk9130b to on, set 1697 to off
        self.bk9130b_1.setOutputState(True)
        self.bk9130b_2.setOutputState(True)
        self.bk1697.setOutputState(False)

        # set otm, digital, and heater voltages
        self.bk9130b_1.setVoltages((0, VP_HTR, VP5))
        self.bk9130b_2.setVoltages((0, 0, V_OTM))
        time.sleep(SETTLE_TIME)

        # set clock voltages
        self.bk9130b_1.setVoltages((VP7, VP_HTR, VP5))
        self.bk9130b_2.setVoltages((VP15, VN15, V_OTM))
        self.bk1697.setVoltage(VP40)
        time.sleep(SETTLE_TIME)

        # set bk1697 to on
        self.bk1697.setOutputState(True)

    def powerOff(self):

        # check if voltages are off; if not, proceed.
    
        # set bk1697 to off.
        self.bk1697.setOutputState(False)

        # set clock voltages and analog to 0V
        self.bk9130b_1.setVoltages((0, voltages[1], voltages[2]))
        self.bk9130b_2.setVoltages((0, 0, voltages[3]))
        time.sleep(SETTLE_TIME)

        # set otm, digital, and heater voltages to 9V
        self.bk9130b_1.setVoltages((0, 0, 0))
        self.bk9130b_2.setVoltages((0, 0, 0))

        # bk9130b set to off
        self.bk9130b_1.setOutputState(False)
        self.bk9130b_2.setOutputState(False)

class Power_Supplies(object):
    def __init__(self):
        self.rm = JVisaResourceManager()
        # Open the Power supplies for jvisa commands
        self.BK9130B_1 = self.rm.openInstrument(USBaddresses.BK9130B1address)	# Open the Analog, Heater, and Digital Power Supply
        self.BK9130B_2 = self.rm.openInstrument(USBaddresses.BK9130B2address)	# Open CLK Low, CLK High, and OTM Power Supply
        self.BK1697 = self.rm.openInstrument(USBaddresses.BK1697address)	# Open the OD Power Supply
        self.BK9184 = self.rm.openInstrument(USBaddresses.BK9184address)	# Open the Back Bias Power Supply

        # Set the Correct Baud Rates 
        self.BK9130B_1.setBaudRate(Baud9130B)
        self.BK9130B_2.setBaudRate(Baud9130B)
        #BK1697.baud_rate = Baud1697  #same as default, no need to set
        self.BK9184.setBaudRate(Baud9184)

        #Set the correct termination characters
        self.BK9130B_1.setWriteTerminator(BK9130Btermination)
        self.BK9130B_1.setReadTerminationCharacter(BK9130Btermination)
        self.BK9130B_2.setWriteTerminator(BK9130Btermination)
        self.BK9130B_2.setReadTerminationCharacter(BK9130Btermination)
        self.BK1697.setWriteTerminator(BK1697termination)
        self.BK1697.setReadTerminationCharacter(BK1697termination)
        #self.BK9184.setWriteTerminator(BK9184termination) #BK9184 has default write but \r\n read termination for some reason
        #self.BK9184.setReadTerminationCharacter(BK9184termination) #Jython only allows a single temination character not \r\n so we have to just add that to the readout.
        
        # Set the power supplies to recieve remote commands
        self.BK9130B_1.write('SYSTem:REMote')
        self.BK9130B_2.write('SYSTem:REMote')
        try:
            self.BK1697.queryString('SESS00')
        except (JException,Exception) as e:
            print("OD Error: ",e)
        self.BK9184.write('SYStem:REMote \r\n')
        return

    def check_connections(self):
        '''This function checks whether all four power supplies are responding to remote control.

        return: 
        Will return True if all are connected. If any power supply is not connected, will return False and print which devices are not responding.'''

        FoundIDs=[]
        try:
            FoundIDs.append(self.BK9130B_1.queryString('*IDN?'))
        except (JException,Exception) as e:
            FoundIDs.append("Not Found")
            print(e)
        
        try:
            FoundIDs.append(self.BK9130B_2.queryString('*IDN?'))
        except (JException,Exception) as e:
            FoundIDs.append("Not Found")
            print(e)
        
        try:    
            FoundIDs.append(self.BK1697.queryString('SESS00'))
        except (JException,Exception) as e:
            FoundIDs.append("Not Found")
            print(e)

        try:    
            FoundIDs.append(self.BK9184.queryString('*IDN? \r\n'))
        except (JException,Exception) as e:
            FoundIDs.append("Not Found")
            print(e)
            
        IDlist=[ID9130B1,ID9130B2,OK1697,ID9184]
        if FoundIDs == IDlist:
            #print("All Power Supplies Connected")
            return True
        else:
            if IDlist[0] != FoundIDs[0]:
                print("ERROR: BK9130_1 (Clocks) Not connected, please fix the address in USBaddresses.py.")
            if IDlist[1] != FoundIDs[1]:
                print("ERROR: BK9130_2 (CLocks) Not connected, please fix the address in USBaddresses.py.")
            if IDlist[2] != FoundIDs[2]:
                print("ERROR: BK1697 (OD) Not connected, please fix the address in USBaddresses.py.")
            if IDlist[3] != FoundIDs[3]:
                print("ERROR: BK9184 (BSS) Not connected, please fix the address in USBaddresses.py.")
            return False

    def read_BSS(self):
        PWRBSS=self.BK9184.queryString('MEAS:VOLT? \r\n')
        return PWRBSS
    
    def read_volt(self,printresult=False):
        '''This function reads out the power supply voltages and returns them as a list.

        inputs: 
            printresult: By default set to 'False'. If printresult=True, it will print out the values.
        return: The power supply voltages in a list as [Analog, Heater, Digital, CLK Low, CLK High, OTM, OD, BSS]'''

        PWR1=self.BK9130B_1.queryString('MEAS:VOLT:ALL?')
        PWR1=[float(voltage) for voltage in (PWR1.split(','))]
        PWR2=self.BK9130B_2.queryString('MEAS:VOLT:ALL?')
        PWR2=[float(voltage) for voltage in (PWR2.split(','))]
        OD=self.BK1697.queryString('GETD00')
        OD=float(OD)*10**-7
        self.BK1697.readString()
        #OD=[float(str(OD[0])[:-7])*10**-2]
        PWRBSS=self.BK9184.queryString('MEAS:VOLT? \r\n')
        PWRBSS=float(PWRBSS)
        volts=[PWR1[0],PWR1[1],PWR1[2],PWR2[0],PWR2[1],PWR2[2],OD,PWRBSS]
        if printresult==True:
            print('''Analog 		= '''+str(volts[0])+'''
Heater		= '''+str(volts[1])+'''
Digital		= '''+str(volts[2])+'''
CLK Low 	= '''+str(volts[3])+'''
CLK High 	= '''+str(volts[4])+'''
OTM 		= '''+str(volts[5])+'''
OD 		= '''+str(volts[6])+'''
BSS		= '''+str(volts[7]))
        if PWRBSS>maximum_voltage_difference and min(volts[:-1])<maximum_voltage_difference:
            print("WARNING: BSS on but other voltages off. Shutting down BSS.")
            self.BK9184.write('OUT 0')
        return volts

    def check_volt(self,BSS=True, printresult=False):
        '''This function checks the difference between the set voltage values and the actual output values.

        inputs: 
            BSS: By default set to 'True'. If BSS=False, This function will compare BSS to 0V. This is useful if the back bias is supposed to be off.
            printresult: By default set to 'False'. If printresult=True, it will print out whether the check was passed and what the values read out were.
        
        return: Whether the maximum difference between the set voltages and the actual output is within the max allowed value. (True if it is)'''
        voltages=self.read_volt()
        inputs= [VP7,VP_HTR,VP5,VP15,VN15,V_OTM,VP40,VN70]
        if BSS==False:
            inputs[7]=0
        diff=[abs(voltages[i]-inputs[i]) for i in range(8)]
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

    def check_for_off_volt(self,printresult=False):
        '''This function checks the difference between the actual output values and 0V for each.

        inputs: 
            printresult: By default set to 'False'. If printresult=True, it will print out whether the check was passed and what the values read out were.
        return: True if the voltages are all within the acceptable rance of zero.'''
        voltages=self.read_volt()
        inputs= [0,0,0,0,0,0,0,0]
        diff=[abs(voltages[i]-inputs[i]) for i in range(8)]
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


    def power_setup(self):
        '''This function turns on the REB5 and OTM power supplies to the voltages according to the setings in the 'PowerSupplyConfig.py' file. It does not turn on the BSS supply

        result: turns on REB5 and OTM voltages. Returns true if it worked or shuts down and turns off if it did not.'''

        #first check whether the voltages are already on.
        checkoff=self.check_for_off_volt()
        check=self.check_volt(BSS=False)
        checkBSS=self.check_volt(BSS=True)

        #if BSS is supposed to be False, make sure BSS gets turned off even if it passed the voltage check.

        #if voltages are not at set values or at 0V, turn them off in order.
        if check==False and checkoff==False and checkBSS==False:
            print('WARNING: Voltages at Unknown values! Shutting Down.')
            checkoff=self.power_shutdown()
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
            self.BK1697.queryString('SOUT001') #OD is just turned off

            # Turn on the Power Supply voltages

            #phase 1
            self.BK9130B_2.write('APPLY:VOLTage 0,0,'+str(V_OTM))
            self.BK9130B_1.write('APPLY:VOLTage 0,'+str(VP_HTR)+','+str(VP5))
            print('OTM, Digital, and Heater Voltages On...')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            self.read_volt(printresult=True)

            #phase 2
            self.BK9130B_1.write('APPLY:VOLTage '+str(VP7)+','+str(VP_HTR)+','+str(VP5))
            self.BK9130B_2.write('APPLY:VOLTage  '+str(VP15)+','+str(VN15)+','+str(V_OTM))
            self.BK1697.queryString('VOLT00'+str(VP40)+'0')
            print('Clock Voltages On...')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            self.read_volt(printresult=True)

            #phase 3
            self.BK1697.queryString('SOUT000')
            sleep(2)
            print('OD Voltage On...')

            finalcheck=self.check_volt(BSS=False,printresult=True)
        if finalcheck==True:
            print('REB Voltage Setup Complete.')
            return True
        else:
            print('WARNING: VOLTAGES ARE NOT CORRECT!')
            return False
    
    def bss_on(self):
        '''This Function Turns on the BSS Supply
        
        return: True if on, False if not.'''
        check=self.check_volt(BSS=False)
        if check == True:
            self.BK9184.write('VOLT '+ str(VN70)+' \r\n')
            self.BK9184.write('OUT:LIM:VOLT '+str(VN70max)+' \r\n')
            self.BK9184.write('OUT:LIM:CURR '+str(IN70max)+' \r\n')
            errors=self.BK9184.queryString('SYS:ERR? \r\n')
            if errors=='0':
            	self.BK9184.write('OUT ON \r\n')
            else:
            	print("BSS Supply error: ",errors)
            sleep(0.5) #sleep to let voltage reach VN70 value
        check=self.check_volt(BSS=True)
        if check==True:
            print("BSS supply on.")
            return True
        else:
            print("ERROR: You must turn on CCD voltages before BSS!")
            return False
    
    def bss_on_arbitrary_voltage(self,BSS_voltage):
        '''This Function Turns on the BSS Supply with a new back bias voltage set as an argument.
        
        return: True if on, False if not.'''
        VN70arb=BSS_voltage
        self.bss_on()
        self.BK9184.write('VOLT '+ str(VN70arb)+' \r\n')
        self.BK9184.write('OUT:LIM:VOLT '+str(VN70max)+' \r\n')
        self.BK9184.write('OUT:LIM:CURR '+str(IN70max)+' \r\n')
        errors=self.BK9184.queryString('SYS:ERR? \r\n')
        if errors=='0':
            self.BK9184.write('OUT ON \r\n')
        else:
            print("BSS Supply error: ",errors)
        sleep(0.5) #sleep to let voltage reach VN70 value
    
    def bss_off(self):
        '''This Function Turns off the BSS Supply
        
        return: True if off, False if not.'''
        '''This Function Turns on the BSS Supply
        
        return: True if on, False if not.'''
        self.BK9184.write('OUT 0 \r\n')
        self.BK9184.write('VOLT 0 \r\n')
        sleep(0.2) #wait for voltage to turn off
        checkoff=self.check_for_off_volt()
        check=self.check_volt(BSS=False)
        if check==True or checkoff==True:
            print("BSS supply off.")
            return True
        
        else:
            print("WARNING: BSS Not shut down properly or other voltages incorrect!")
            return False

    def power_shutdown(self):
        '''This function zeroes and shuts off all REB and OTM power supplies.'''
        voltages = self.read_volt()
        checkoff=self.check_for_off_volt()

        if checkoff==False:  
            print("Shutting down voltages...")

            # Set Back Bias to 0V	
            self.BK9184.write('VOLT 0 \r\n')
            self.BK9184.write('OUT 0 \r\n')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            read=self.read_volt(printresult=True)
            if read[7]<maximum_voltage_difference:
                print('Back Bias Off...')
            else:
                print('ERROR: Failed to shut down BSS! Exiting.')
                return False

            #Set OD to 0V
            self.BK1697.queryString('SOUT001')
            print("Waiting "+str(voltagedelaytime)+"s")
            sleep(voltagedelaytime)
            read=self.read_volt(printresult=True)
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
            read=self.read_volt(printresult=True)
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
            checkoff=self.check_for_off_volt(printresult=True)
        if checkoff==True:
            print('All Voltages Off')
            return True
        else:
            print('WARNING: VOLTAGES ARE NOT CORRECT! SHUTDOWN DID NOT COMPLETE CORRECTLY!')
            return False
