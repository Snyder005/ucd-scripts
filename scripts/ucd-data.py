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

from ccs.scripting import CCS
import config

# Temporary work around for problems with CCS responsiveness
CCS.setDefaultTimeout(Duration.ofSeconds(30))

class WarningFilter(object):

    def filter(self, log_record): 
        return log_record.levelno != logging.WARNING

def main(cfgfile):

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

    ## Parse config file and execute data acquisition
    try:
        cfg = config.parseConfig(cfgfile)
        config.execute(cfg, {"run" : None}) # is the run object needed?
    except (JException, Exception):
        logger.exception("Fatal error occurred in data acquisition.")

if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('cfgfile', type=str)

    args = parser.parse_args()
    main(args.cfgfile)
