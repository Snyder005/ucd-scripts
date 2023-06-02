# Data Acquisition Configuration File Documentation

Data acquisition is performed by defining the desired test and image configurations in a CFG file. To run a data acquisition, the configuration file is passed as a command-line argument to the main `ucd-data.py` script that is run in the `ccs-script` Jython environment.

## Sections

The data acquisition configuration file consists of several sections that define different aspects of the data acquisition include the test types to be run, a top-level description of the data acquisition, and sections dedicated to the configuration of the individual test types. Each section consists of a capitalized descriptor contained in square brackets. Here we will cover the different sections in detail.

### ACQUIRE Section

The `ACQUIRE` section is a required section in every data acquisition configuration file. It is used to define the test types to be performed in the acquisition. Possible test types include: bias, dark, flat, spot, and persistence. In addition, the `ACQUIRE` sections defines the additional sections that must be included in the configuration file.  

Example:

    [ACQUIRE]
    bias
    dark
    flat

In the above example the `ACQUIRE` section details three different test types that will be performed by the acquisition script: bias, dark, and flat. The configuration file must therefore also contain a `BIAS`, `DARK`, and `FLAT` section.

### DESCRIPTION Section

The `DESCRIPTION` section is an optional section that allows for a top-level, human-readable description of the purpose of the data acquisition configuration file. This description can span multiple lines, and will be recorded in the output of the human-readable log file. 

Example:

    [DESCRIPTION]
    This is an example top-level description.
    The description can include multiple lines.
    Separate lines will be concatenated in the log file.

### BIAS Section

The `BIAS` section is used to define a test consisting of only bias images. 

* ANNOTATION
