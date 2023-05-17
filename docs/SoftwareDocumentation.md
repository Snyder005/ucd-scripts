# Introduction

CCS is a set of software packages designed to provide control of all subsystems required for operation of the LSST Camera including power supplies, focal plane operation, image handling, optical equipment, and refrigeration.  The UC Davis CCS installation is installed on the laboratory computer Viscacha and is comprised of two subsystems: the focal plane subsystem `ucd-fp` and the image handling subsystem `ucd-ih`.  

# DAQ Documentation

## How to restart the DAQ

# CCS Documentation

## Troubleshooting

The following documents some common errors that may be encountered when attempting to operate the system using CCS.

### Triggering image in folder raw failed

This error is raised by the `endIntegration` CCS command if there was an error in triggering the image, which can have a number of different causes. For specific solutions, refer to the exact error codes encountered.

* rc=2 Status is 2: Request posted to sequencer timed out (service running?)

This is caused by the synchronous command service having been started before the partition service was running on the management node. To fix, log in to the DAQ and restart `scs`.

Example:

    ccd@vischa:~$  ssh root@`atca_ip darwin/1/4/0 --ifname lsst-daq
    root@192.168.100.236's password:                               
    Last login: Fri Jul 22 17:48:16 2022 from 192.168.100.1
    [root@darwin/1/4/0 ~]# systemctl restart scs

* rc=7 Status is 0: Request completed successfully

This is caused by the catalog server on the DAQ ATCA crate not running. To fix, log in to and reset the DAQ (See [How to Restart the DAQ](#How-to-restart-the-DAQ)).

* 

