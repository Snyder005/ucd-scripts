#!/bin/bash
cd /home/ccd/ucd-scripts/lib/
python3 Purge_Datastore.py 1>> /mnt/10TBHDD/data/logs/DataStorePurge.log 2>> /mnt/10TBHDD/data/logs/DataStorePurge.log&

