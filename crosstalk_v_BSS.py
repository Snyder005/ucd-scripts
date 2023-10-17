#/usr/bin/env ccs-script
import sys
import time
import os
import logging
import datetime
from argparse import ArgumentParser
from java.time import Duration
import java.lang.Exception as JException

from org.lsst.ccs.scripting import CCS

from ccs import aliases
from ccs import proxies
from ccs import versions
from ccs import configs
import config

import PowerSupplyConfig

# Temporary work around for problems with CCS responsiveness
CCS.setDefaultTimeout(Duration.ofSeconds(30))

class WarningFilter(object):

    def filter(self, log_record): 
        return log_record.levelno != logging.WARNING

def take_biases(cfgfile, run=None):

    ## Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    log_format = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", 
                                   datefmt = "%Y-%m-%d %H:%M:%S")

    ## Set up handler for command line
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)

    ## Set up handler for daily observing log file
    ih = CCS.attachSubsystem("ucd-ih")
    rootdir = ih.sendSynchCommand("getConfigurationParameterValue imageHandler/ImageHandlingConfig FITSRootDirectory")
    today = datetime.date.today().strftime("%Y%m%d")
    if not os.path.exists(os.path.join(rootdir, today)):
        os.makedirs(os.path.join(rootdir, today))

    obsfile_handler = logging.FileHandler(os.path.join(rootdir, today, '{0}_acquisition.log'.format(today)))
    obsfile_handler.setLevel(logging.INFO)
    obsfile_handler.addFilter(WarningFilter())
    obsfile_handler.setFormatter(log_format)
    logger.addHandler(obsfile_handler)

    ## Set up handler for global log file
    homedir = os.path.expanduser('~')
    globalfile_handler = logging.FileHandler(os.path.join(homedir, 'data_acquisition.log'))
    globalfile_handler.setLevel(logging.DEBUG)
    globalfile_handler.setFormatter(log_format)
    logger.addHandler(globalfile_handler)

    ## Write config versions to cwd
    if run:
        fp = CCS.attachProxy('ucd-fp')
        time.sleep(10.0)
        versions.write_versions(fp)
        configs.write_config(fp, ['Sequencer', 'Rafts'])

    ## Parse config file and execute data acquisition
    try:
        cfg = config.parseConfig(cfgfile)
        config.execute(cfg, {"run" : run})
    except (JException, Exception):
        logger.exception("Fatal error occurred in data acquisition.")


fp = CCS.attachSubsystem("ucd-fp")        
def set_backbias_off():
    fp.sendSynchCommand("R22/Reb0 setBackBias false")

    return True

def set_backbias_on():
    ## Check CCD state
    ccdState = fp.sendSynchCommand("R22/Reb0 getCCDsPowerState")
    if ccdState == 'OFF':
        raise RuntimeError("CCD is not powered on!")

    print "Setting back bias switch on."
    fp.sendSynchCommand("R22/Reb0 setBackBias True")
    return True



supplies = PowerSupplyConfig.Power_Supplies()
back_bias_voltage=52
voltagestep=0.08

date=time.strftime("%Y%m%d")
imagedir='/mnt/10TBHDD/data/'+date

print("get outta there!")
time.sleep(30)
while back_bias_voltage>=48:
    supplies.bss_on_arbitrary_voltage(back_bias_voltage)
    set_backbias_on()
    current_bss=supplies.read_BSS() 
    file = open(imagedir+'/BSS_log.txt', 'a')
    out=current_bss+" "+datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")+"\n"
    file.write(out)       
    file.close()       
    take_biases("/home/ccd/ucd-scripts/eotest-configs/crosstalk_v_bss.cfg","--run")
    set_backbias_off()
    supplies.bss_off()
    back_bias_voltage-=voltagestep
    time.sleep(3)

voltagestep=5
while back_bias_voltage>5:
    supplies.bss_on_arbitrary_voltage(back_bias_voltage)
    set_backbias_on()
    current_bss=supplies.read_BSS() 
    file = open(imagedir+'/BSS_log.txt', 'a')
    out=current_bss+" "+datetime.datetime.now().strftime("%Y%m%d-%H:%M:%S")+"\n"
    file.write(out)       
    file.close()       
    take_biases("/home/ccd/ucd-scripts/eotest-configs/crosstalk_v_bss.cfg","--run")
    set_backbias_off()
    supplies.bss_off()
    back_bias_voltage-=voltagestep
    time.sleep(3)
    
    
