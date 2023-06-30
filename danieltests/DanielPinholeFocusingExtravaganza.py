import sys,time,subprocess
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import SphereConfig
import Stage


#user inputs
startingz=None #None to not move first
x=0
y=0
z=-200
steps = 10 #0 for one image, no movement

focus=False

#time.sleep(20)

stage = Stage.Stage()

if startingz!=None:
    focus=True
pos=stage.go_to(z=startingz,focus=focus)

#take first image
subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/examples/spot.cfg',check=True, shell=True)
file = open('/mnt/10TBHDD/data/20230628/movementlog.txt', 'a')
out="Starting new focus sweep"
file.write(out+'\n')
file.write(str(pos)+'\n')
file.close()


if steps>0:
    for i in range(steps):
        pos=stage.move_stage(x=x,y=y,z=z)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py /home/ccd/ucd-scripts/examples/spot.cfg',check=True, shell=True)
        file = open('/mnt/10TBHDD/data/20230628/movementlog.txt', 'a')
        file.write(str(pos)+'\n')
        file.close()
        print(pos)
        time.sleep(1)
