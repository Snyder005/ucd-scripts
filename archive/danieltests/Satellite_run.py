#!/usr/bin/env ccs-script
import sys,time
import datetime
import ucd_data
import SphereConfig

## Creates a Sphere object and initializes socket connections
sphere = SphereConfig.Sphere()
'''
## Check current before
current = sphere.read_photodiode()
print "Initial current: {0:.3E}".format(current)

#you can turn on the light. 
sphere.turn_light_on()
print "Light turned on."

#you can change the light intensity between 0% and 100% intensity by changin the shutter position. >99 and <1 are all the way open and closed. We have not recently tested how accurate this is.
sphere.set_light_intensity(99)
print "Light intensity set to 20"

#you can read the photodiode output
current = sphere.read_photodiode()
print "New current: {0:.3E}".format(current)



## Creates a Sphere object and initializes socket connections
sphere = SphereConfig.Sphere()

today = datetime.date.today().strftime("%Y%m%d")

sphere.turn_light_on()
print "Light turned on."

file = open('/mnt/10TBHDD/data/'+today+'/intensity_log.txt', 'a')
out="Starting new satellite run"
file.write(out+'\n')
file.close()

intensities=range(1,3,1)

sphere.set_light_intensity(20)
current = sphere.read_photodiode()
for i in intensities:
    sphere.set_light_intensity(i)
    current = sphere.read_photodiode()
    file = open('/mnt/10TBHDD/data/'+today+'/intensity_log.txt', 'a')
    file.write(str(current)+'\n')
    file.close()
    ucd_data.main('/home/ccd/ucd-scripts/eotest-configs/crosstalk-streak.cfg')
    
,
          2,
          2.5,
          3,
          3.5,
          4,
          4.5,
          5,
          5.5,
          6,
          6.5,
          7,
          7.5,
          8,
          8.5,
          9,
          9.5,
          10,
          10.5,
          11,
          11.5,
          12,
          12.5,
          13,
          13.5,
          14,
          14.5,
          15        # exposure time per dither
'''
