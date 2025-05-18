#!/usr/bin/env ccs-script
#Back bias checking script

#2025 - Craig Lage

#This script checks the back bias voltage and current
from org.lsst.ccs.scripting import CCS
from datetime import datetime
import sys, time
sys.path.append('/home/ccd/ucd-scripts/lib')

import BackBiasCheck
BBCheck = BackBiasCheck.BackBias()

BBCheck.check_connections()
outfile = open("/home/ccd/HVbias_Monitor.txt", "w")

for i in range(10):
    Vss = BBCheck.read_BSS()    
    Iss = BBCheck.read_ISS()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S.%f")
    output = "Vss = %.4f, Iss = %.4f, T = %s"%(float(Vss), float(Iss), current_time)
    print(output)
    outfile.write(output+'\n')
    time.sleep(0.1)

outfile.close()
