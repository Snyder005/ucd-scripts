import sys,time,subprocess
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Stage

stage = Stage.Stage()

time.sleep(5)
pos=stage.read_encoders()
print(pos)

x=-16000
y=8000
z=-422

#pos=stage.move_stage(x=x)
#pos=stage.move_stage(y=y)
#pos=stage.move_stage(z=z)

#pos=stage.go_to(z=z,focus=False)

pos=stage.go_to_exact(z=z)
print(pos)
