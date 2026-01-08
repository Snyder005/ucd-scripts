#!/usr/bin/env ccs-script
import csv
import time
import argparse
import ucd_sphere

def main(outfile, step=-30):

    start = time.time()
    sphere = ucd_sphere.Sphere()
    sphere.turn_light_on()

    numsteps = int(abs(12000/step)+2)
    steps = []
    currents = []
    for i in range(numsteps):
        sphere.drive_aperture(12000)
        time.sleep(0.5)
        sphere.drive_aperture(step*i) # check this
        current = sphere.read_photodiode()
        
        steps.append(step*i)
        currents.append(current)
        time.sleep(0.5)

    intensities = [100*current/max(currents) for current in currents]
    index = intensities.index(max(currents))
    steps = steps[index:]
    intensities = intensities[index:]
    fields = ['Steps', 'Intensity']
    columns = [steps, intensities]

    with open(outfile, 'w'):

        writer = csv.writer(csvfile)
        writer.writerow(fields)
        writer.writerows(rows)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('outfile', type=str)
    parser.add_argument('--step', '-s', type=int, default=-30)

    args = parser.parse_arg()
    main(args.outfile, step=args.step)
