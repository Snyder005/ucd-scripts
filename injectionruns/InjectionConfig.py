#Adjust the below parameters Run biasrun.py before this script

VID=6

lowvoltage=-0.02 	#lowest Vpp to use
highvoltage=-1.3	#highest Vpp to use
numberofvoltages=10	#number of steps from low to high voltage

lowdelay=0.0007	#the starting delay time from the p3 clock
highdelay=0.0007035	#the ending delay time from the p3 clock
delaystep=0.00000002	#the step between delay times

sleeptime=14		#the time to sleep between changing settings.

cfgfile="biases.cfg"
biascfg="priorbiases.cfg"

notes=None
imagesperrun=2
biasesperrun=20

##### DO NOT EDIT BELOW #####
import numpy as np
import time,subprocess,datetime,sys,glob
import runindex
from astropy.io import fits
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Email_Warning

date=time.strftime("%Y%m%d")
datadir='/mnt/10TBHDD/data/'
imagedir=datadir+date

delaytimes=np.arange(lowdelay,highdelay,delaystep)
if lowdelay==highdelay:
    delaytimes=[lowdelay]
        
def take_data(cfgfile):
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py '+cfgfile,check=True, shell=True)
    return
    
def set_alarm(state):
    if state=="off" or state=="OFF" or state=="Off":
        subprocess.run('python /home/ccd/security/disarm.py',check=True, shell=True)
    elif state=="on" or state=="ON" or state=="On":
        subprocess.run('python /home/ccd/security/arm.py',check=True, shell=True)
    
def make_imagedir(imagedir):
    subprocess.run('mkdir '+imagedir,check=True, shell=True)
    return

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

def remove_fits_files(imagedir):
    subprocess.run('rm '+imagedir+'/TS_C_*',check=True, shell=True)
    
def copy_file_to_imagedir(file):
    subprocess.run('cp '+file+" "+imagedir,check=True, shell=True)
    
def rename_directory(directory,newname):
    currentindex=runindex.runindex
    subprocess.run('mv '+directory+" "+newname+str(currentindex),check=True, shell=True)
    currentindex+=1
    with open('/home/ccd/ucd-scripts/injectionruns/runindex.py', 'w') as f:
        f.write("runindex = "+str(currentindex))
    return
    
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
        
def writelogfile(filename,notes):  
    file = open(filename, 'a')
    file.write(notes)       
    file.close()
    
def write_fits_headers(directory):
    stime=time.time()
    print("writing .fits headers. DO NOT EXIT!")
    voltagelist=np.linspace(lowvoltage,highvoltage,numberofvoltages)
    files=np.array(glob.glob(directory+'/*.fits'))
    files.sort()
    imagestoupdate=files[biasesperrun:]
    start=0
    for voltage in voltagelist:
        for delay in delaytimes:
            for image in imagestoupdate[start:start+imagesperrun]:
                hdul = fits.open(image, mode='update')
                # Get the header of the primary HDU
                header = hdul[0].header
                # Add or modify a keyword in the header
                header.set('IMGTYPE', 'INJECT', 'Injection test data')
                header.set('VOLTAGE', voltage, 'Injection test voltage (Vpp)')
                header.set('DELAY', delay, 'Injection test delay from PClk3 trigger (s)')
                # Save the changes and close the file
                hdul.close()
            start+=imagesperrun
        print("Finished V="+'{0:.4f}'.format(voltage)+". "+str(int(time.time()-stime))+"s elapsed.")
    print(".FITS headers updated")
    return
            
def full_injection_run():
    #set_alarm("on")
    starttime=time.time()
    eWarning("Starting New Injection Run.")
    numberofruns=len(delaytimes)*numberofvoltages
    iteration=1
    try:    
        for run in range(numberofruns):
            take_data(cfgfile)
            sleepy=sleeptime*iteration-time.time()+starttime
            print("sleeping "+str(sleepy)+"s")
            time.sleep(sleepy) #sleep until we have taken our images at the old settings
            iteration+=1  
    except Exception as e:
        print(e)
        eWarning("Error in injection run on iteration "+str(iteration)+"\n"+str(e))
    power_CCD("off")
    copy_file_to_imagedir(cfgfile)
    copy_file_to_imagedir("/home/ccd/ucd-scripts/injectionruns/InjectionConfig.py")
    notestolog='''
'''+time.asctime()+''' Starting Injection Run
Injecting into VID'''+str(VID)+'''
Number of Voltages: '''+str(numberofvoltages)+'''
Low Voltage: '''+str(lowvoltage)+'''
High Voltage: '''+str(highvoltage)+'''
Delay Step Size: '''+str(delaystep)+'''
Lowest Delay: '''+str(lowdelay)+'''
Highest Delay: '''+str(highdelay)+"\n"
    if notes:
        notestolog=notestolog+'''
'''+notes+"\n"
    writelogfile(imagedir+"/"+date+"-log.txt",notestolog)
    newdate=time.strftime("%Y%m%d")
    if newdate!=date:
    	copy_file_to_imagedir(datadir+newdate+"/*")
    	time.sleep(2)
    write_fits_headers(imagedir)
    rename_directory(imagedir,imagedir+"-Injection")
    eWarning("Finished injection run")
    set_alarm("off")
    return
    
def bias_run():
    make_imagedir(imagedir)
    power_CCD("on")
    notestolog=time.asctime()+" Took 20 Bias images with no Injection\n"
    writelogfile(imagedir+"/"+date+"-log.txt",notestolog)
    take_data(biascfg)
    return
