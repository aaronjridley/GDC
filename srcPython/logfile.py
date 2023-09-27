#!/usr/bin/env python

import numpy as np
import re
import datetime as dt


# ----------------------------------------------------------------------
# GITM variables have weird characters, get rid of them!
# ----------------------------------------------------------------------

def fix_var(v):
    nv = re.sub('!U', '', v)
    nv = re.sub('!N', '', nv)
    nv = re.sub('!D', '', nv)
    return nv

# This fixes an array of variables or a single variable:

def fix_vars(vars):
    print('vars : ', vars)
    if (np.isscalar(vars)):
        newvars = fix_var(vars)
    else:
        newvars = []
        for v in vars:
            nv = re.sub('!U', '', v)
            nv = re.sub('!N', '', nv)
            nv = re.sub('!D', '', nv)
            newvars.append(nv)
    return newvars

# ----------------------------------------------------------------------
# Read logfile, which has a specific format
# ----------------------------------------------------------------------

def read_timeline_file(file):

    data = {"times" : [],
            'vars': [],
            "integral" : 'values',
            "file": file}

    fpin = open(file, 'r')

    lines = fpin.readlines()

    iStart = 0
    iEnd = len(lines)
    iLine = iStart

    data['alt'] = 0.0

    while (iLine < iEnd):
        line = lines[iLine]

        m = re.match(r'#VAR',line)
        if m:
            # skip year, month, day, hour, minute, second:
            print(' --> Variables in File :')
            if (lines[iLine+1].strip().lower() == 'year'):

                m = re.match(r'milli',lines[iLine+7])
                if m:
                    useMS = True
                    offset = 7
                else:
                    useMS = False
                    offset = 6
                iLine += offset + 1
            else:
                iLine += 1
            iVar_ = 0
            while (len(lines[iLine].strip()) > 1):
                data["vars"].append(lines[iLine].strip())
                print('    --> %d:' % iVar_, data["vars"][-1])
                iLine += 1
                iVar_ += 1
            data['var'] = data["vars"][0]

        m = re.match(r'#INTEGRAL',line)
        if m:
            iLine += 1
            data["integral"] = lines[iLine].strip()

        m = re.match(r'#ALTITUDE',line)
        if m:
            iLine += 1
            data["alt"] = float(lines[iLine].strip())

        m = re.match(r'#DIRECTORY',line)
        if m:
            iLine += 1
            data["dir"] = lines[iLine].strip()

        m = re.match(r'#START',line)
        if m:
            iStart = iLine + 1
            break

        iLine += 1

    nVars = len(data['vars'])
    nTimes = iEnd - iStart
    allValues = np.zeros([nVars, nTimes])
    for i in range(iStart, iEnd):
        aline = lines[i].split()
        if (len(aline) > offset):
            year = int(aline[0])
            month = int(aline[1])
            day = int(aline[2])
            hour = int(aline[3])
            minute = int(aline[4])
            second = int(aline[5])
            if (useMS):
                ms = int(aline[6])
            else:
                ms = 0
            t = dt.datetime(year, month, day, hour, minute, second, ms)
        
            data["times"].append(t)
            for iVar in range(nVars):
                allValues[iVar, i - iStart] = float(aline[offset + iVar])

    data['values'] = allValues
            
    return data

