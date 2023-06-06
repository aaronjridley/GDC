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

#-----------------------------------------------------------------------------
# read in NASA file
#-----------------------------------------------------------------------------

def read_gdc_ephemeris_file(filein, MissionTime, hours, equator = False):

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
        print(data)
        alldata.append(data)
    
    return alldata

if __name__ == '__main__':

    filelist = sorted(glob("GDC*.txt"))

    # phase 1 starts: 31 Jul 2028
    #         ends: 6 Nov 2028
    # phase 3 starts: 20 Aug 2029
    #         ends: 17 May 2030

    fig = plt.figure(figsize = (10,7))
    ax=fig.add_axes([0.1,0.1,0.8,0.8])

    dayMin = dt.datetime(2029, 9, 1, 0, 0, 0)
    dayMax = dt.datetime(2029, 9, 5, 0, 0, 0)
    dDay = 2
    span = int((dayMax - dayMin).days)

    cmap = cm.viridis
    isFirst = True
    for day in range(0, span+1, dDay):
        MissionTime = dayMin + dt.timedelta(days = day)
        timeRange = 120.0
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

                isFirst = False
            
            color = np.zeros(len(data['lons'])) + day
            x, y = m(data['lons'], data['lats'])
            m.scatter(x, y, c = color, s = 10, \
                      vmin = 0, vmax = span, cmap = cmap)
            m.scatter(x[-1], y[-1], c = day, s = 100, cmap = cmap, \
                      vmin = 0, vmax = span)

        
    plotfile = 'test.png'
    fig.savefig(plotfile)
    plt.close()


    
