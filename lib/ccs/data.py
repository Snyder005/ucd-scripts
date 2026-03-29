#!/usr/bin/env ccs-script
class DeviceError(Exception):

    def __init__(self, message, cause=None):
        super(DeviceError, self).__init__(message)
        self.cause = cause

    def __str__(self):
        result = super(DeviceError, self).__str__()

        cause = self.cause
        while cause is not None:
            result += " -> caused by {0!r}".format(cause)

            if hasattr(cause, "cause"):
                cause = getattr(cause, "cause")
            else:
                cause = None
        return result

class PowerError(DeviceError):
    pass
