#REB5 POWER STARTUP SCRIPT

#2023-Daniel Polin

#This script turns on the REB5 Power supplies and sets them to the voltages set in 'lib/PowerSupplyConfig.py'. It does not turn on the back bias voltage.

import sys,time
sys.path.append('/home/ccd/ucd-scripts/lib')
import SphereConfig

sphere = SphereConfig.Sphere()

#you only have to initialize these once per usage
sphere.Initialize_Light_Socket() #initialize the light

sphere.Initialize_Shutter_Socket() #initialize the shutter

#you can turn on the light. 
sphere.Turn_Light_On()

#you can turn off the light
sphere.Turn_Light_Off()

#you can change the light intensity between 0% and 100% intensity by changin the shutter position. >99 and <1 are all the way open and closed. We have not recently tested how accurate this is.

light_intensity = 50 #here I just set it to 50, this should probably be set by an external sys argument.

sphere.VA_Set_Light_Intensity(light_intensity)

#you can read the photodiode output
sphere.Read_Photodiode()
