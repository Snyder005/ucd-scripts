#! /usr/bin/env python
import argparse
import time

import Stage

def main(dx=None, dy=None, dz=None):

    print(dx, dy, dz)
    stage = Stage.Stage()
    time.sleep(5)
    position = stage.read_encoders()
    print('Initial: x = {0:d}, y = {1:d}, z = {2:d}'.format(*position))

    if dx is not None:
        position = stage.move_stage(x=dx)
    if dy is not None:
        position = stage.move_stage(y=dy)
    if dz is not None:
        position = stage.move_stage(z=dz)

    print('Current: x = {0:d}, y = {1:d}, z = {2:d}'.format(*position))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=int, default=None)
    parser.add_argument('--y', type=int, default=None)
    parser.add_argument('--z', type=int, default=None)
    args = parser.parse_args()

    main(dx=args.x, dy=args.y, dz=args.z)
