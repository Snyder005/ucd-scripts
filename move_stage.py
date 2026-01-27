#!/usr/bin/env python
import time
import argparse
import Stage

#stage = Stage.Stage()

#time.sleep(5)
#pos=stage.read_encoders()
#print(pos)

#x=-(10500/2-300)/2
#x=2*10240
#y=-(10500*3/4)
#z=100#-15000#-100

#pos=stage.move_stage(x=x)
#pos=stage.move_stage(y=y)
#pos=stage.move_stage(z=z)

#pos=stage.go_to(z=z,focus=False)

#pos=stage.go_to_exact(z=z)
#pos=stage.read_encoders()

#print(pos)

def main(dx=None, dy=None, dz=None):

    stage = Stage.Stage()
    
    time.sleep(5)
    position = stage.read_encoders()
    print(position)
    return # debug code

    if x is not None:
        position = stage.move_stage(x=dx)
    
    if y is not None:
        position = stage.move_stage(y=dy)

    if z is not None:
        position = stage.move_stage(z=dz)

    position = stage.read_encoders()
    print(position)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dx', type=str, default=None)
    parser.add_argument('--dy', type=str, default=None)
    parser.add_argument('--dz', type=str, default=None)
    args = parser.parse_args()

    main(dx=args.dx, dy=args.dy, dz=args.dz)
