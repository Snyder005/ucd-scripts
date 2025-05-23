#!/usr/bin/env python
#Author: Craig Lage, Daniel Polin
#Date: 20220420
# This code sends an E-Mail in the event of a failure

import sys, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#************************************* SUBROUTINES ***********************************************
lsst_addr="ucdavislsst@gmail.com"

def Send_Warning(message_subject, message_text):
    to_list=[lsst_addr,'polin@ucdavis.edu','aksnyder@ucdavis.edu','nsbach@ucdavis.edu'] #,
    outside_list = []
    # First send waring for all ucdavis addrs to default server at solid.physics.ucdavis.edu
    for to_addr in to_list:
        try:
            to_addr.index("ucdavis.edu")
        except ValueError:
            outside_list.append(to_addr)
    for to_addr in outside_list:
        to_list.remove(to_addr)
    if len(to_list) > 0:
        msg = MIMEMultipart()
        msg['From']=lsst_addr
        msg['Subject']=message_subject
        msg.attach(MIMEText(message_text,'plain'))
        msg['To']=','.join(to_list)
        text=msg.as_string()
        server=smtplib.SMTP('ucdavis-edu.mail.protection.outlook.com', 25)
        server.starttls()
        server.sendmail(lsst_addr, to_list, text)
        server.quit()
    # The to_list should be cleansed of any ucdavis.edu clients at this point
    server=smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(lsst_addr,'Nerdlet1414')
    msg = MIMEMultipart()
    msg['From']=lsst_addr
    msg['Subject']=message_subject
    msg.attach(MIMEText(message_text,'plain'))
    msg['To']=','.join(outside_list)
    text=msg.as_string()
    server.sendmail(lsst_addr, outside_list, text)
    server.quit()
    return 
