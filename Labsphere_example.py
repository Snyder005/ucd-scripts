#!/usr/bin/env ccs-script
import sys,time
import SphereConfig
from argparse import ArgumentParser

def main(light_intensity):
    sphere = SphereConfig.Sphere()

    #you only have to initialize these once per usage
    sphere.Initialize_Light_Socket() #initialize the light
    sphere.Initialize_Shutter_Socket() #initialize the shutter

    #you can turn on the light. 
    sphere.Turn_Light_On()

    #you can change the light intensity between 0% and 100% intensity by changin the shutter position. >99 and <1 are all the way open and closed. We have not recently tested how accurate this is.
    sphere.VA_Set_Light_Intensity(light_intensity)

    #you can read the photodiode output
    current = sphere.Read_Photodiode()
    print current

    #you can turn off the light
    sphere.Turn_Light_Off()

if __name__ == '__main__':

    parser = ArgumentParser(sys.argv[0])
    parser.add_argument('--intensity', type=int, default=100)
    args = parser.parse_args()

    main(args.intensity)
