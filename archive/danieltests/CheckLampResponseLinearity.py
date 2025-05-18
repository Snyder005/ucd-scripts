#!/usr/bin/env ccs-script
import sys,time
import SphereConfig
from argparse import ArgumentParser

## Creates a Sphere object and initializes socket connections
sphere = SphereConfig.Sphere()

sphere.turn_light_on()

intensities=range(0,101,5)

for intensity in intensities:
    sphere.set_light_intensity(intensity)
    current = sphere.read_photodiode()
    result=str(intensity)+" "+str(current)
    f=open("diode_settings.txt",'a')
    f.write(result+"\n")
    f.close()
    print result
    
sphere.turn_light_off()
