#Adjust the below parameters Run biasrun.py before this script

VID=6

voltages=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,                                                                                                                                      3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0,5.1,5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,6.0]
delay=0.00000058
numberofimagesperset=30


##### DO NOT EDIT BELOW #####
import numpy as np
import time,subprocess,datetime,sys,glob
from astropy.io import fits
import runindex

date=time.strftime("%Y%m%d")
datadir='/mnt/10TBHDD/data/'
imagedir=datadir+date
logfile=imagedir+"/"+date+"-log.txt"

def write_fits_headers(directory,voltage,delay):
    stime=time.time()
    print("writing .fits headers. DO NOT EXIT!")
    files=np.array(glob.glob(directory+'/*.fits'))
    files.sort()
    imagestoupdate=files[-numberofimagesperset:]
    for image in imagestoupdate:
        hdul = fits.open(image, mode='update')
        # Get the header of the primary HDU
        header = hdul[0].header
        # Add or modify a keyword in the header
        header.set('IMGTYPE', 'INJECT', 'Injection test data')
        header.set('VOLTAGE', voltage, 'Injection test voltage (Vpp)')
        header.set('DELAY', delay, 'Injection test delay from S2 trigger (s)')
        # Save the changes and close the file
        hdul.close()
    print("Finished V="+'{0:.4f}'.format(voltage)+". "+str(int(time.time()-stime))+"s elapsed.")
    print(".FITS headers updated")
    return

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/injectionruns/scanmode_injection.cfg',check=True, shell=True)
files=np.array(glob.glob(imagedir+'/*.fits'))
files.sort()
firstfile=files[0].split("/")[-1]
lastfile=files[-1].split("/")[-1]
f = open(logfile, 'a')
text=firstfile+" to "+lastfile+": Biases\n"
f.write(text)       
f.close()
reset=input("Set Voltage="+str(voltages[0])+" Turn on the Signal Generator Output and press enter...")

for i in range(len(voltages)):
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/injectionruns/scanmode_injection.cfg',check=True, shell=True)
    write_fits_headers(imagedir,voltages[i],delay)
    files=np.array(glob.glob(imagedir+'/*.fits'))
    files.sort()
    firstfile=files[0].split("/")[-1]
    lastfile=files[-numberofimagesperset].split("/")[-1]
    f = open(logfile, 'a')
    text=firstfile+" to "+lastfile+": voltage="+str(voltages[i])+"\n"
    f.write(text)       
    f.close()
    if i<len(voltages)-1:
        reset=input("Change voltage to "+str(voltages[i+1])+" and press enter...") 
