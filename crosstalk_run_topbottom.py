import sys,time,subprocess,datetime
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Stage

stage = Stage.Stage()

date=time.strftime("%Y%m%d")
startingimagedir='/mnt/10TBHDD/data/'+date
segments=['/Top','/Bottom']

x=21220

file = open(startingimagedir+'/runninglog.txt', 'a')
out="Starting "+segments[0]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
file.write(out)       
file.close()

print("Running. Get outta there!")
time.sleep(30) #get out of the room

subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak.cfg',check=True, shell=True)
subprocess.run('mkdir '+startingimagedir+segments[0],check=True, shell=True)
subprocess.run('mv '+startingimagedir+'/TS_C* '+startingimagedir+segments[0],check=True, shell=True)
      
file = open(startingimagedir+'/runninglog.txt', 'a')
out="Finished "+segments[0]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+". Starting "+segments[1]+"\n"
file.write(out)       
file.close()
pos=stage.move_stage(x=x)
time.sleep(10)
subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/crosstalk_streak.cfg',check=True, shell=True)
subprocess.run('mkdir '+startingimagedir+segments[1],check=True, shell=True)
subprocess.run('mv '+imagedir+'/TS_C* '+startingimagedir+segments[1],check=True, shell=True)

file = open(startingimagedir+'/runninglog.txt', 'a')
out="Finished "+segments[1]+" at "+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S")+"\n"
file.write(out)       
file.close()
subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)

