#Code to take bias stability tests
import numpy as np
import time,subprocess,datetime,sys
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Email_Warning

def eWarning(warning):
    try:
        subject = "Run Finished " + time.asctime()
        w_file = open('/home/ccd/ucd-scripts/python-lib/send_warning', 'w')
        w_file.write(subject + ":: ")
        w_file.write(warning)
        w_file.close()
        Email_Warning.Send_Warning(subject, warning)
    except:
        pass

scale='linear' #'log', 'linear'

date=time.strftime("%Y%m%d")
imagedir='/mnt/10TBHDD/data/'+date

print("running get outta there!")
time.sleep(30)
writesleep=600
sleeptime=1200
if scale=='log':
    sleeptime=2
starttime=time.time()
currenttime=starttime

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/bias_stability_e2v.cfg',check=True, shell=True)
while time.time()-starttime<86400:
    if time.time()-currenttime>sleeptime-1:
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/bias_stability_e2v.cfg',check=True, shell=True)
        currenttime=time.time()
        if scale=='log':
            sleeptime*=2
    file = open(imagedir+'/runninglog.txt', 'a')
    out="Still running correctly at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
    file.write(out)       
    file.close()
    print("Sleeping for 10 min")
    time.sleep(writesleep)
    

subprocess.run('mv '+imagedir+'/ '+imagedir+'-bias_stability_'+scale+'_spaced/',check=True, shell=True)  

eWarning("Linear scale Run Finished starting log scale")

scale='log' #'log', 'linear'

date=time.strftime("%Y%m%d")
imagedir='/mnt/10TBHDD/data/'+date

print("running get outta there!")
time.sleep(30)
writesleep=600
sleeptime=1200
if scale=='log':
    sleeptime=2
starttime=time.time()
currenttime=starttime

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/bias_stability_e2v.cfg',check=True, shell=True)
while time.time()-starttime<86400:
    if time.time()-currenttime>sleeptime-1:
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/bias_stability_e2v.cfg',check=True, shell=True)
        currenttime=time.time()
        if scale=='log':
            sleeptime*=2
    file = open(imagedir+'/runninglog.txt', 'a')
    out="Still running correctly at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
    file.write(out)       
    file.close()
    print("Sleeping for 10 min")
    time.sleep(writesleep)
    

subprocess.run('mv '+imagedir+'/ '+imagedir+'-bias_stability_'+scale+'_spaced/',check=True, shell=True)  

eWarning("Log scale Run Finished")
