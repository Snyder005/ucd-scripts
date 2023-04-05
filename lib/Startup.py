#TEMPEST IMAGING STARTUP SCRIPT

# This script should be run after a system reset it does the following:

import os
import pyvisa

###############################################################################
#Enable Darwin DAQ control of REB clocks
os.system(source daq_enable_clocks.sh)

###############################################################################
# Query the USB devices to have the correct device assigned to the correct USB port
# Write USB addresses to file
ID9130B1 = 'B&K Precision, 9130B, 802361023737520053, 1.10-1.04\n'
ID9130B2 = 'B&K Precision, 9130B, 802361023737520051, 1.10-1.04\n'
OK1697 = 'OK'
ID9184 = 'B&K PRECISION,9184,373B15105,2.04,0\r\n'
shutter_reset_return ='$R -1\r\n'
IDstageX = ''
IDstageY = ''
IDstageZ = ''

rm = pyvisa.ResourceManager()
resources=rm.list_resources()

BK9130B1address = 'WARNING: BK9130B1 not detected'
BK9130B2address = 'WARNING: BK9130B2 not detected'
BK1697address = 'WARNING: BK1697 not detected'
BK9184address = 'WARNING: BK9184 not detected'
shutteraddress = 'WARNING: Shutter not connected'
stageXaddress = ''
stageYaddress = ''
stageZaddress = ''

for tty in resources:
    device = rm.open_resource(tty)
    device.baud_rate=Baud9130B
    try:
        ID=device.query('*IDN?')
        if ID==ID9130B1:
            BK9130B1address = tty
        if ID==ID9130B2:
            BK9130B2address = tty
    except Exception:
        #device not the one we're looking for
        device.baud_rate=Baud9184
        try:
            ID=device.query('*IDN?')
            if ID==ID9184:
                BK9184address = tty
        except Exception:
            #device not the one we're looking for
            device.baud_rate=Baud1697
            device.write_termination=BK1697termination
            device.read_termination=BK1697termination
            try:
                okresponse = device.query('\rSESS00')
                if okresponse==OK1697:
                    BK1697address = tty
            except Exception:
                try:
        		ID=device.query('$R\r')
        		if ID==shutter_reset_return.replace('\x00',''):
            			shutteraddress = tty
    		except Exception:
        		pass
        		
#write the addresses to the USBaddresses.py file        		
with open('/home/ccd/ccs/etc/USBaddresses.py', 'w') as f:
    f.write('''BK9130B1address = "'''+BK9130B1address+'''"
BK9130B2address = "'''+BK9130B2address+'''"
BK1697address = "'''+BK1697address+'''"
BK9184address = "'''+BK9184address+'''"
shutteraddress= "'''+shutteraddress+'"')

print('BK9130B1: '+BK9130B1address)
print('BK9130B2: '+BK9130B2address)
print('BK9184: '+BK1697address)
print('BK1697: '+BK9184address)
print('Shutter: '+shutteraddress)
print('stageX: '+stageXaddress)
print('stageY: '+stageYaddress)
print('stageZ: '+stageZaddress)

###############################################################################
#REB5 Power Supply Startup
import PowerSupplyConfig
import StartupConfig

if StartupConfig.REBPowerStatus == True:
	if BK9130B1address == 'WARNING: BK9130B1 not detected' or BK9130B2address == 'WARNING: BK9130B2 not detected' or BK1697address == 'WARNING: BK1697 not detected' or BK9184address == 'WARNING: BK9184 not detected':
		print('WARNING: REB5 Power Startup Halted - One or more power supplies not connected')
	else:
		PowerSupplyConfig.Power_Setup(BSS=StartupConfig.BSS)
elif StartupConfig.REBPowerStatus == False:
	PowerSupplyConfig.Power_Shutdown()

###############################################################################
#Start CCS Subsystem (focal plane, image handler, and database subsystems)
os.system(sudo systemctl start ucd-fp)
print('CCS Focal Plane Subsystem Initiated')
os.system(sudo systemctl start ucd-ih)
print('CCS Image Handler Subsystem Initiated')
os.system(sudo systemctl start h2db)
print('CCS Database Subsystem Initiated')

###############################################################################
#Labsphere Light Startup


###############################################################################
#Turn on CCD

###############################################################################
#Focusing

