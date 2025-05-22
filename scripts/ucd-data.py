#/usr/bin/env ccs-script
import sys
import time
import os
import logging
import datetime
from argparse import ArgumentParser
import threading

from java.time import Duration
import java.lang.Exception as JException

from org.lsst.ccs.scripting import CCS

from ccs import aliases
from ccs import proxies
from ccs import versions
from ccs import configs
import config
import BackBiasCheck # in future maybe rename

# Temporary work around for problems with CCS responsiveness
CCS.setDefaultTimeout(Duration.ofSeconds(30))

class WarningFilter(object):

    def filter(self, log_record): 
        return log_record.levelno != logging.WARNING

def bss_monitor(stop_event, outfile):

    bss = BackBiasCheck.BackBias()
    bss.check_connections()

    with open(outfile, 'a') as f:
        while not stop_event.is_set():
            vss = float(bss.read_BSS())
            iss = float(bss.read_ISS())
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S.%f")
            output = "Vss = {0:.4f}, Iss = {1:.4f}, T = {2}\n".format(vss, iss, current_time)
            f.write(output)
            time.sleep(0.1)

def main(cfgfile, run=None, log_bss=False):

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

    ## Set up background thread
    bss_logfile = os.path.join(rootdir, today, '{0}_bss.log'.format(today))
    stop_event = threading.Event()
    background_thread = threading.Thread(target=bss_monitor, args=(stop_event, bss_logfile))

    ## Optionally start BSS monitor
    if log_bss:
        background_thread.start()

    ## Parse config file and execute data acquisition
    try:
        cfg = config.parseConfig(cfgfile)
        config.execute(cfg, {"run" : run})
    except (JException, Exception):
        logger.exception("Fatal error occurred in data acquisition.")

    ## Stop BSS monitoring if it is running
    if background_thread.is_alive():
        stop_event.set()
        background_thread.join()

if __name__ == '__main__':

    parser = ArgumentParser(sys.argv[0], add_help=False)
    parser.add_argument('cfgfile', type=str)
    parser.add_argument('--run', type=str, default=None)
    parser.add_argument('--log-bss', action='store_true')

    args = parser.parse_args()
    main(args.cfgfile, args.run, args.log_bss)
