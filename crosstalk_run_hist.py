import sys,time,subprocess,datetime
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Stage

stage = Stage.Stage()

date=time.strftime("%Y%m%d")
startingimagedir='/mnt/10TBHDD/data/'+date
segments=['/Seg10_11','/Seg00_01_12_13','/Seg02_03_14_15','/Seg04_05_16_17','/Seg06_07']

y=-10212

file = open(startingimagedir+'/runninglog.txt', 'a')
out="Starting "+segments[0]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
file.write(out)       
file.close()

print("Running. Get outta there!")
time.sleep(30) #get out of the room

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak_hist.cfg',check=True, shell=True)
subprocess.run('mkdir '+startingimagedir+segments[0],check=True, shell=True)
subprocess.run('mv '+startingimagedir+'/TS_C* '+startingimagedir+segments[0],check=True, shell=True)


did_date_change=False
for i in range(4):
    date=time.strftime("%Y%m%d")
    imagedir='/mnt/10TBHDD/data/'+date        
    file = open(startingimagedir+'/runninglog.txt', 'a')
    out="Finished "+segments[i]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+". Starting "+segments[i+1]+"\n"
    file.write(out)       
    file.close()
    pos=stage.move_stage(y=y)
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak_hist.cfg',check=True, shell=True)
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

