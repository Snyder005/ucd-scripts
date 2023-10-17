# CCS Documentation

The UC Davis CCS installation consists of the focal plane subsystem `ucd-fp` and image handler service `ucd-ih`. There are also three CCS Applications that are used for operation of the UC Davis Beam Simulator test stand: the CCS shell environment `ccs-shell`, the CCS GUI `ccs-console`, and the CCS scripting environment `ccs-script`.

## CCS Start-up

When first initialized (i.e. after a reboot of the laboratory computer), it is necessary to start the various CCS subsystems and auxillary programs used for CCS operation. This includes the focal plane (`ucd-fp`), image handler (`ucd-ih`), and the database (`h2db`) subsystems:

    ccd@viscacha:~$  sudo systemctl start ucd-fp
    ccd@viscacha:~$  sudo systemctl start ucd-ih
    ccd@viscacha:~$  sudo systemctl start h2db

To check the status of a subsystem:

    ccd@viscacha:~$  sudo systemctl status ucd-fp

To restart a subsystem:

    ccd@viscacha:~$  sudo systemctl restart ucd-fp

To stop a subsystem:

    ccd@viscacha:~$  sudo systemctl stop ucd-fp

## CCS Applications

### CCS Shell

The CCS shell environment `ccs-shell` is used to issue CCS commands from a command line. To run, type:

    ccd@viscacha:~$  ccs-shell

CCS commands have a specific syntax and often require specifying the exact CCS subsystem to issue the command to. Usage of the `ccs-shell` is covered in [
System Operation Using CCS](#System-Operation-Using-CCS).

### CCS GUI

The CCS GUI `ccs-console` can be used for monitoring of all CCS subsystems as well as for issuing CCS commands via a CCS shell command line.  To run simply type:

    ccd@viscacha:~$  ccs-console

This will spawn a "blank" instance of the CCS GUI. This can be populated with windows by selecting from the top tool bar.  To open a CCS shell command line, select "Command Line" under the "CCS Tools" option in the tool bar.  The CCS shell command line can then be used exactly as `ccs-shell` to issue CCS commands.  To spawn a monitoring window, select the desired subsystem under "CCS Subsystems" in the tool bar and then select "Default Monitor". This will spawn a tree of monitoring options that can be expanded to view the desired values.

### CCS Scripting Environment

The CCS scripting environment `ccs-script` is used for scripting in the CCS Jython environment and is analogous to `python` or `python3`. There are a number of subtle differences.  The CCS Jython environment is an implementation of the Python programming language designed to run on the Java platform.  All modules in the standard Python distribution are included, except for those implemented originally in C. Jython allows for the use of any Java class and will often rely on Java classes instead of Python modules.

To spawn an interactive CCS Jython environment type:

    ccd@viscacha:~$  ccs-shell
    CCS jython 2.7.2
    >>> 

To run a script written in Jython type:

    ccd@viscacha:~$  ccs-shell my_jython_script.py

Or

    ccd@viscacha:~$  ./my_jython_script.py

If the shebang line is set to `#! /usr/bin/env ccs-script`.

The UC Davis Beam Simulator test stand acquisition script `ucd-data.py` is a Jython script used to automate image acquisition using configurations set by YAML files.

## System Operation Using CCS

It is possible to operate the UC Davis Beam Simulator from `ccs-shell` command line using CCS commands. Although automated scripting using `ccs-script` is preferred, the CCS shell environment can be useful for monitoring, viewing configurable parameters, and modifying configurable parameters. The `ccs-shell` command line includes a tab completion mechanism and a `help` function, to assist in determining appropriate CCS commands. The following demonstrate different use cases of the CCS shell environment and include full examples used in actual system operation.

### Check Focal Plane State

To check the focal plane state:

    ccs>set target ucd-fp
    ucd-fp ccs>getState
    AlertState:ALARM CommandState:READY ConfigurationState:DIRTY FocalPlaneState:QUIESCENT OperationalState:ENGINEERING_FAULT PhaseState:OPERATIONAL SequencerState:IDLE
    R22/Reb0: CCDsPowerState:ON HVBiasState:OFF RebDeviceState:ONLINE RebValidationState:VALID
    R22/Reb1: CCDsPowerState:UNKNOWN HVBiasState:UNKNOWN RebDeviceState:OFFLINE RebValidationState:UNKNOWN
    R22/Reb2: CCDsPowerState:UNKNOWN HVBiasState:UNKNOWN RebDeviceState:OFFLINE RebValidationState:UNKNOWN

This will show the global state of the focal plane (`FocalPlaneState`), the sequencer state (`SequencerState`) and the configuration state (`ConfigurationState`). For each of the possible REBs this will show the CCD power (`CCDsPowerState`), the Back Bias voltage relay (`HVBiasSwitch`).  For the UC Davis Beam Simulator, only a single REB is enabled, R22/Reb0.

Note that since the `getState` command is being issued to the `ucd-fp` subsystem, the `set target` command was used to select `ucd-fp`. This isn't necessary, but greatly simplifies commands if a large number will be issued to the same subsystem. For instance, to designate a target subsystem for a single command:

    ccs>ucd-fp getState
    AlertState:ALARM CommandState:READY ConfigurationState:DIRTY FocalPlaneState:QUIESCENT OperationalState:ENGINEERING_FAULT PhaseState:OPERATIONAL SequencerState:IDLE
    R22/Reb0: CCDsPowerState:ON HVBiasState:OFF RebDeviceState:ONLINE RebValidationState:VALID
    R22/Reb1: CCDsPowerState:UNKNOWN HVBiasState:UNKNOWN RebDeviceState:OFFLINE RebValidationState:UNKNOWN
    R22/Reb2: CCDsPowerState:UNKNOWN HVBiasState:UNKNOWN RebDeviceState:OFFLINE RebValidationState:UNKNOWN

The command line prompt will indicate the current target subsystem (e.g. `ccs>` compared to `ucd-fp ccs>`).

### Power On CCD

Before proceeding the following must be verified:

* All power supplies must be on and set to the appropriate voltages.
* The back bias relay on the REB5 must be closed, indicated by the state of the focal plane subsystem `HVBiasState:OFF`. To check back bias relay state:

    ucd-fp ccs>R22/Reb0 isBackBiasOn

* Voltage limits have been properly configured. See [Configuring Voltage Limits](#Configuring-Voltage-Limits)

To power on the CCD:

    ucd-fp ccs>R22/Reb0 powerCCDsOn
    ucd-fp ccs>R22/Reb0 setBackBias true

This will begin the power on procedure for R22/Reb0.     

### Power Off CCD

To power off the CCD:

    ucd-fp ccs>R22/Reb0 setBackBias false
    ucd-fp ccs>R22/Reb0 powerCCDsOff

This will close the back bias voltage relay and run the power off procedure for R22/Reb0.

### Basic Image Acquisition

To perform an image acquisition by hand using CCS commands:

    ucd-fp ccs>startIntegration "test" [R22/Reb0]
    ucd-fp ccs>endIntegration
    ucd-fp ccs>waitForFitsFiles

This will begin the integration for R22/Reb0, end the integration, and trigger the reading of the output FITs files from the DAQ datastore. If the CCDs are power off this will only read out the REB5. If the CCDs are powered on this will be a true image acquisition.

### Configure Voltage Limits

The REB5 can be used to operate 3 CCDs simultaneously, however the UC Davis Beam Simulator only uses a single CCD, leaving the other two connections open. For this reason it is necessary to modify some of the default voltage limits.  The commands to do so are:

    ucd-fp ccs>R22/Reb0/Bias0 change odZeroErr 1.0
    ucd-fp ccs>R22/Reb0/Bias1 change odZeroErr 1.0
    ucd-fp ccs>R22/Reb0/Bias2 change odZeroErr 1.0
    ucd-fp ccs>R22/Reb0/Bias0 change odTol 0.3
    ucd-fp ccs>R22/Reb0/Bias1 change odTol 0.3
    ucd-fp ccs>R22/Reb0/Bias2 change odTol 0.3
    ucd-fp ccs>R22/Reb0/Bias1 change gdTol 0.2

These will change the error on the output drain voltage zero error to 1.0 and set point tolerance to 0.3 V for all three CCD connections (Bias0, Bias1, Bias2). Additionally, the guard drain voltage set point tolerance is changed to 0.2 V for only the connected CCD (Bias1).

## CCS Configurations

The configuration of CCS subsystems is done using a set of `properties` files that can be found in the `${HOME}/ccs/etc` directory. 

### Focal Plane Configurations

* `FocalPlane_common_General.properties`

Specifies a series of variables for the `imageNameService`.

* `FocalPlane_common_Sequencer.properties`

Used to specify and configure sequencer parameters.

* `FocalPlane_v26_Sequencer.properties`

Additional sequencer configurations for a specific CCS version.

* `FocalPlane_ucd_General.properties`

Additional specifications specific to the UCD test stand.

* `FocalPlane_ucd_build.properties`

Used to specify the focal plane rafts and CCD types.

* `FocalPlane_common_DAQ.properties`

Used to set generic `sequencerConfig` variables.

* `FocalPlane_ucd_DAQ.properties`

Used to set the name of the DAQ partition via `sequencerConfig/daqPartition=davis`.

* `FocalPlane_ucd_Devices.properties`

Used to enable/disable sensors by Reb.

* `FocalPlane_ucd_HardwareId.properties`

Used to specify the names and serial numbers of the Raft, REB, and CCDs.

* `FocalPlane_ucd_Instrument.properties`

Used to set the `instrumentConfig` variables including test stand, instrument, and camera name.

* `FocalPlane_ucd_Limits.properties`

Used to set the warning limits for REB voltage and current monitoring.

* `FocalPlane_ucd_Rafts.properties`

Used to set raft voltages and ASPIC parameters.

* `FocalPlane_ucd_RaftsLimits.properties`

Used to set raft voltage software limits.

* `FocalPlane_ucd_RaftsPower.properties`

Sets voltage and current test parameters for CCD power on.

* `FocalPlane_ucd_RaftTempControl.properties`

Used to set the temperature control variables for each raft.

* `FocalPlane_ucd_RaftTempControlStatus.properties`

Used to toggle temperature control status.

* `FocalPlane_ucd_timers.properties`

Used to specify the read time for monitoring tasks.

* `FocalPlane_ucd_Visualization.properties`

Used to set possible web visualization.

## Troubleshooting

The following documents some common errors that may be encountered when attempting to operate the system using CCS.

### Error dispatching command: Command not accepted in state...

This error is raised when attempting to issue a CCS command while the subystem is in an improperly configured state. Some examples of this include `FocalPlaneState:NEEDS_CLEAR` or `FocalPlaneState:INTEGRATING`.  To fix, it is necessary to return the `ucd-fp` subsystem to `FocalPlaneState:QUIESCENT` and `SequencerState:IDLE`.  This can be done by clearing the CCD or by ending the integration.

Example:

To clear the focal plane, in `ccs-shell`:

    ccs>ucd-fp clear

To forcibly end integration, in `ccs-shell`:

    ccs>ucd-fp endIntegration false

### Triggering image in folder raw failed

This error is raised by the `endIntegration` CCS command if there was an error in triggering the image, which can have a number of different causes. For specific solutions, refer to the exact error codes encountered.

* rc=7 Status is 0: Request completed successfully

This is caused by the catalog server on the DAQ ATCA crate not running. To fix, log in to and reset the DAQ by using `minicom`.

Example:

    ccd@viscacha:~$  ssh root@`atca_ip darwin/1/4/0 --ifname lsst-daq`
    root@192.168.100.236's password:
    Last login: Fri Jul 22 17:48:16 2022 from 192.168.100.1
    [root@darwin/1/4/0 ~]# minicom -w bay0.0

    Welcome to minicom 2.7

    OPTIONS: I18n
    Compiled on Jan 11 2014, 04:10:34.
    Port /dev/ttyUSB1

    Press CTRL-A Z for help on special keys


    [/] # reboot

Failing this, use:

    ccd@viscacha:~$  cob_rce_reset darwin-sm/1/0/0

* rc=36 Status is 0: Request completed successfully

This is caused by the DAQ client being unable to write the image metadata to the DAQ datastore. To fix, restart the `rce` proxy, the focal plane subsystem, and the image handler service.

Example:

    ccd@viscacha:~$  sudo systemctl restart rce
    ccd@viscacha:~$  sudo systemctl restart ucd-fp
    ccd@viscacha:~$  sudo systemctl restart ucd-ih 

 * rc=2 Status is 2: Request posted to sequencer timed out (service running?)

This is caused by the synchronous command service having been started before the partition service was running on the management node. To fix, log in to the DAQ and restart `scs`.

Example:

    ccd@viscacha:~$  ssh root@`atca_ip darwin/1/4/0 --ifname lsst-daq`
    root@192.168.100.236's password:                               
    Last login: Fri Jul 22 17:48:16 2022 from 192.168.100.1
    [root@darwin/1/4/0 ~]# systemctl restart scs

* rc=3 Status is 3: Wakeup posted to the readout services timed out (services not running?)

This error indicates a problem with the CCS communicating with the DAQ datastore. This is most likely caused by ommitting REB location information (R22/Reb0) from the `startIntegration` command.
