#!/usr/bin env ccs-script
#import StageConfig
import time

def moveTo(x=0, y=0, z=0):
    pass
#    print "Moving stage to ({0}, {1}, {2})".format(x, y, z)
#    for axis, value in [('x', x), ('y', y), ('z', z)]:
#       StageConfig.move_to(axis, value)
#       waitForMove(axis)

def waitForMove(axis):
    raise NotImplementedError
#    time.sleep(1)
#    while StageConfig.is_moving(axis):
#        time.sleep(0.01)
