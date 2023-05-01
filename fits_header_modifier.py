#!/usr/bin/env python3
from astropy.io import fits
import argparse

def main(infiles):

    for infile in infiles:
        print("Opening {0}".format(infile))
        
        with fits.open(infile) as hdulist:
        
            ## Rename Raft Bay
            hdulist[0].header['RAFTBAY'] = 'R10'
        
            ## Rearrange HDUs
            for i in range(1, 5):
                
                data1 = hdulist[i].data
                data2 = hdulist[9-i].data
                
                hdulist[i].data = data2
                hdulist[9-i].data = data1
            hdulist.writeto(infile.replace('R22', 'R10'))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('infiles', nargs='+')
    args = parser.parse_args()

    main(args)
