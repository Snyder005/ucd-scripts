#!/usr/bin/env python3
from astropy.io import fits
import argparse
import copy

def main(infiles):

    for infile in infiles:
        print("Opening {0}".format(infile))
        
        with fits.open(infile, mode='update') as hdulist:
        
            ## Check file history
            if 'HISTORY' in hdulist[0].header:
                print("Amps already reordered! Skipping...")
                continue

            ## Rearrange HDUs
            for i in range(9, 13):
                
                data1 = copy.deepcopy(hdulist[i].data)
                data2 = copy.deepcopy(hdulist[25-i].data)
                
                hdulist[i].data = data2
                hdulist[25-i].data = data1

            hdulist[0].header.add_history('Amp Order Fixed.')
            hdulist.flush()
            print("Amp order fixed.")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', nargs='+')
    args = parser.parse_args()

    main(args.infiles)
