import argparse

def on():

    print "Power on."

def off():

    print "Power off."

if __name__ == '__main__':

    parser = argparse.ArgumentParser('test.py')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--on', action='store_true')
    group.add_argument('--off', action='store_false')
    args = parser.parse_args()

    state = args.on and args.off

    if state:
        on()
    else:
        off() 
