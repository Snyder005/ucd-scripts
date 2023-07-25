# UC Davis Beam Simulator Data Management

The UC Davis Beam Simulator data is publically available as a shared Butler Gen 3 Repository (

## Data Compression

Data compression is performed locally on the Viscacha laboratory computer. Image data is stored on a dedicated 10 TB hard drive, mounted at `/mnt/10TBHDD`, under the subdirectory `data` and organized by acquisition date. All FITS files are compressed using `fpack` (see [FPACK documentation](https://heasarc.gsfc.nasa.gov/fitsio/fpack/)).  To match Rubin DM convention all compressed FITS files retain their original file names and extensions.

Example:

    ccd@viscacha:~$  fpack -F -Y -v /mnt/10TBHDD/data/20230620/*.fits

The above will compress all FITS files located in the subdirectory for 2023-06-20, where `-F` forces the input file to be ovrwritten by the compressed file with the same name, `-Y` suprsses the promprts to confirm the `-F` option, and `-v` enables verbose mode where each file is listed as it is processed.  This also demonstrates that the input files may contain the usual wild card characters (`*`, `?`, etc.) that will be expanded by the shell.

## Data Transfer

Currently the local data is mirrored to USDF using `rsync` after compression (see [RSYNC documentation](https://linux.die.net/man/1/rsync)). The dedicated disk space for the UC Davis Beam Simulator image data is located at `/sdf/data/rubin/offline/ucd/` and organized into subdirectories named by acquisition date. This process is done using the USDF data transfer nodes `sdfdtn001` or `sdfdtn002`, rather than the usual login or development nodes.

Example:

    ccd@viscacha:~$  rsync -av /mnt/10TBHDD/20230620 snyder18@sdfdtn001.slac.stanford.edu:/sdf/data/rubin/offline/ucd

The above will copy the directory `/mnt/10TBHDD/20230620` and all its contents to the directory `/sdf/rubin/offline/ucd`. The user login must have write permissions to the USDF data locations.

## Butler Ingest

The remote data at USDF is ingested into a dedicated Gen 3 Repository, to be used for data analysis using the DM Science Pipelines. This repository is located at `/sdf/group/rubin/repo/ucd`. 

Example:

    (lsst-scipipe-6.0.0) [snyder18@sdfrome002 ~]$ butler ingest-raws --transfer direct /sdf/group/rubin/repo/ucd /sdf/data/rubin/offline/ucd/20230620

The above will ingest the raw (compressed) FITS files in the directory `sdf/data/rubin/offline/ucd/20230620` into the Gen 3 repository at `/sdf/group/rubin/repo/ucd`.
