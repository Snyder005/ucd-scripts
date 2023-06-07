#!/usr/bin env ccs-script
#import StageConfig
import time
import logging
import subprocess

logger = logging.getLogger(__name__)

def moveTo(x=0, y=0, z=0):
    logger.info("Moving stage to ({0}, {1}, {2})".format(x, y, z))
    try:
        encoder_output = subprocess.check_output([], shell=True)
    except subprocess.CalledProcessError:
        raise RuntimeError("Stage failed to move.")
