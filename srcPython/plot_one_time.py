#!/usr/bin/env python

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap
from pylab import cm

import numpy as np
import datetime as dt
import re
from glob import glob

import argparse

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


#-----------------------------------------------------------------------------
# parse arguments
#-----------------------------------------------------------------------------

def parse_args_gdc():

    parser = argparse.ArgumentParser(description = \
                                     'Read and Plot GDC Ephemerides')
    
    parser.add_argument('-start', \
                        help = 'start date as YYYYMMDD[.HHMM]')
    
    parser.add_argument('-skip', \
                        help = 'interval (in days) between plots', \
                        default = 1, type = int)
    
    parser.add_argument('-days', \
                        help = 'number of days to plot', \
                        default = 1, type = int)

    args = parser.parse_args()

    return args

    

#-----------------------------------------------------------------------------
# get the first time in the GDC file
#-----------------------------------------------------------------------------

def get_starttime_gdc_ephemeris_file(filein):

    fpin = open(filein, 'r')

    # Read header:
    for line in fpin:

        m = re.match(r'-----------',line)
        if m:
            break

    # Read main data
    line = fpin.readline()
    fpin.close()
    cols = line.split()

    day = int(cols[0])
    mon = mStrToNum[cols[1]]
    year = int(cols[2])

    t = cols[3].split(':')
    hour = int(t[0])
    min = int(t[1])
    sec = int(float(t[2]))
    time = dt.datetime(year, mon, day, hour, min, sec)

    return time
    
        
#-----------------------------------------------------------------------------
# get the last time in the GDC file
#-----------------------------------------------------------------------------

def get_endtime_gdc_ephemeris_file(filein):

    fpin = open(filein, 'r')
    lines = fpin.readlines()
    fpin.close()
    line = lines[-1]

    cols = line.split()

    day = int(cols[0])
    mon = mStrToNum[cols[1]]
    year = int(cols[2])

    t = cols[3].split(':')
    hour = int(t[0])
    min = int(t[1])
    sec = int(float(t[2]))
    time = dt.datetime(year, mon, day, hour, min, sec)

    return time
    
        
#-----------------------------------------------------------------------------
# read in NASA file
#-----------------------------------------------------------------------------

def read_whole_ephemeris_file(filein):

    fpin = open(filein, 'r')
    lines = fpin.readlines()

    # Read header:
    iLineStart = 0
    for line in lines:

        m = re.match(r'-----------',line)
        iLineStart = iLineStart + 1
        if m:
            break

    nLines = len(lines)

    data = {
        'time' : [],
        'lons' : [],
        'lats' : [],
        'alts' : [],
        'file' : filein}

    for iLine in np.arange(iLineStart, nLines):
        line = lines[iLine]
        cols = line.split()

        day = int(cols[0])
        mon = mStrToNum[cols[1]]
        year = int(cols[2])

        # figure out time:
        t = cols[3].split(':')
        hour = int(t[0])
        min = int(t[1])
        sec = int(float(t[2]))
        data['time'].append(dt.datetime(year, mon, day, hour, min, sec))
        data['lats'].append(float(cols[10]))
        data['lons'].append(float(cols[11]))
        data['alts'].append(float(cols[12]))

    return data


#-----------------------------------------------------------------------------
# read in NASA file
#-----------------------------------------------------------------------------

def read_gdc_ephemeris_file(filein, MissionTime, hours, equator = False):

    fpin = open(filein, 'r')

    # Read header:
    for line in fpin:

        m = re.match(r'-----------',line)
        if m:
            break
    
    data = {
        'times' : [],
        'realTime' : [],
        'lons' : [],
        'lats' : [],
        'alts' : [],
        'file' : filein,
        'MissionTime' : MissionTime}

    MissionTimeEnd = MissionTime + dt.timedelta(hours = hours)
    if (equator):
        lastLat = -91.0
    
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
            lat = float(cols[10])
            if (equator):
                MissionTime = time
                MissionTimeEnd = MissionTime + dt.timedelta(hours = hours)
                #print(lastLat, lat, MissionTime)
                if ((lastLat < 0.0) and (lat >= 0.0)):
                    equator = False
                    data['lats'].append(lat)
                    data['lons'].append(float(cols[11]))
                    data['alts'].append(float(cols[12]))
                    data['times'].append((time - MissionTime).seconds)
                    data['realTime'].append(time)
                else:
                    lastLat = float(cols[10])
            else:
                data['lats'].append(lat)
                data['lons'].append(float(cols[11]))
                data['alts'].append(float(cols[12]))
                data['times'].append((time - MissionTime).seconds)
                data['realTime'].append(time)
        else:
            lastLat = float(cols[10])
            
        if (time > MissionTimeEnd):
            break

    fpin.close()
    
    return data


#-----------------------------------------------------------------------------
# plot out all GDC satellites for one time
#-----------------------------------------------------------------------------

def plot_gdc_sats_one_time(filelist, time, timeRange = 60):

    alldata = []
    hours = timeRange / 3600.0

    equator = True
    isFirst = True
    for filein in filelist:
    
        data = read_gdc_ephemeris_file(filein, time, hours, equator = equator)
        if (isFirst):
            equator = False
            time = data['realTime'][0]
            isFirst = False
        #print(data)
        alldata.append(data)
    
    return alldata

def convert_sDate_to_datetime(sDate):
    
    sDate = args.sDate

    ye = sDate[0:4]
    mo = sDate[4:6]
    da = sDate[6:8]

    if (len(sDate) >= 11):
        hr = sDate[9:11]
        if (len(sDate) >= 13):
            mi = sDate[11:13]
        else:
            mi = '00'
    else:
        hr = '00'
        mi = '00'

    dDate = datetime(int(ye), int(mo), int(da), int(hr), int(mi), 0)

    return dDate
    

if __name__ == '__main__':

    args = parse_args_gdc()

    filelist = sorted(glob("GDC*.txt"))
    if (args.start):
        dayMin = convert_sDate_to_datetime(sDate)
    else:
        dayMin = get_starttime_gdc_ephemeris_file(filelist[0])

    if (args.days < 1):
        dayMax = get_endtime_gdc_ephemeris_file(filelist[0])
        days = int((dayMax-dayMin).total_seconds()/86400)
        print(dayMin)
        print(dayMax)
        print('Setting days to: ',days)
    else:
        days = args.days
        dayMax = dayMin + dt.timedelta(days = days)
        
    dDay = args.skip

    filelist = sorted(glob("GDC*.txt"))

    alldata = []
    for file in filelist:
        print('Reading entire file : ', file)
        allSatLocs.append(read_whole_ephemeris_file(file))
        
    exit()

    # phase 1 starts: 31 Jul 2028
    #         ends: 6 Nov 2028
    # phase 3 starts: 20 Aug 2029
    #         ends: 17 May 2030

    span = days

    cmap = cm.viridis

    iStart = 0
    for day in range(0, span+1, dDay):
        
        fig = plt.figure(figsize = (10,7))
        ax=fig.add_axes([0.1,0.1,0.8,0.8])
        isFirst = True
        
        MissionTime = dayMin + dt.timedelta(days = day)
        timeRange = 120.0

        ### Use the allSatLocs variable instead of reading in the files
        
        alldata = plot_gdc_sats_one_time(filelist, MissionTime, timeRange)
        
        for data in alldata:

            if (isFirst):
                # center the map on the first satellite:
                cLon = data['lons'][0]
                rLon = cLon + 180.0
                lLon = cLon - 180.0
    
                m = Basemap(projection='merc', \
                            rsphere=(6378137.00,6356752.3142),\
                            llcrnrlon=lLon,llcrnrlat=-81., \
                            resolution='l', lon_0 = cLon, \
                            urcrnrlon=rLon,urcrnrlat=81.)

                m.drawcoastlines()
                #m.fillcontinents()
                # draw parallels
                m.drawparallels(np.arange(-100,100,20),labels=[1,1,0,1])
                # draw meridians
                m.drawmeridians(np.arange(-180,180,45),labels=[1,1,0,1])

                title = MissionTime.strftime('%d %B, %Y')
                plt.title(title)

                isFirst = False
            
            color = np.zeros(len(data['lons'])) + day
            x, y = m(data['lons'], data['lats'])
            m.scatter(x, y, c = color, s = 10, \
                      vmin = 0, vmax = span, cmap = cmap)
            m.scatter(x[-1], y[-1], c = day, s = 100, cmap = cmap, \
                      vmin = 0, vmax = span)

        
        plotfile = MissionTime.strftime('gdc_ephemeris_%y%m%d.png')
        print(plotfile)
        fig.savefig(plotfile)
        plt.close()


    
