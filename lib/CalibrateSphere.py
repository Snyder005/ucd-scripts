#!/usr/bin/env ccs-script
import sys,time
import SphereConfig

## Creates a Sphere object and initializes socket connections
sphere = SphereConfig.Sphere()


sphere.calibrate_aperature()

'''##Turn on the sphere
sphere.turn_light_on()


##
stime=time.time()
step=-30

##Make the Look Up Table File
file = open('/home/ccd/ucd-scripts/lib/SphereLookUpTable.txt', 'w')
out=str(step)+"\n"
file.write(out)
file.close()

n=0
for i in range(abs(12000/step)+2):
    sphere.drive_aperture(12000)
    time.sleep(0.5)
    sphere.drive_aperture(step*i)
    current = sphere.read_photodiode()
    file = open('/home/ccd/ucd-scripts/lib/SphereLookUpTable.txt', 'a')
    file.write(str(current)+'\n')
    file.close()
    print(i*step,current)
    time.sleep(0.5)


#Turn off the Sphere at the end
sphere.turn_light_off()

print("Done. Took: "+str(time.time()-stime)+"s for "+str(abs(12000/step))+" steps")'''
