#!/usr/bin/env ccs-script
import sys,time
import SphereConfig
import PowerSupplyConfig
from argparse import ArgumentParser
import sys,time


supplies = PowerSupplyConfig.Power_Supplies()

check=supplies.read_volt(printresult=True) #check whether supplies are connected.

'''


def main(light_intensity):

    ## Creates a Sphere object and initializes socket connections
    sphere = SphereConfig.Sphere()

    ## Check current before
    current = sphere.read_photodiode()
    print "Initial current: {0:.3E}".format(current)

    #you can turn on the light. 
    sphere.turn_light_on()
    print "Light turned on."

    #you can change the light intensity between 0% and 100% intensity by changin the shutter position. >99 and <1 are all the way open and closed. We have not recently tested how accurate this is.
    sphere.set_light_intensity(light_intensity)
    print "Light intensity set to {0} %".format(light_intensity)

    #you can read the photodiode output
    current = sphere.read_photodiode()
    print "New current: {0:.3E}".format(current)

    #you can turn off the light
    sphere.turn_light_off()
    print "Lamp turned off."

    current = sphere.read_photodiode()


if __name__ == '__main__':

    parser = ArgumentParser(sys.argv[0])
    parser.add_argument('--intensity', type=int, default=50)
    args = parser.parse_args()

    main(args.intensity)'''
