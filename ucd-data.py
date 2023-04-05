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
from optparse import OptionParser

# Temporary work around for problems with CCS responsiveness
CCS.setDefaultTimeout(Duration.ofSeconds(30))

## Parse command line options 
parser=OptionParser()
parser.add_option("--run", dest="run")

(options, args) = parser.parse_args()

if len(args)!=1:
  parser.print_help()
  exit(1)

if options.run:
    fp = CCS.attachProxy('ucd-fp')
    time.sleep(10.0)
    versions.write_versions(fp)
    configs.write_config(fp, ['Sequencer', 'Rafts'])

cfg = config.parseConfig(args[0])
config.execute(cfg, {"run": options.run})
