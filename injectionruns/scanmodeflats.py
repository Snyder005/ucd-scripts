##### DO NOT EDIT BELOW #####
import numpy as np
import time,subprocess,datetime,sys,glob
from astropy.io import fits
import runindex
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Email_Warning

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
            
def power_light(state):
    if state=="off" or state=="OFF" or state=="Off":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)
    elif state=="on" or state=="ON" or state=="On":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOn.py',check=True, shell=True)
        
def eWarning(warning):
    try:
        subject = "Injection Test Update " + time.asctime()
        w_file = open('/home/ccd/ucd-scripts/python-lib/send_warning', 'w')
        w_file.write(subject + ":: ")
        w_file.write(warning)
        w_file.close()
        Email_Warning.Send_Warning(subject, warning)
    except:
        pass
    
def rename_directory(directory,newname):
    currentindex=runindex.runindex
    subprocess.run('mv '+directory+" "+newname+str(currentindex),check=True, shell=True)
    currentindex+=1
    with open('/home/ccd/ucd-scripts/injectionruns/runindex.py', 'w') as f:
        f.write("runindex = "+str(currentindex))
    return newname+str(currentindex-1)

print("sleeping 30s get outta there!")
time.sleep(30)
eWarning("Starting New Injection Run.")   
try:
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/injectionruns/scanmodeflats.cfg',check=True, shell=True)  

    newdir=rename_directory(imagedir,imagedir+"-InjectionScanMode")  
except:
    print("error in run")
    eWarning("Error in Scan Mode Flat run.")
    time.sleep(1)
       
power_light("off")
power_CCD("off")
eWarning("Scan Mode Flat run finished.")
