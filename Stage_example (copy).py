#2023-Daniel Polin
import sys,time
sys.path.append('/home/ccd/ucd-scripts/python-versions')
import Stage

stage = Stage.Stage()

#check=stage.check_communications()
#print(check)

read=stage.read_encoders()
print(read)

x=2
y=3
z=-500
move=stage.move_stage(x=x,y=y,z=z)
print(move)

zero=stage.zero_encoders()
print(zero)
