import numpy as np
import time,subprocess,datetime,sys,glob,random
from astropy.io import fits
sys.path.append('/home/ccd/ucd-scripts/python-lib')
import Email_Warning

persistencecfgfile="50_15s_200sofDarks.cfg"
sleeptime=30

date=time.strftime("%Y%m%d")
imagedir='/mnt/10TBHDD/data/'+date

def take_data(cfgfile):
    try:
        subprocess.run('ccs-script /home/ccd/ucd-scripts/ucd-data.py '+cfgfile,check=True, shell=True)
        power_light("off")
    except:
        power_light("off")
    return
    
#def make_imagedir()

def power_CCD(state):
    if state=="off" or state=="OFF" or state=="Off":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py R21 --off',check=True, shell=True)
        time.sleep(2)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py R21 --off',check=True, shell=True)
    elif state=="on" or state=="ON" or state=="On":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/powerCCD.py R21 --on',check=True, shell=True)
        time.sleep(2)
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/setBackBias.py R21 --on',check=True, shell=True)
    
def power_light(state):
    if state=="off" or state=="OFF" or state=="Off":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOff.py',check=True, shell=True)
    elif state=="on" or state=="ON" or state=="On":
        subprocess.run('ccs-script /home/ccd/ucd-scripts/scripts/sphereOn.py',check=True, shell=True)

def remove_fits_files(imagedir):
    subprocess.run('rm '+imagedir+'/TS_C_*',check=True, shell=True)
    
def copy_file_to_imagedir(file):
    subprocess.run('cp '+file+" "+imagedir,check=True, shell=True)
    
def move_files_to_new_directory(directory,filename):
    subprocess.run('mkdir '+imagedir+"/"+filename,=True, shell=True)
    subprocess.run('mv '+directory+"/TS_C* "+imagedir+"/"+filename,check=True, shell=True)
    
def eWarning(warning):
    try:
        subject = "CCD LAB UPDATE " + time.asctime()
        w_file = open('/home/ccd/ucd-scripts/python-lib/send_warning', 'w')
        w_file.write(subject + ":: ")
        w_file.write(warning)
        w_file.close()
        Email_Warning.Send_Warning(subject, warning)
    except:
        pass
        
def getvoltages( pl, pswing, sswing, rgswing, drd=8.0, **kwargs ):
    pl_off = 0.0
    pu_off = 0.0
    rd_off = 0.0
    od_off = 0.0
    og_off = 0.0
    sl_off = 0.0
    sh_off = 0.0
    rgl_off = 0.0
    rgh_off = 0.0
    gd_off = 0.0
    chz = 11
    # Rules to set the voltages
    pl0 = pl			 # nominal
    pl1 = pl0 + pl_off   # corrected
    #
    pu0 = pl0 + pswing	# nominal based on pl nominal
    pu1 = pu0 + pu_off   # corrected
    #
    rd0 = pu0 + drd
    rd1 = rd0 + rd_off
    #
    od0 = rd0 + 11.8
    od1 = od0 + od_off
    #
    og0 = rd0 - chz - 4
    og1 = og0 + og_off
    #
    sl0 = og0 - 2.0
    sl1 = sl0 + sl_off
    #
    sh0 = sl0 + sswing
    sh1 = sh0 + sh_off
    #
    rgh0 = rd0 - 5.5
    rgh1 = rgh0 + rgh_off
    #
    rgl0 = rgh0 - rgswing
    rgl1 = rgl0 + rgl_off
    #
    gd0 = 26
    gd1 = gd0 + gd_off
    #
    # Apply the offsets
    # pl = pl + pl_off
    # pu = pu + pu_off
    # rd = rd + rd_off
    # od = od + od_off
    # og = og + og_off
    # sl = sl + sl_off
    # sh = sh + sh_off
    # rgh = rgh + rgh_off
    # rgl = rgl + rgl_off
    # ----------
    #proto = {
    #        "DAC": {
    #            "pclkHighP": pu1,
    #            "pclkLowP": pl1,
    #            "sclkHighP": sh1,
    #            "sclkLowP": sl1,
    #            "rgHighP": rgh1,
    #            "rgLowP": rgl1,
    #        },
    #        "Bias": {
    #            "rdP": rd1,
    #            "odP": od1,
    #            "ogP": og1,
    #            "gdP": gd1,
    #        }
    #    }
    #for key in [ "DAC", "Bias" ]:
    #    proto[key].update(kwargs[key])
    return pu1,pl1,sh1,sl1,rgh1,rd1,od1,og1,gd1,

def full_persistence_run(sleeptime):
    print("Get outta there! Sleeping for "+str(sleeptime)+"s")
    time.sleep(sleeptime)
    eWarning("Starting new persistence run.")
    copy_file_to_imagedir(persistnececfgfile)
    copy_file_to_imagedir("/home/ccd/ucd-scripts/persistence/persistencerun.py")
    copy_file_to_imagedir("/home/ccd/ccs/etc/FocalPlane_ucd_Rafts.properties")
    copy_file_to_imagedir("/home/ccd/ccs/etc/FocalPlane_ucd_RaftsLimits.properties")
    i=1
    length=str(len(sequencerlist))
    for sequencerfilename in sequencerlist:
        nowdate=time.strftime("%Y%m%d")
        nowimagedir='/mnt/10TBHDD/data/'+nowdate
        try:
            power_CCD("on")
            take_data(sequencercfgfile)
            sequencer="FP_E2V_2s_ir2_"+sequencerfilename+".seq"
            seq=get_sequencer_from_header(nowimagedir)
            if sequencer!=seq:
                eWarning("The sequencer file is not correct in the header for "+str(sequencerfilename))
                time.sleep(2)
                raise Exception("Sequencer file not correct in the header!")
            move_files_to_new_directory(nowimagedir,sequencerfilename)
            power_CCD("off")
            eWarning("Finished sequencer run for "+str(sequencerfilename)+" "+str(i)+"/"+length)
            i+=1
            time.sleep(10)
        except:
            eWarning("Error in sequencer run on "+str(sequencerfilename))
            raise Exception("Error in sequencer run on "+str(sequencerfilename))   
    
####### MAIN PROGRAM #########

