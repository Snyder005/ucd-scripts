#!/usr/bin/env ccs-script
import sys,time
import SphereConfig
from argparse import ArgumentParser

def main(light_intensity):
    sphere = SphereConfig.Sphere()

    #you only have to initialize these once per usage
    sphere.initialize_light_socket() #initialize the light
    sphere.initialize_shutter_socket() #initialize the shutter

    ## Check current before
    current = sphere.read_photodiode()

    #you can turn on the light. 
    sphere.turn_light_on()

    #you can change the light intensity between 0% and 100% intensity by changin the shutter position. >99 and <1 are all the way open and closed. We have not recently tested how accurate this is.
    sphere.va_set_light_intensity(light_intensity)

    #you can read the photodiode output
    current = sphere.read_photodiode()

    #you can turn off the light
    sphere.turn_light_off()

    time.sleep(10.0)
    current = sphere.read_photodiode()

if __name__ == '__main__':

    parser = ArgumentParser(sys.argv[0])
    parser.add_argument('--intensity', type=int, default=50)
    args = parser.parse_args()

    main(args.intensity)
