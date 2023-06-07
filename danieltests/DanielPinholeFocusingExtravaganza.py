import sys,time,subprocess
import StagePosition
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import SphereConfig
import Stage

pos=StagePosition.last_pos
stage = Stage.Stage()
move=stage.read_encoders()
print(pos)

x=0
y=300
z=0
steps = 1
file = open('/mnt/10TBHDD/data/20230606/movementlog.txt', 'a')
out="Starting new focus sweep"
file.write(out+'\n')
file.close()
time.sleep(20)
for i in range(steps):
    file = open('/mnt/10TBHDD/data/20230606/movementlog.txt', 'a')
    file.write(str(pos)+'\n')
    file.close()
    subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/examples/spot.cfg',check=True, shell=True)
    time.sleep(1)
    move=stage.move_stage(x=x,y=y,z=z)
    pos=[pos[i]+move[i] for i in range(3)]
    print(pos)
    if i==steps-1:
        file = open('/mnt/10TBHDD/data/20230606/movementlog.txt', 'a')
        file.write(str(pos)+'\n')
        file.close()
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/examples/spot.cfg',check=True, shell=True)

file = open('/home/ccd/ucd-scripts/danieltests/StagePosition.py', 'w')
file.write("last_pos="+str(pos))
file.close()



