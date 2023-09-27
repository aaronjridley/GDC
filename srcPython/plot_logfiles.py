#!/usr/bin/env python

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import re
import argparse
import datetime as dt

from logfile import *

# ----------------------------------------------------------------------
# Function to parse input arguments
# ----------------------------------------------------------------------

def get_args_timeline():

    parser = argparse.ArgumentParser(description =
                                     'Post process and move model results')
    parser.add_argument('-plotfile',
                        help = 'output file for plot',
                        default = 'timeline.png')

    parser.add_argument('-vars',
                        help = 'var(s) to plot (e.g. -vars 0 or -vars 0 1 2',
                        default = [0], nargs = '+', type = int)
    
    parser.add_argument('filelist', nargs='+', \
                        help = 'list files to use for generating plots')
    
    args = parser.parse_args()

    return args

# ----------------------------------------------------------------------
# match filename with colors and linestyles
# ----------------------------------------------------------------------

def assign_var_to_color(var):

    color = 'black'
    line = 'solid'
    label = file
    
    m = re.match('.*GOCE.*', var)
    if m:
        color = 'black'
        line = 'solid'
        label = 'GOCE'

    m = re.match('.*GITM.*', var)
    if m:
        color = 'blue'
        line = 'solid'
        label = 'GITM'
        
    m = re.match('.*Smooth.*', var)
    if m:
        line = 'dashed'
        label = label + ' (smoothed)'
        
    return color, line, label

# ----------------------------------------------------------------------
# match filename with colors and linestyles
# ----------------------------------------------------------------------

def assign_file_to_color(file):

    color = 'black'
    line = 'solid'
    label = file
    
    m = re.match(r'gdcA', file)
    if m:
        color = 'red'
        label = 'GDC A'

    m = re.match(r'gdcB', file)
    if m:
        color = 'blue'
        label = 'GDC B'

    m = re.match(r'gdcC', file)
    if m:
        color = 'cyan'
        label = 'GDC C'

    m = re.match(r'gdcD', file)
    if m:
        color = 'orange'
        label = 'GDC D'

    m = re.match(r'gdcE', file)
    if m:
        color = 'grey'
        label = 'GDC E'

    m = re.match(r'gdcF', file)
    if m:
        color = 'black'
        label = 'GDC F'

    m = re.match('.*lt005', file)
    if m:
        line = 'dashed'
        label = label + ' (LT 0.5)'

    m = re.match(r'base', file)
    if m:
        color = 'black'
        line = 'solid'
        label = 'Idealized Model'

    m = re.match(r'fre', file)
    if m:
        color = 'grey'
        line = 'solid'
        label = 'FRE Model'

    m = re.match(r'ovation', file)
    if m:
        color = 'blue'
        line = 'dashed'
        label = 'Ovation'

    m = re.match(r'avee_050', file)
    if m:
        color = 'darkblue'
        line = 'dashed'
    m = re.match(r'avee_075', file)
    if m:
        color = 'blue'
        line = 'dashed'

    m = re.match(r'avee_150', file)
    if m:
        color = 'firebrick'
        line = 'dashdot'
        
    m = re.match(r'avee_200', file)
    if m:
        color = 'red'
        line = 'dashdot'
        
    m = re.match(r'fta', file)
    if m:
        color = 'forestgreen'
        line = 'dashed'
        label = 'FTA Model'

    m = re.match(r'ae', file)
    if m:
        color = 'plum'
        line = 'dashed'
        label = 'FRE, AE Power'
        
    m = re.match(r'ions', file)
    if m:
        color = 'plum'
        line = 'dashdot'
        label = 'Ions'
        
    m = re.match(r'.*no', file)
    if m:
        color = 'cyan'
        label = 'NO Cooling'
    m = re.match(r'.*ch', file)
    if m:
        color = 'red'
        label = 'Chemical Heating'
    m = re.match(r'.*ht', file)
    if m:
        color = 'blue'
        label = 'Heat Transfer'
    m = re.match(r'.*jh', file)
    if m:
        label = 'Joule Heating'
        
    return color, line, label

# Needed to run main script as the default executable from the command line
if __name__ == '__main__':

    args = get_args_timeline()

    iVar = args.vars[0]

    nFiles = len(args.filelist)
    nVars = len(args.vars)
    
    fig = plt.figure(figsize = (10,10))
    ax = fig.add_subplot(111)
    
    for file in args.filelist:
        print("Reading file : ",file)
        data = read_timeline_file(file)

        for iVar in args.vars:
            print('Plotting Variable : ', data["vars"][iVar])
            
            label = fix_vars(data["vars"][iVar])
            color = 'black'
            line = '-'

            if (nFiles > 1):
                color,line,label = assign_file_to_color(file)
            if (nVars > 1):
                color,line,label = assign_var_to_color(data['vars'][iVar])
                
            ax.plot(data["times"], data["values"][iVar], label = label,
                    color = color, linestyle = line, linewidth = 2.0)

    iVar = args.vars[0]
    ytitle = data["integral"] + " of " + \
        data["vars"][iVar]
    if (data["alt"] > 0.0):
        ytitle += " at " + \
            "%5.1f" % data["alt"] + " km Alt"
    ax.set_ylabel(ytitle)

    ax.legend()
    plotfile = args.plotfile
    print('writing : ',plotfile)    
    fig.savefig(plotfile)
    plt.close()
