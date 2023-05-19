import subprocess
import time

subprocess.run('ccs-script lib/ucd-data.py examples/spot.cfg',check=True, shell=True)

time.sleep(1)

subprocess.run('lib/python3 autosort.py',check=True, shell=True)
