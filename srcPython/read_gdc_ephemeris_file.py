#!/usr/bin/env python

import numpy as np
import datetime as dt
import re

#-----------------------------------------------------------------------------
# read in NASA file
#-----------------------------------------------------------------------------

def read_gdc_ephemeris_file(filein, MissionTime, hours):

    mStrToNum = {"Jan": 1,
                 "Feb": 2,
                 "Mar": 3,
                 "Apr": 4,
                 "May": 5,
                 "Jun": 6,
                 "Jul": 7,
                 "Aug": 8,
                 "Sep": 9,
                 "Oct": 10,
                 "Nov": 11,
                 "Dec": 12}
    
    fpin = open(filein, 'r')

    # Read header:
    for line in fpin:

        m = re.match(r'-----------',line)
        if m:
            break
    
    data = {
        'times' : [],
        'lons' : [],
        'lats' : [],
        'alts' : [],
        'file' : filein,
        'MissionTime' : MissionTime}

    MissionTimeEnd = MissionTime + dt.timedelta(hours = hours)
    
    # Read main data
    for line in fpin:
        cols = line.split()

        day = int(cols[0])
        mon = mStrToNum[cols[1]]
        year = int(cols[2])

        # figure out time:
        t = cols[3].split(':')
        hour = int(t[0])
        min = int(t[1])
        sec = int(float(t[2]))
        time = dt.datetime(year, mon, day, hour, min, sec)

        if ((time >= MissionTime) & (time <= MissionTimeEnd)):
            data['lats'].append(float(cols[10]))
            data['lons'].append(float(cols[11]))
            data['alts'].append(float(cols[12]))
            data['times'].append((time - MissionTime).seconds)
            
        if (time > MissionTimeEnd):
            break

    fpin.close()
    
    return data

