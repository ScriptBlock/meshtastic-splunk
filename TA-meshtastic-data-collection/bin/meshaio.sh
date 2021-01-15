#!/bin/sh
export PYTHONPATH=/usr/local/lib/python3.6/site-packages:/usr/local/lib64/python3.6/site-packages

pid=`ps -e -o pid,cmd | grep meshaio.py | grep $1 | awk '{print $1}'`

if [ ! $pid ]; then
   rm -f $SPLUNK_HOME/etc/apps/TA-meshtastic-data-collection/bin/data/*-$1.log
   python3 $SPLUNK_HOME/etc/apps/TA-meshtastic-data-collection/bin/meshaio.py $1 $2 $3 $4 $5 $6
fi
