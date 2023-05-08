#!/usr/bin/env python3
from astropy.io import fits
import argparse

def main(infiles):

    for infile in infiles:
        print("Opening {0}".format(infile))
        
        with fits.open(infile) as hdulist:
        
            ## Rearrange HDUs
            for i in range(9, 13):
                
                data1 = hdulist[i].data
                data2 = hdulist[25-i].data
                
                hdulist[i].data = data2
                hdulist[25-i].data = data1

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', nargs='+')
    args = parser.parse_args()

    main(args)
