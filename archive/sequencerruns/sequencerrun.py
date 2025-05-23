import numpy as np
import time,subprocess,datetime,sys,glob,random
from astropy.io import fits
sys.path.append('/home/ccd/ucd-scripts/python')
import Email_Warning

#sequencerlist=["v29_overlap532","v29_overlap226","v29_overlap452","v29_overlap1190","v29_overlap660","v29_overlap2260","v29_overlap1720","v29_overlap930","v26_overlap1330","v26_nonoverlapping","v26"] 

sequencerlist=["v29_overlap532","v29_overlap226","v29_overlap452","v29_overlap1190","v29_overlap660","v29_overlap2260","v29_overlap1720","v29_overlap930","v26_overlap1330","v26_nonoverlapping","v26"] 

sequencercfgfile="overlap_scanmode.cfg"
sleeptime=30

date=time.strftime("%Y%m%d")
imagedir='/mnt/10TBHDD/data/'+date


def set_alarm(state):
    if state=="off" or state=="OFF" or state=="Off":
        subprocess.run('python /home/ccd/security/disarm.py',check=True, shell=True)
    elif state=="on" or state=="ON" or state=="On":
        subprocess.run('python /home/ccd/security/arm.py',check=True, shell=True)

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
    
def move_files_to_new_directory(directory,sequencerfilename):
    subprocess.run('mkdir '+imagedir+"/"+sequencerfilename,check=True, shell=True)
    subprocess.run('mv '+directory+"/TS_C* "+imagedir+"/"+sequencerfilename,check=True, shell=True)
    
def check_sequencer(location):
    output=subprocess.check_output(["/home/ccd/ccs/bin/ccs-shell <ccssequencercheck.txt"],shell=True)
    output=str(output)
    output=output.split("\\n")
    output=output[-11]
    output=output.split(location+"_")
    #ITLseqreturn=output[2][:-6]
    e2vseqreturn=output[1].split(".seq")
    e2vseqreturn=e2vseqreturn[0]
    return e2vseqreturn#,ITLseqreturn
    
def change_sequencer(sequencer,location):
    text='''set target ucd-fp

sequencerConfig change sequencer [E2V:FP_E2V_2s_'''+location+'''_'''+sequencer+'''.seq,ITL:FP_ITL_2s_'''+location+'''_'''+sequencer+'''.seq]

printConfigurationParameters Sequencer'''
    file = open("ccssequencercommands.txt", 'w')
    file.write(text)       
    file.close()
    
    output=subprocess.check_output(["/home/ccd/ccs/bin/ccs-shell <ccssequencercommands.txt"],shell=True)
    return output
    
def eWarning(warning):
    try:
        subject = "Run Update" + time.asctime()
        w_file = open('/home/ccd/ucd-scripts/python/send_warning', 'w')
        w_file.write(subject + ":: ")
        w_file.write(warning)
        w_file.close()
        Email_Warning.Send_Warning(subject, warning)
    except:
        pass
        
def get_sequencer_from_header(directory):
    fitsfiles=np.array(glob.glob(directory+'/*.fits'))
    headerseq=fits.getheader(fitsfiles[0])["SEQFILE"]
    return headerseq

def full_sequencer_run(sleeptime):
    print("Get outta there! Sleeping for "+str(sleeptime)+"s")
    time.sleep(sleeptime)
    eWarning("Starting new sequencer run.")
    try:
        subprocess.run('mkdir '+imagedir,check=True, shell=True)
    except:
        print(date+" directory already exists")
    copy_file_to_imagedir(sequencercfgfile)
    copy_file_to_imagedir("/home/ccd/ucd-scripts/sequencerruns/sequencerrun.py")
    
    i=1
    length=str(len(sequencerlist))
    set_alarm("on")
    for sequencerfilename in sequencerlist:
        nowdate=time.strftime("%Y%m%d")
        sequencerstart=sequencerfilename[:3]
        if sequencerstart=="v29" or sequencerstart=="v30":
            location="l3cp"
        elif sequencerstart=="v26" or sequencerstart=="v27":
            location="ir2"
        else:
            eWarning("Sequencer not an accepted version (ie. v26,v29)")
            raise Exception("Sequencer not an accepted version (ie. v26,v29)")
        nowimagedir='/mnt/10TBHDD/data/'+nowdate
        check="no"
        attempt=0
        while check!=sequencerfilename and attempt<5:
            try:
                change_sequencer(sequencerfilename,location)
                time.sleep(10)
                check=check_sequencer(location)
                attempt+=1
            except:
                time.sleep(10)
        if not check==sequencerfilename:
            eWarning("The sequencer failed to update to "+str(sequencerfilename))
            raise Exception("The sequencer failed to update to "+str(sequencerfilename))
        try:
            power_CCD("on")
            take_data(sequencercfgfile)
            sequencer="FP_E2V_2s_"+location+"_"+sequencerfilename+".seq"
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
            power_light("off")
            print("Error in sequencer run on "+str(sequencerfilename))   
    set_alarm("off")

if __name__ == '__main__':
    
    full_sequencer_run(sleeptime)

