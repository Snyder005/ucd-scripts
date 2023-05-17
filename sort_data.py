import numpy as np
import glob,os
import datetime

today=datetime.datetime.now().strftime("%Y%m%d")
directory='/mnt/10TBHDD/data/'+today
move='mv '+directory+'/TS*/*S01* '+directory
os.system(move)
remove='rm -r '+directory+'/TS*/'
os.system(remove)
