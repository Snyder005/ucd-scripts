import sys,time,subprocess
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Stage

stage = Stage.Stage()

#time.sleep(5)
pos=stage.read_encoders()
print(pos)

y=200 #10212

pos=stage.move_stage(y=y)
print(pos)
