#!/usr/bin/env python3
from astropy.io import fits
import argparse
import copy
import subprocess
import os
import glob
from datetime import datetime

DATADIR = '/mnt/10TBHDD/data/'

def main(date):

    ## Verify date format
    try:
        datetime.strptime(date, '%Y%m%d')
    except ValueError as e:
        print(e)
        return 1

    maindir = os.path.join(DATADIR, date)
    subdirs = os.path.join(maindir, 'TS_C_*')

    ## Reorder amplifiers
    infiles = glob.glob(os.path.join(subdirs, '*S01.fits'))
    if len(infiles) == 0:
        print('No files found in directory: {0}'.format(maindir))
        return 1

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

    ## Move FITs files
    try:
        subprocess.run('mv {0}/*S01.fits {1}/.'.format(subdirs, maindir),
                        check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print("Failed to move FITs files.")
        return 1
 
    ## Delete remaining files and folder
    try:
        subprocess.run('rm {0}/*S00.fits {0}/*S02.fits'.format(subdirs), check=True, shell=True)
        subprocess.run('rmdir {0}/'.format(subdirs), check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print("Failed to remove subdirectories.")
        return 1

    return 0

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Reorganize/process FITs files in a directory.')
    parser.add_argument('date', type=str, 
                        help='Target date with format YYYYMMDDDD')
    args = parser.parse_args()

    main(args.date)
