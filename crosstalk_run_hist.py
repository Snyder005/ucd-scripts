import sys,time,subprocess,datetime
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Stage
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

stage = Stage.Stage()

date=time.strftime("%Y%m%d")
startingimagedir='/mnt/10TBHDD/data/'+date
segments=['/Seg10_11','/Seg00_01_12_13','/Seg02_03_14_15','/Seg04_05_16_17','/Seg06_07']

x=-10500
y=-10212
detector="e2v"

file = open(startingimagedir+'/runninglog.txt', 'a')
out="Starting "+segments[0]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
file.write(out)       
file.close()

print("Running. Get outta there!")
time.sleep(30) #get out of the room

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak_hist_'+detector+'.cfg',check=True, shell=True)
subprocess.run('mkdir '+startingimagedir+segments[0],check=True, shell=True)
subprocess.run('mv '+startingimagedir+'/TS_C* '+startingimagedir+segments[0],check=True, shell=True)


did_date_change=False
for i in range(4):
    eWarning("Finished Run "+str(i+1)+"/4. Starting next run")
    date=time.strftime("%Y%m%d")
    imagedir='/mnt/10TBHDD/data/'+date        
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Finished "+segments[i]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+". Starting "+segments[i+1]+"\n"
    file.write(out)       
    file.close()
    if detector=="ITL":
        pos=stage.move_stage(y=y)
    elif detector=="e2v":
        pos=stage.move_stage(x=x)
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak_hist_'+detector+'.cfg',check=True, shell=True)
    subprocess.run('mkdir '+startingimagedir+segments[i+1],check=True, shell=True)
    subprocess.run('mv '+imagedir+'/TS_C* '+startingimagedir+segments[i+1],check=True, shell=True)
    if imagedir!=startingimagedir and not did_date_change:
        did_date_change=True
        subprocess.run('mv '+startingimagedir+'/TS_C* '+startingimagedir+segments[i+1],check=True, shell=True)
        

file = open(startingimagedir+'/runninglog.txt', 'a')
out="Finished "+segments[4]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
file.write(out)       
file.close()
subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)

eWarning("Final Run Finished")

