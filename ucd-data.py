#!/usr/bin/env ccs-script
import sys
import time
from org.lsst.ccs.scripting import CCS
from ccs import aliases
from ccs import proxies
from ccs import versions
from ccs import configs
from java.time import Duration
import config
from argparse import ArgumentParser
import logging
import datetime

# Temporary work around for problems with CCS responsiveness
CCS.setDefaultTimeout(Duration.ofSeconds(30))

class WarningFilter(object):

    def filter(self, log_record): 
        return log_record.levelno != logging.WARNING

def main(cfgfile, run=None):

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

    ## Set up handler for observing log
    today = datetime.date.today().strftime("%Y%m%d")
    file_handler = logging.FileHandler('{0}_log.txt'.format(today))
    file_handler.setLevel(logging.INFO)
    file_handler.addFilter(WarningFilter())
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

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
    except Exception:
        logger.exception("Fatal error occurred in data acquisition.")

if __name__ == '__main__':

    parser = ArgumentParser(sys.argv[0])
    parser.add_argument('cfgfile', type=str, help="Data acquisition config file.")
    parser.add_argument('--run', type=str, default=None, help="Run number.")

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    args = parser.parse_args()
    main(args.cfgfile, args.run)
