#Code to brighter fatter tests
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

date=time.strftime("%Y%m%d")
startingimagedir='/mnt/10TBHDD/data/'+date

file = open(startingimagedir+'/runninglog.txt', 'a')
out="Starting at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
file.write(out)       
file.close()

print("running get outta there!")
time.sleep(30)

try:
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/calibrationdarks1.cfg',check=True, shell=True)
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Finished 15s darks at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
    file.write(out)       
    file.close()
except:
    print("failure")
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Run failed at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
    file.write(out)       
    file.close()
    subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)
    
try:
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/calibrationdarks2.cfg',check=True, shell=True)
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Finished 30s darks at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
    file.write(out)       
    file.close()
except:
    print("failure")
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Run failed at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
    file.write(out)       
    file.close()
    subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)
eWarning("30s and 15s Finished starting 60s")    
try:
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/calibrationdarks3.cfg',check=True, shell=True)
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Finished 60s darks at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"+"Run Complete!"
    file.write(out)       
    file.close()
except:
    print("failure")
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Run failed at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
    file.write(out)       
    file.close()

subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)

eWarning("Run Finished")

