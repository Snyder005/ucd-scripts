import sys,time,subprocess
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Stage

stage = Stage.Stage()

#time.sleep(5)
pos=stage.read_encoders()
print(pos)
x=500
y=-9000
z=17000

#pos=stage.move_stage(x=x,y=y,z=z)
pos=stage.go_to(z=z,focus=False)
print(pos)
