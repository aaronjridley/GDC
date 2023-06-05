#!/usr/bin/env python

import numpy as np
import datetime as dt
import re
import sys

#-----------------------------------------------------------------------------
# 
#-----------------------------------------------------------------------------

def get_args(argv):

    filelist = []
    outfile = 'gdc_'
    missionYear = 2029
    missionMon = 1
    missionDay = 1
    missionHour = 0
    missionMin = 0
    missionSec = 0

    actualYear = 2013
    actualMon = 3
    actualDay = 16
    actualHour = 0
    actualMin = 0
    actualSec = 0

    hours = 24

    help = 0
    
    for arg in argv:

        IsFound = 0

        if (not IsFound):

            m = re.match(r'-hours=(\d+)',arg)
            if m:
                hours = int(m.group(1))
                IsFound = 1

            m = re.match(r'-mission=(\d\d\d\d).(\d\d).(\d\d)',arg)
            if m:
                missionYear = int(m.group(1))
                missionMon = int(m.group(2))
                missionDay = int(m.group(3))
                IsFound = 1

            m = re.match(r'-mission=(\d\d\d\d).(\d\d).(\d\d).(\d\d)',arg)
            if m:
                missionYear = int(m.group(1))
                missionMon = int(m.group(2))
                missionDay = int(m.group(3))
                missionHour = int(m.group(4))
                IsFound = 1

            m = re.match(r'-mission=(\d\d\d\d).(\d\d).(\d\d).(\d\d).(\d\d)',arg)
            if m:
                missionYear = int(m.group(1))
                missionMon = int(m.group(2))
                missionDay = int(m.group(3))
                missionHour = int(m.group(4))
                missionMin = int(m.group(5))
                IsFound = 1

            m = re.match(r'-mission=(\d\d\d\d).(\d\d).(\d\d).(\d\d).(\d\d).(\d\d)',arg)
            if m:
                missionYear = int(m.group(1))
                missionMon = int(m.group(2))
                missionDay = int(m.group(3))
                missionHour = int(m.group(4))
                missionMin = int(m.group(5))
                missionSec = int(m.group(6))
                IsFound = 1

            m = re.match(r'-actual=(\d\d\d\d).(\d\d).(\d\d)',arg)
            if m:
                actualYear = int(m.group(1))
                actualMon = int(m.group(2))
                actualDay = int(m.group(3))
                IsFound = 1

            m = re.match(r'-actual=(\d\d\d\d).(\d\d).(\d\d).(\d\d)',arg)
            if m:
                actualYear = int(m.group(1))
                actualMon = int(m.group(2))
                actualDay = int(m.group(3))
                actualHour = int(m.group(4))
                IsFound = 1

            m = re.match(r'-actual=(\d\d\d\d).(\d\d).(\d\d).(\d\d).(\d\d)',arg)
            if m:
                actualYear = int(m.group(1))
                actualMon = int(m.group(2))
                actualDay = int(m.group(3))
                actualHour = int(m.group(4))
                actualMin = int(m.group(5))
                IsFound = 1

            m = re.match(r'-actual=(\d\d\d\d).(\d\d).(\d\d).(\d\d).(\d\d).(\d\d)',arg)
            if m:
                actualYear = int(m.group(1))
                actualMon = int(m.group(2))
                actualDay = int(m.group(3))
                actualHour = int(m.group(4))
                actualMin = int(m.group(5))
                actualSec = int(m.group(6))
                IsFound = 1

            m = re.match(r'-outfile=(.*)',arg)
            if m:
                outfile = m.group(1)
                IsFound = 1

            m = re.match(r'-help',arg)
            if m:
                help = 1
                IsFound = 1

            if IsFound==0 and not(arg==argv[0]):
                filelist.append(arg)


    MissionTime = dt.datetime(missionYear, missionMon, missionDay, \
                             missionHour, missionMin, missionSec)
    ActualTime = dt.datetime(actualYear, actualMon, actualDay, \
                             actualHour, actualMin, actualSec)
    
    args = {'filelist':filelist,
            'ActualTime': ActualTime,
            'MissionTime': MissionTime,
            'hours': hours,
            'help': help,
            'outfile': outfile}

    return args

#-----------------------------------------------------------------------------
# read in NASA file
#-----------------------------------------------------------------------------

def read_file(filein, MissionTime, hours):

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

#-----------------------------------------------------------------------------
# Write satellite file
#-----------------------------------------------------------------------------

def write_file(fileout, data, ActualTime):

    fpout = open(fileout, 'w')

    fpout.write('\n')
    fpout.write('Output from file: '+data['file']+'\n')
    fpout.write('Using parse_gdc.py\n')
    fpout.write('\n')
    fpout.write('Format:\n')
    fpout.write('year month day hour minute second milli-sec lon lat alt\n')
    fpout.write('\n')
    fpout.write('#START\n')

    lat0 = data['lats'][0]
    IsReported = 0
    for i,time in enumerate(data['times']):

        t = ActualTime + dt.timedelta(seconds = time)
        
        date = t.strftime('%Y %m %d %H %M %S 00 ')
        lon = (data['lons'][i] + 360.0) % 360.0
        lat = data['lats'][i]
        if ((lat >= 0) and (lat0 < 0) and (IsReported == 0)):
            ut = t.hour + t.minute/60.0 + t.second/3600.0
            LocalTime = (lon/15.0 + ut) % 24.0
            print('Local Time of Ascending Node :', LocalTime)
            IsReported = 1
        lat0 = lat
        pos = '%7.2f %7.2f %8.2f\n' % \
            (lon, data['lats'][i], data['alts'][i])
        fpout.write(date+pos)
    
    fpout.close()

    
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Main Code!
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

args = get_args(sys.argv)

if (args["help"]):

    print('Usage : ')
    print('parse_gdc.py -mission=year.month.day.[hh].[mm].[ss]')
    print('             -actual=[yyyy].[mm].[dd].[hh].[mm].[ss]')
    print('             -hours=hours of file to grab')
    print('             -outfile=output file)')
    print('             file[s] to read')
    exit()

for i,infile in enumerate(args['filelist']):

    print('Reading file : '+infile)
    data = read_file(infile, args['MissionTime'], args['hours'])

    if (len(args['filelist']) > 1):
        outfile = args['outfile']+'_%02d.txt' % (i+1)
    else:
        outfile = args['outfile']

    print('Writing file : '+outfile)
    write_file(outfile, data, args['ActualTime'])
