import sys,time,subprocess,datetime
sys.path.append('/home/ccd/ucd-scripts/python-lib')

date=time.strftime("%Y%m%d")
startingimagedir='/mnt/10TBHDD/data/'+date


print("Running. Get outta there!")
time.sleep(30) #get out of the room
subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/ptc_r.cfg',check=True, shell=True)

subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)
