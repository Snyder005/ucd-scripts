# Data Acquisition Configuration File Documentation

Data acquisition is performed by defining the desired test and image configurations in a CFG file. To run a data acquisition, the configuration file is passed as a command-line argument to the main `ucd-data.py` script that is run in the `ccs-script` Jython environment.

## Sections

The data acquisition configuration file consists of several sections that define different aspects of the data acquisition include the test types to be run, a top-level description of the data acquisition, and sections dedicated to the configuration of the individual test types. Each section consists of a capitalized descriptor contained in square brackets. Here we will cover the different sections in detail.

### ACQUIRE Section

The `ACQUIRE` section is a required section in every data acquisition configuration file. It is used to define the test types to be performed in the acquisition. Standard test types include: bias, dark, flat, spot, and persistence. For every test type included in the `ACQUIRE` section there must be a corresponding section with the same name included in the configuration file.  

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

The `BIAS` section is used to define a test consisting of only bias images. It is the simplest test type and can contain the following key name, value pairs.

* ANNOTATION

The annotation name, value pair is optional and allows for a short description that will be included in the output FITS file primary header. The default value is an empty string.

* LOCATIONS

The locations name, value pair is required and specifies the locations of the CCDs to be read out during the acquisition. The required value for the UC Davis Beam Simulator is R22/Reb0.

* CLEARS

The clears name, value pair is optional and specifies the number of clears to perform per image readout. The default value is 1.

* EXTRADELAY

The extra delay name, value pair is optional and specifies the delay (in seconds) between image acquisitions. The default value is 0.

* DESCRIPTION

The description name, value pair is optional and allows for a human-readable description of the purpose of the bias test to be recorded in the output of the human-readable log-file. The default value is None.

* COUNT

The count name, value pair is required and sepcifies the number of bias images to be taken in the acquisition.

Example:

    [BIAS]
    ANNOTATION = Just R22/Reb0
    LOCATION = R22/Reb0
    DESCRIPTION = 5 bias images.
    COUNT = 5

In the above example the `BIAS` section details an acquisition consisting of 5 bias images. The `CLEARS` and `EXTRADELAY` name, value pairs are allowed to be their default values.

### DARK Section

The `DARK` section is used to define a test consisting of dark images, with a configurable number of interleaved bias images. It can contain the following key name, value pairs.

* ANNOTATION

The annotation name, value pair is optional and allows for a short description that will be included in the output FITS file primary header. The default value is an empty string.

* LOCATIONS

The locations name, value pair is required and specifies the locations of the CCDs to be read out during the acquisition. The required value for the UC Davis Beam Simulator is R22/Reb0.

* CLEARS

The clears name, value pair is optional and specifies the number of clears to perform per image readout. The default value is 1.

* EXTRADELAY

The extra delay name, value pair is optional and specifies the delay (in seconds) between image acquisitions. The default value is 0.

* DESCRIPTION

The description name, value pair is optional and allows for a human-readable description of the purpose of the bias test to be recorded in the output of the human-readable log-file. The default value is None.

* BCOUNT

The bcount name, value pair is optional and specifies the number of bias images per set of dark images. The default value is 1.

* dark

The dark name, value pair is required and specifies a list of dark image acquisitions, consisting of comma separated lines. Each line consists of two values, an integration time (in seconds) and a dark image count. The final line should not include a concluding comma.

Example:

    [DARK]
    LOCATIONS = R22/Reb0
    DESCRIPTION = A set of two 10 second dark images and a set of two 60 second dark images.
    BCOUNT = 1
    
    dark = 10 2,
           60 2

In the above example we are taking two sets of dark images, some at 10 seconds and some at 60 seconds. The `BCOUNT` name, value pair indicates that there will be one bias image between each dark image taken.

### FLAT Section
