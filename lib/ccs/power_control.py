from ccs.data import PowerException

class PowerControl(object):

    def __init__(self, name, devc, hw_chan, op_voltage, op_current=None):
        self.name = name
        self.devc = devc
        if (hw_chan < self.devc.MIN_CHAN) or (hw_chan > self.devc.MAX_CHAN)
            raise PowerException('HW channel number is invalid: {0}'.format(hw_chan))
        else:
            self.hw_chan = hw_chan
        self.op_voltage = op_voltage
        self.op_current = op_current # Current limit only for HV Bias

    def get_state(self):
        try:
            state = self.read_output()
            voltage = 0.0 if state == 'NC' else self.read_voltage()
            current = 0.0 if state == 'NC' else self.read_current()
        except PowerException:
            state = 'NC'
            voltage = 0.0
            current = 0.0

        return self.name, state, voltage, current

    def read_voltage(self):
        return self.devc.read_voltage(self.hw_chan)

    def write_voltage(self):
        self.devc.write_voltage(self.op_voltage, self.hw_chan)
    
    def read_current(self):
        return self.devc.read_current(self.hw_chan)

    def write_current(self): # Current limit only for HV Bias
        if self.op_current is not None:
            self.devc.write_current(self.op_current, self.hw_chan)

    def read_output(self):
        return self.devc.read_output(self.hw_chan)

    def write_output(self, state):
        self.devc.write_output(state, self.hw_chan)

    def power_on(self):
        self.write_voltage()
        #self.write_current()
        self.write_output('ON')

    def power_off(self):
        self.write_output('OFF')
