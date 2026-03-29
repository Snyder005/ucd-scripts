#!/usr/bin/env ccs-script
class DeviceException(Exception):

    def __init__(self, message):
        self.message = message
        super(PowerException, self).__init__(self.message)

class PowerException(Exception):

    def __init__(self, message):
        self.message = message
        super(PowerException, self).__init__(self.message)
