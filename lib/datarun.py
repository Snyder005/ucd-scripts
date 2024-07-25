import re
import ConfigParser
import StringIO
import acquire
import logging

logger = logging.getLogger(__name__)

class DataRun(Object):

    def __init__(self, filename):

        self.parse_config(filename):

    def parse_config(self, filename):
        """Parse a data run configuration file.

        Parameters
        ----------
        filename : `str`
            Data run configuration file name.
        """
        with open(filename) as f:
            lines = f.readlines()

        ## Eliminate inline # delimited comments
        slines = map(lambda l: re.sub(r"([^#]*)\s#.*", r"\1", l), lines)

        config = ConfigParser.SafeConfigParser(allow_no_value=True)
        config.readfp(StringIO.StringIO("".join(slines)))

        self.config = config

    def execute(self,  command_line_options):
        """Execute data run acquisitions based on configuration.

        Parameters
        ----------
        command_line_options: `dict` [`str, `str`]
            Additional command line options for execution:

            ``"run"``
                Run number (`str`).
        """
        ## Get optional data acquisition description
        if self.config.has_section("DESCRIPTION"):
            description = " ".join(self.config.options("DESCRIPTION"))
        else:
            description = None
        logger.info("Run Description: {0}".format(description))
        logger.info("Run Number: {0}".format(command_line_options.get("run", None)))

        ## Get data run acquisitions
        items = config.options("ACQUIRE")
        logger.info("Acquisition Items: {0}".format(", ".join(items)))

        for item in items:
            options = ConfigDict(config.items(item.upper()))
            options.update(command_line_options)
            acq_type = options.get('acqtype', item).upper()
            options.update({'acqtype' : acq_type})

            method = getattr(acquire, 'do_{0}'.format(acq_type.lower()))
            result = method(options) # is this result useful to be returned?

class ConfigDict(dict): ## perhaps move to a utils module?
    """Simple wrapper for a dictionary of data run configuration items.
    """
    def get(self, key, default=None):
        """Extends default `dict.get` method for error handling.

        Raises
        ------
        Exception
            Raised if ``key`` is missing.
        """
        value = super(ConfigDict, dict).get(key, default)
        if value == None:
            raise Exception('Missing config value {0}'.format(key))
        else:
            return value

    def get_int(self, key, default=None):
        """Get dictionary value as type `int`.

        Returns
        -------
        value : `int`
            Value of the item specified by ``key``.

        Raises
        ------
        TypeError
            Raised if ``value`` is not of type `int`.
        """
        value = self.get(key, default)
        return int(value)

    def get_float(self, key, default=None):
        """Get dictionary value as type `float`.

        Returns
        -------
        value : `float`
            Value of the item specified by ``key``.

        Raises
        ------
        TypeError
            Raised if ``value`` is not of type `float`.
        """
        value = self.get(key, default)
        return float(value)

    def get_bool(self, key, default=None):
        """Get dictionary value as type `bool`.

        The dictionary value will be `True` if, following conversion to lower
        case, it is included in the list ``['true', '1', 't', 'y', 'yes']``,
        else it will be `False`.

        Returns
        -------
        value : `bool`
            Value of the item specified by ``key``.
        """
        value = self.get(key, default)
        return value.lower() in ['true', '1', 't', 'y', 'yes']

    def get_list(self, key):
        """Get dictionary value as type `list`.

        Returns
        -------
        value: `list`
            Value of the item specified by ``key`` split into a list by 
            delimiter ``'\n'``.
        """
        value = self.get(key)
        return value.replace('\n', '').split(',')
