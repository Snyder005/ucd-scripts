#! /usr/bin/env ccs-script
import argparse
import SphereConfig

def power_sphere_on():

    sphere = SphereConfig.Sphere()

    current = sphere.read_photodiode()
    print "Initial current: {0:.3E}".format(current)

    sphere.turn_light_on()
    print "Light turned on."

    sphere.set_light_intensity(10)
    print "Light intensity set to 10"

    current = sphere.read_photodiode()
    print "New current: {0:.3E}".format(current)

    return True 

def power_sphere_off():

    sphere = SphereConfig.Sphere()

    current = sphere.read_photodiode()
    print "Initial current: {0:.3E}".format(current)

    sphere.turn_light_off()
    print "Light turned off."

    current = sphere.read_photodiode()
    print "New current: {0:.3E}".format(current)

    return True

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(sys.argv[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_false')
    args = parser.parse_args()

    state = args.on and args.off

    if state:
        print(power_sphere_on())
    else:
        print(power_sphere_off())
