# ucd-scripts
Interim scripts for running UC Davis Beam Simulator.

Current organization

* lib/         -- Scripts intended to be on the CCS "jython path", so installed in ~/ccs/etc or /lsst/ccs/prod/etc
* examples     -- Example configuration file
* ucd-data.py  -- Example top-level script

Can be run as

ccs-script ucd-data.py examples/bias.cfg    

or if ccs-script is on your PATH

./ucd-data.py examples/bias.cfg
