import sys,time,subprocess
import StagePosition
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import SphereConfig
import Stage

pos=StagePosition.last_pos
stage = Stage.Stage()
move=stage.read_encoders()
print(pos)

x=pos[0]
y=-1000
z=pos[2]

x=x-pos[0]
y=y-pos[1]
z=z-pos[2]
time.sleep(5)
move=stage.move_stage(x=x,y=y,z=z)
time.sleep(1)
move=stage.move_stage(x=0,y=0,z=-200)
pos=[pos[i]+move[i] for i in range(3)]
print(pos)
time.sleep(5)
move=stage.read_encoders()
pos=[pos[i]+move[i] for i in range(3)]
print(pos)
file = open('/home/ccd/ucd-scripts/danieltests/StagePosition.py', 'w')
file.write("last_pos="+str(pos))
file.close()
