import sys,time,subprocess
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Stage

stage = Stage.Stage()


pos=stage.read_encoders()
print(pos)
x=0
y=0
z=0

#pos=stage.move_stage(x=x,y=y,z=z)
pos=stage.go_to(y=y,focus=False)
print(pos)
