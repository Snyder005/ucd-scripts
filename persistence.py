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

print("running get outta there!")
time.sleep(30)

try:
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/bias_stability_e2v.cfg',check=True, shell=True)
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/calibrationdarks1.cfg',check=True, shell=True)
    for i in range(5):
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v1.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v2.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v3.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v4.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v5.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v6.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v7.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v8.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v9.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/persistence_e2v10.cfg',check=True, shell=True)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/eotest-configs/bias_stability_e2v.cfg',check=True, shell=True)
        eWarning(str(i+1)+"/5 Runs Finished")
    

except:
    print("failure")
subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)

eWarning("Run Finished")
