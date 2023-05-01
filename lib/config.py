import re
import ConfigParser
import StringIO
import acquire

def parseConfig(filename):
    with open(filename) as f:
        lines = f.readlines()

    ## Eliminate inline # delimited comments
    slines = map(lambda l: re.sub(r"([^#]*)\s#.*", r"\1", l), lines)
    config = ConfigParser.SafeConfigParser(allow_no_value=True)
    config.readfp(StringIO.StringIO("".join(slines)))
    return config

def execute(config, command_line_options):

    items = config.options("ACQUIRE")
    for item in items:
        options = Config(dict(config.items(item.upper())))
        options.update(command_line_options)
        acq_type = options.get('acqtype')
        if not acq_type:
            acq_type = item
        method = getattr(acquire, 'do_{0}'.format(acq_type))
        options.update({'acqtype' : acq_type.upper()})
        result = method(options)

class Config(dict):
    """Simple wrapper for a dictionary with convenience methods for handling 
    common configuration tasks
    """
    def getInt(self, key, defaultValue=None):
        value = self.get(key)
        if not value:
            if defaultValue != None:
                return defaultValue
            else:
                raise Exception('Missing config value {0}'.format(key))
        return int(value)

    def getFloat(self, key, defaultValue=None):
        value = self.get(key)
        if not value:
            if defaultValue != None:
                return defaultValue
            else:
                raise Exception('Missing config value {0}'.format(key))
        return float(value)

    def getBool(self, key, defaultValue=None):
        value = self.get(key)
        if not value:
            if defaultValue != None:
                return defaultValue
            else:
                raise Exception('Missing config value {0}'.format(key))
        return value.lower() in ['true', '1', 't', 'y', 'yes']

    def getList(self, key):
        return self.get(key).replace('\n', '').split(',')
