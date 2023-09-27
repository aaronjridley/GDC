#!/usr/bin/env python

from glob import glob
from gitm_routines import *
import datetime as dt
import re
import sys
import argparse
import os

# ----------------------------------------------------------------------
# Figure out arguments
# ----------------------------------------------------------------------

def get_args():

    r""" Parse the arguements and set to a dictionary

    Parameters
    ----------

    Returns
    -------
    args: A dictionary containing information about arguements, such
          as filelist, IsGitm, var (number), cut, diff (difference with
          other plots), movie, ext (for movie), rate (framerate for movie),
          tec, winds (plot with winds), alt (to plot), lat (to plot),
          lon (to plot), IsLog, and help (display help)
    """

    parser = argparse.ArgumentParser(
        description = 'Extract data from GITM files along satellite path')

    parser.add_argument('-vars', metavar = 'vars',  default ='3,4,15', \
                        help = 'comma-separated list of variables to extract')

    parser.add_argument('-pre', metavar = 'pre',  default ='3DALL', \
                        help = 'prefix for GITM files to look for')

    parser.add_argument('-outfile', metavar = 'outfile',  \
                        default ='none', \
                        help = 'output filename')

    parser.add_argument('satfiles', nargs='+', \
                        help = 'list files to use for generating plots')
    
    args = parser.parse_args()

    return args


# ----------------------------------------------------------------------
# read satellite file (logfile - style)
# ----------------------------------------------------------------------

def read_satellite_file(filein):

    fpin = open(filein, 'r')

    useMS = False

    # Read header:
    for line in fpin:

        m = re.match(r'milli',line.lower())
        if m:
            useMS = True
        
        m = re.match(r'#START',line)
        if m:
            break
    
    data = {
        'times' : [],
        'lons' : [],
        'lats' : [],
        'alts' : [],
        'file' : filein}

    iData_ = 6
    if (useMS):
        iData_ += 1
    
    # Read main data
    for line in fpin:
        cols = line.split()

        yy = int(cols[0])
        mm = int(cols[1])
        dd = int(cols[2])
        hh = int(cols[3])
        mn = int(cols[4])
        ss = int(cols[5])
        if (useMS):
            ms = int(cols[6])
        else:
            ms = 0
        data["times"].append(dt.datetime(yy,mm,dd,hh,mn,ss,ms*1000))
        data["lons"].append(float(cols[iData_]))
        data["lats"].append(float(cols[iData_+1]))
        data["alts"].append(float(cols[iData_+2]))
        
    fpin.close()
    
    return data

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# Main Code!
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

rtod = 180.0/np.pi

args = get_args()

vars = np.array(args.vars.split(','))
vars = vars.astype(int)

gitmfiles = sorted(glob(args.pre + '*bin'))
headers = read_gitm_headers(args.pre)

nGitmFiles = len(headers["time"])

# get lons, lats, alts:
lla = [0,1,2]
data = read_gitm_one_file(headers["filename"][0], lla)
Alts = data[2][0][0]/1000.0;
Lons = data[0][:,0,0]*rtod;
Lats = data[1][0,:,0]*rtod;
[nLons, nLats, nAlts] = data[0].shape

dLon = Lons[1]-Lons[0]
dLat = Lats[1]-Lats[0]

nVars = len(vars)
AfterVals = np.zeros(nVars)
BeforeVals = np.zeros(nVars)

for file in args.satfiles:

    print('-> Reading Satellite file : ', file)
    data = read_satellite_file(file)

    if (len(args.outfile) <= 4):
        iP = file.find('.txt')
        if (iP < 0):
            iP = file.find('.dat')
        if (iP > 0):
            outfile = file[0:iP] + '_gitm.txt'
        else:
            outfile = file + '_gitm.txt'
    else:
        outfile = args.outfile
        
    print('-> Writing Extracted file : ', outfile)
    fpout = open(outfile, 'w')

    fpout.write('\n')
    fpout.write('Satellite file: ' + file + '\n')
    fpout.write('Using gitm_extract_sat_ssv.py\n')
    fpout.write(dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S\n"))
    fpout.write("\n")
    fpout.write("#DIRECTORY\n")
    fpout.write(os.getcwd() + "\n")
    fpout.write("\n")
    fpout.write('#VARIABLES\n')
    fpout.write('year\n')
    fpout.write('month\n')
    fpout.write('day\n')
    fpout.write('hour\n')
    fpout.write('minute\n')
    fpout.write('second\n')
    fpout.write('milli-sec\n')
    fpout.write('longitude\n')
    fpout.write('latitude\n')
    fpout.write('altitude\n')
    for v in vars:
        fpout.write(headers['vars'][v]+'\n')
    fpout.write('\n')
    fpout.write('#START\n')
            
    iBefore0 = -1
    iAfter0 = -1
    # here we just assume that we will start with the first set of files.
    # this shouldn't matter...
    iBefore = 0
    iAfter = 1

    for i, time in enumerate(data["times"]):

        while (time > headers["time"][iAfter]):
            iAfter = iAfter+1
            if (iAfter >= nGitmFiles-1):
                break
        
        if (iAfter == nGitmFiles):
            break

        iBefore = iAfter-1

        if (iBefore != iBefore0):
            file = headers["filename"][iBefore]
            BeforeData = read_gitm_one_file(file, vars)
        if (iAfter != iAfter0):
            file = headers["filename"][iAfter]
            AfterData = read_gitm_one_file(file, vars)

        if (time >= headers["time"][iBefore]):
            
            dt = (headers["time"][iAfter] - \
                  headers["time"][iBefore]).total_seconds()
            xt = (time - headers["time"][iBefore]).total_seconds() / dt

            lon = data["lons"][i]
            lat = data["lats"][i]
            alt = data["alts"][i]
        
            xLon = (lon-Lons[0])/dLon
            iLon = int(xLon)
            xLon = xLon - iLon
        
            yLat = (lat-Lats[0])/dLat
            jLat = int(yLat)
            yLat = yLat - jLat

            kAlt = 0
            zAlt = 0.0
            if ((alt > Alts[0]) and (nAlts > 1)):
                if (alt > Alts[nAlts-1]):
                    # above domain:
                    kAlt = nAlts-2
                    zAlt = 1.0
                else:
                    while (Alts[kAlt] < alt):
                        kAlt = kAlt + 1
                    kAlt = kAlt - 1
                    zAlt = (alt - Alts[kAlt]) / (Alts[kAlt+1] - Alts[kAlt])
                kAltp1 = kAlt + 1
            else:
                kAltp1 = kAlt
                
            for i, v in enumerate(vars):
                BeforeVals[i] = \
                    (1-xLon)*(1-yLat)*(1-zAlt)*BeforeData[v][iLon][jLat][kAlt]+\
                    (  xLon)*(1-yLat)*(1-zAlt)*BeforeData[v][iLon+1][jLat][kAlt]+\
                    (1-xLon)*(  yLat)*(1-zAlt)*BeforeData[v][iLon][jLat+1][kAlt]+\
                    (  xLon)*(  yLat)*(1-zAlt)*BeforeData[v][iLon+1][jLat+1][kAlt]+\
                    (1-xLon)*(1-yLat)*(  zAlt)*BeforeData[v][iLon][jLat][kAltp1]+\
                    (  xLon)*(1-yLat)*(  zAlt)*BeforeData[v][iLon+1][jLat][kAltp1]+\
                    (1-xLon)*(  yLat)*(  zAlt)*BeforeData[v][iLon][jLat+1][kAltp1]+\
                    (  xLon)*(  yLat)*(  zAlt)*BeforeData[v][iLon+1][jLat+1][kAltp1]
                AfterVals[i] = \
                    (1-xLon)*(1-yLat)*(1-zAlt)*AfterData[v][iLon][jLat][kAlt]+\
                    (  xLon)*(1-yLat)*(1-zAlt)*AfterData[v][iLon+1][jLat][kAlt]+\
                    (1-xLon)*(  yLat)*(1-zAlt)*AfterData[v][iLon][jLat+1][kAlt]+\
                    (  xLon)*(  yLat)*(1-zAlt)*AfterData[v][iLon+1][jLat+1][kAlt]+\
                    (1-xLon)*(1-yLat)*(  zAlt)*AfterData[v][iLon][jLat][kAltp1]+\
                    (  xLon)*(1-yLat)*(  zAlt)*AfterData[v][iLon+1][jLat][kAltp1]+\
                    (1-xLon)*(  yLat)*(  zAlt)*AfterData[v][iLon][jLat+1][kAltp1]+\
                    (  xLon)*(  yLat)*(  zAlt)*AfterData[v][iLon+1][jLat+1][kAltp1]

            date = time.strftime('%Y %m %d %H %M %S 00 ')
            pos = '%7.2f %7.2f %8.2f' % (lon, lat, alt)
            vals = ''
            for i, v in enumerate(vars):
                v = (1-xt) * BeforeVals[i] + xt * AfterVals[i]
                vals = vals + '  %e' % v
            fpout.write(date+pos+vals+'\n')

        iBefore0 = iBefore
        iAfter0 = iAfter
