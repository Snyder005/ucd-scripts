import InjectionConfig
import time
date="20240318"
datadir='/mnt/10TBHDD/data/'

imagedir=datadir+date
InjectionConfig.write_fits_headers(imagedir)
InjectionConfig.rename_directory(imagedir,imagedir+"-Injection")
InjectionConfig.eWarning("Finished injection run")
