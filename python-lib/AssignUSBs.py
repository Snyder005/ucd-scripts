#USB ASSIGNING SCRIPT

# This script should be run after a system reset it assigns the correct USB adresses in /dev/ttyUSB? to the correct devices by querying them and returning the correct device.
#Daniel Polin 2023

import pyvisa,subprocess
import PowerSupplyConfig

class Assign_USBs(object):
    def __init__(self):
        self.BK9130B1address = 'WARNING: BK9130B1 not detected'
        self.BK9130B2address = 'WARNING: BK9130B2 not detected'
        self.BK1697address = 'WARNING: BK1697 not detected'
        self.BK9184address = 'WARNING: BK9184 not detected'
        self.shutteraddress = 'WARNING: Shutter not detected'
        self.stageaddress = 'Warning: Stage motor not detected'
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
        
    def assign_shutter(self)
    '''Determines the correct USB addresses in /dev/ and writes them to the USBaddresses.py file'''
    #assign the shutter
    try:
        sh = subprocess.check_output(['ls', '-l', '/dev/shutter']).decode()
        shutteraddress='ASRL1'+sh[-2]+'::INSTR'
    except Exception as e:
        print("Failure to write shutter address. Exception of type %s and args = \n"%type(e).__name__, e.args)
    #assign the stage address
    try:
        sh = subprocess.check_output(['ls', '-l', '/dev/stage']).decode()
        stageaddress='ASRL1'+sh[-2]+'::INSTR'
    except Exception as e:
        print("Failure to write stage motor address. Exception of type %s and args = \n"%type(e).__name__, e.args)
    rm = pyvisa.ResourceManager()
    resources=rm.list_resources()
    for tty in resources:
        try:
            #Look for the BK9130s
            if BK9130B1address == 'WARNING: BK9130B1 not detected' or BK9130B2address == 'WARNING: BK9130B2 not detected':
                device = rm.open_resource(tty)
                device.baud_rate=PowerSupplyConfig.Baud9130B
                device.write_termination=PowerSupplyConfig.BK9130Btermination
                device.read_termination=PowerSupplyConfig.BK9130Btermination
                ID=device.query('*IDN?')
                if ID==PowerSupplyConfig.ID9130B1:
                    BK9130B1address = tty
                if ID==ID9130B2:
                    BK9130B2address = tty
            else:
                a=[ #throw an exception on purpose
        except Exception:
            #device not the one we're looking for, look for BK9184
            try:
                if BK9184address == 'WARNING: BK9184 not detected':
                    device.baud_rate=PowerSupplyConfig.Baud9184
                    device.read_termination=PowerSupplyConfig.BK9184termination
                    ID=device.query('*IDN?')
                    if ID==PowerSupplyConfig.ID9184:
                        BK9184address = tty
                else:
                    a=[ #throw an exception on purpose
            except Exception:
                #device not the one we're looking for. Look for BK1697
                try:
                    if BK1697address == 'WARNING: BK1697 not detected'
                        device.baud_rate=PowerSupplyConfig.Baud1697
                        device.write_termination=PowerSupplyConfig.BK1697termination
                        device.read_termination=PowerSupplyConfig.BK1697termination
                        okresponse = device.query('\rSESS00')
                        if okresponse==PowerSupplyConfig.OK1697:
                            BK1697address = tty
                    else:
                        a=[ #throw an exception on purpose
                except Exception:
                    #device not the one we're looking for. Look for shutter.
                    device = rm.open_resource(tty)
                    device.write_termination='\r\n'
                    device.read_termination='\r\n'
                    try:
                        ID=device.query('$O 2')
                        if ID==shutter_reset_return or shutter_reset_return2:
                            shutteraddress = tty
                    except Exception:
                        pass
                
#write the addresses to the USBaddresses.py file
with open('/home/ccd/ucd-scripts/lib/USBaddresses.py', 'w') as f:
    f.write('''BK9130B1address = "'''+BK9130B1address+'''"
BK9130B2address = "'''+BK9130B2address+'''"
BK1697address = "'''+BK1697address+'''"
BK9184address = "'''+BK9184address+'''"
shutteraddress= "'''+shutteraddress+'''"
stageaddress= "'''+stageaddress+'"')

print('BK9130B1: '+BK9130B1address)
print('BK9130B2: '+BK9130B2address)
print('BK9184: '+BK1697address)
print('BK1697: '+BK9184address)
print('Shutter: '+shutteraddress)
print('Stage Motor: '+stageaddress)
