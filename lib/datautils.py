#!/usr/bin/env ccs-script
import os
import shutil
from datetime import datetime
import argparse
import copy
from os.path import isdir, isfile, join

DATADIR = '/mnt/10TBHDD/data/'

def reorder_fits_hdus(infile):

    pass

def reorganize_data(date):
    """Reorganize and process data after acquisition.

    Steps include:
    - Modify R22/Reb0/S01 image file to have proper HDU ordering.
    - Move R22/Reb0/S01 image file out of subdirectory
    - Remove R22/Reb0/S00 and R22/Reb0/S02 image files.
    - Remove empty subdirectory.

    Parameters
    ----------
    date : `str`
        Date string formated as YYYYMMDD.
    """

    ## Verify date format
    try:
        datetime.strptime(date, '%Y%m%d')
    except ValueError as e:
        print(e)
        return

    maindir = join(DATADIR, date)

    ## Get subdirectories
    tag = 'TS_C_{0}'.format(date)
    subdirs = [join(maindir, d) for d in os.listdir(maindir) if isdir(join(maindir, d)) if tag in d]
    subdirs.sort()

    for subdir in subdirs:

        filelist = [join(subdir, f) for f in os.listdir(subdir) if isfile(join(subdir, f))]

        ## Move or delete files depending on CCD name
        for infile in filelist:

            if infile.endswith('S01.fits'):

                reorder_fits_hdus(infile)
                try:
                    shutil.move(infile, maindir) # raises IOError if file not found
                    print "{0} moved to {1} successfully.".format(infile, maindir)
                except IOError as e:
                    print e
                    print "Failed to move {0} to {1}.".format(infile, maindir)

            elif infile.endswith('S00.fits') or infile.endswith('S02.fits'):

                try:
                    os.remove(infile) # raises OSError if filepath cannot be removed
                    print "{0} removed.".format(infile)
                except OSError as e:
                    print e
                    print "Failed to remove {0}.".format(infile)

        ## Remove subdirectory if empty
        try:
            os.rmdir(subdir) # raises OSError if not empty
            print "Directory {0} removed.".format(subdir)
        except OSError as e:
            print e
            print "Failed to remove {0}.".format(subdir)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('date', type=str)
    args = parser.parse_args()

    reorganize_data(args.date)
