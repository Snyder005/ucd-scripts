import InjectionConfig
import time
#stime=time.time()
date="20240329"
datadir='/mnt/10TBHDD/data/'

imagedir=datadir+date
InjectionConfig.write_fits_headers(imagedir)
InjectionConfig.rename_directory(imagedir,imagedir+"-Injection")
InjectionConfig.eWarning("Finished injection run.")
