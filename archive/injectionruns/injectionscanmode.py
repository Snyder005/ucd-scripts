#Adjust the below parameters Run biasrun.py before this script

VID=6

voltage=1.0 
delay=0.00000136

##### DO NOT EDIT BELOW #####
import numpy as np
import time,subprocess,datetime,sys,glob
from astropy.io import fits
import runindex

date=time.strftime("%Y%m%d")
datadir='/mnt/10TBHDD/data/'
imagedir=datadir+date


def power_CCD(state,BSS=False):
    if state=="off" or state=="OFF" or state=="Off":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py R21 --off',check=True, shell=True)
        time.sleep(2)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py R21 --off',check=True, shell=True)
    elif state=="on" or state=="ON" or state=="On":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py R21 --on',check=True, shell=True)
        time.sleep(2)
        if BSS:
            subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py R21 --on',check=True, shell=True)

def write_fits_headers(directory):
    print("writing .fits headers. DO NOT EXIT!")
    files=np.array(glob.glob(directory+'/*.fits'))
    files.sort()
    for image in files:
        hdul = fits.open(image, mode='update')
        # Get the header of the primary HDU
        header = hdul[0].header
        # Add or modify a keyword in the header
        header.set('IMGTYPE', 'INJECT', 'Injection test data')
        header.set('VOLTAGE', voltage, 'Injection test voltage (Vpp)')
        header.set('DELAY', delay, 'Injection test delay from PClk3 trigger (s)')
        # Save the changes and close the file
        hdul.close()
    print(".FITS headers updated")
    return
    
def rename_directory(directory,newname):
    currentindex=runindex.runindex
    subprocess.run('mv '+directory+" "+newname+str(currentindex),check=True, shell=True)
    currentindex+=1
    with open('/home/ccd/ucd-scripts/injectionruns/runindex.py', 'w') as f:
        f.write("runindex = "+str(currentindex))
    return newname+str(currentindex-1)
    
subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/injectionruns/scanmode_injection.cfg',check=True, shell=True)  

newdir=rename_directory(imagedir,imagedir+"-InjectionScanMode")

reset=input("Turn on the Signal Generator Output and press enter...")

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/injectionruns/scanmode_injection.cfg',check=True, shell=True)    

write_fits_headers(imagedir)       

subprocess.run('mv '+imagedir+"/* "+newdir,check=True, shell=True)
subprocess.run('rm -r '+imagedir,check=True, shell=True)
power_CCD("off")
