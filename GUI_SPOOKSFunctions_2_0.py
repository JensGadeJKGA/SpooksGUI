
# -*- coding: utf-8 -*-
#"""
#Created on Sat Oct 24 11:45:53 2020

#@author: EMBT, JKGA
#"""




####### This script intends to calculate spookswat analyses from an excel input file
####### structured as SPOOKSINPUT.xlsx. 
## Vers 2.1
# Prepared: EMBT, 10.10.2023
# Checked: SEMS, CHHJ
## Vers 1.0
# Prepared: EMBT, 06.07.2020
# Checked: EMSS, 06.07.2020


### Imports
from SpooksHelperLib.Vequilibrium import verticalEquilibrium
from SpooksHelperLib.GenerateReport.generateReport import generateReport
from SpooksHelperLib.Export.export import export
from SpooksHelperLib.plot import plot
from SpooksHelperLib.SPWplugin import log_usage

import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os
import tkinter as tk
import tkinter.scrolledtext as tkst
import subprocess
import time

from datetime import datetime
from pathlib import Path
from tkinter import ttk
from tkinter import filedialog


################ Version ##################

Version = '3'

################ Input file ID ############




############### IMPORT SHEET PILE WALL PLUG IN ###################



################### FUNCTIONS ####################################
        

############### GUI Functions

def OpenSpooks(dev_mode = False, spoof_path = None):
    
    ################### OPEN WINSPOOKS ###################################
    ######### Check in WinSpooks is running - if not -> Run
    ######### (necessary for license check)

    try:
        res = subprocess.check_output(['tasklist'], text=True).splitlines()
    except Exception as e:
        print("Error checking tasklist:", e)
        return

    is_running = any('WinSpooks.exe' in line for line in res)

    if not is_running:
        # Determine the path (real or spoofed)
        if dev_mode:
            spooks_path = Path(spoof_path) if spoof_path else Path("C:/FakeProgramFiles/WinSpooks/WinSpooks.exe")
            print(f"Dev mode: Would launch {spooks_path}")
            return  # Skip launching in dev mode
        else:
            spooks_path = Path("C:/Program Files (x86)/WinSpooks/WinSpooks.exe")
            if spooks_path.exists():
                subprocess.Popen([str(spooks_path)])
                time.sleep(0.5)
            else:
                print(f"WinSpooks.exe not found at {spooks_path}")
    
    # Optional cleanup (not necessary in Python, but fine)
    res = None
    
    


################### 1. OPEN WINSPOOKS ###################################
######### Check in WinSpooks is running - if not -> Run
######### (necessary for license check)
######### Add dev_mode = True to launch the gui in developer mode (runs the gui without spooks)


OpenSpooks()
    

################# 2. STARTING UP GUI INTERFACE #######################




window = tk.Tk()
window.minsize(1300,600) ## Initial GUI size
window.title("WinSPOOKS Plug-in")

tab_parent = ttk.Notebook(window)  ## parent tab
tabcalc = ttk.Frame(tab_parent)    ## Calculation tab
tablog = ttk.Frame(tab_parent)     ## Log tab
tabvers = ttk.Frame(tab_parent)    ## Version tab
tab_parent.add(tabcalc, text="Calculations")
tab_parent.add(tablog, text = "Calculation log")
tab_parent.add(tabvers, text="Version")



######## Output file path
outputdir = None
OutputDirList = []

####### Excel input file path
filename = None
FilenameList = []


def FileDialog():
    
    filename = filedialog.askopenfilename(initialdir =  "/", title = "Select A File", filetype =
    (("excel","*.xlsx"),("all files","*.*")))
    FilenameList.append(filename)
    label_file.configure(text = filename)
    label_file.configure(foreground = 'green')
    stat.configure(text = "Input file loaded")
    button_calc.configure(stat = 'normal')
        
    if checkexp.get() == 1 and OutputDirList != [] and FilenameList != []:
        stat.configure(text = "Ready")
    if checkexp.get() == 0 and FilenameList != []:
        stat.configure(text = "Ready")


def OutputDialog():
    
    
    outputdir = filedialog.askdirectory()
    OutputDirList.append(os.path.abspath(outputdir))
    label_dir.configure(text = outputdir)
    label_dir.configure(foreground = 'green')
    
    if checkexp.get() == 1 and OutputDirList != [] and FilenameList != []:
        stat.configure(text = "Ready")

###### Configuration of GUI output browse button    
def Disable():
    if checkexp.get() == 1 or checkexp_ep.get() == 1 or checkreport.get() == 1:
        button_output.configure(stat = 'normal')
        label_dir.configure(foreground = 'black')
        label_outputdir.configure(foreground = 'black')
    else:
        button_output.configure(stat = 'disable')
        label_dir.configure(foreground = 'grey')
        label_outputdir.configure(foreground = 'grey')


## Calculate
def Calculate():
    
    log_usage()


    if checkexp.get() == 1 and OutputDirList == []:
        stat.configure(text = "Choose export directory")
        
        
    elif FilenameList != []:
        
        InputFile = FilenameList[-1]
                
        ## Update GUI
        stat.configure(text = "Calculating...")
        button_calc.configure(stat = 'disable')
        tabcalc.update_idletasks()
        
        ## Run SpooksFeeder
        print("Feeder")
        FeederOutput = verticalEquilibrium.SPOOKSFeeder(InputFile,calcno,pb,tabcalc,logtxt,tk)
        
        stat.configure(text = "Calculation completed")
        tabcalc.update_idletasks()
        
        
        ##### Generating reports
        if checkreport.get() == 1:
            
            
            generateReport.ReportsMerger(FeederOutput,OutputDirList,Version,stat,tabcalc,pb,calcno)
            
            stat.configure(text = "Reports generated")
            tabcalc.update_idletasks()
            
        
        ## Plot results
        if checkplot.get() == 1:
            
            stat.configure(text = "Plotting results...")
            tabcalc.update_idletasks()
            
            plot.PlotResults(FeederOutput)
            
        ## Export results
        if checkexp.get() == 1:
            
            stat.configure(text = "Exporting results...")
            tabcalc.update_idletasks()
            
            export.ExportResultsAsTxt(FeederOutput,OutputDirList)
            
        
        ## Export earth pressure results
        if checkexp_ep.get() == 1:
            
            stat.configure(text = "Exporting results...")
            tabcalc.update_idletasks()
            
            export.ExportEarthPressureResultsAsTxt(FeederOutput, OutputDirList)
            
        ## Enable calculation button at end of tasks
        stat.configure(text = "Tasks completed...")
        button_calc.configure(stat = 'normal')
        tabcalc.update_idletasks()

           

######################## GUI ELEMENTS ###############################
####################### Calculation tab #############################
        
### Logo and header
label_logo = ttk.Label(tabcalc, text = " COWI", font=("Century Schoolbook", 33), foreground = 'orange red')
label_logo.grid(column = 0, row = 0, sticky = 'SE')
label_header = ttk.Label(tabcalc, text = "WinSPOOKS Plug-in", font=("Calibri", 16))
label_header.grid(column = 2, row = 0, sticky = 'SW')
## empty row
# enter0 = ttk.Label(tabcalc, text = "",)
# enter0.grid(column = 0, row = 1)
label_bestpractice = ttk.Label(tabcalc, text = " Best practice ", font=("Calibri", 10, 'italic'))
label_bestpractice.grid(column = 0, row = 1, sticky = 'NE')
header_input = ttk.Label(tabcalc, text = "Input", font = ("Calibri",14))
header_input.grid(column = 0, row = 2, sticky = 'E')
button_browse = ttk.Button(tabcalc, text = "Browse", command = FileDialog)
button_browse.grid(column =0, row = 3, sticky = 'E')

label_input = ttk.Label(tabcalc, text = "Input file:  ",font = ("Calibri",11))
label_input.grid(column = 1, row = 3, sticky = 'E')
label_file = ttk.Label(tabcalc, text = "No file",font = ("Calibri",11))
label_file.grid(column = 2, row = 3, sticky = 'W')
enter1 = ttk.Label(tabcalc, text = "_______________")
enter1.grid(column = 0, row = 4, sticky = 'E')

#### empty cell
enter2 = ttk.Label(tabcalc, text = "")
enter2.grid(column = 0, row = 7, sticky = 'E')
#### header output
header_output = ttk.Label(tabcalc, text = "Output", font = ("Calibri",14))
header_output.grid(column = 0, row = 8, sticky = 'E')
## Checkbox plot
checkplot = tk.IntVar()
checkplot.set(0)
checkBox_plot = ttk.Checkbutton(tabcalc, variable=checkplot, onvalue=1, offvalue=0, text="Plot results")
checkBox_plot.grid(column = 1, row = 9, sticky = 'W')
## Checkbox export earth pressure results
checkexp_ep = tk.IntVar()
checkexp_ep.set(0)
checkBox_exportep = ttk.Checkbutton(tabcalc, variable=checkexp_ep, onvalue=1, offvalue=0, text="Export earth pressure results as .txt",command = Disable)
checkBox_exportep.grid(column = 1, row = 10, sticky = 'W')
## Checkbox export structure results
checkexp = tk.IntVar()
checkexp.set(0)
checkBox_export = ttk.Checkbutton(tabcalc, variable=checkexp, onvalue=1, offvalue=0, text="Export results as .txt",command = Disable)
checkBox_export.grid(column = 1, row = 11, sticky = 'W')
## Checkbox generate reports
checkreport = tk.IntVar()
checkreport.set(0)
checkBox_report = ttk.Checkbutton(tabcalc, variable=checkreport, onvalue=1, offvalue=0, text="Generate reports",command = Disable)
checkBox_report.grid(column = 1, row = 12, sticky = 'W')
## text export results
label_outputdir = ttk.Label(tabcalc, text ="Export results to:  ",font = ("Calibri",11), foreground = 'grey')
label_outputdir.grid(column = 1, row = 13, sticky = 'E')
## directory path
label_dir = ttk.Label(tabcalc, text = "No directory",font = ("Calibri",11), foreground = 'grey')
label_dir.grid(column = 2, row = 13, sticky = 'W')

## Browse button
button_output = ttk.Button(tabcalc, text = "Browse", command = OutputDialog, state='disabled')
button_output.grid(column =0, row = 13, sticky = 'E')
#### empty cell
enter3 = ttk.Label(tabcalc, text = "_______________")
enter3.grid(column = 0, row = 14, sticky = 'E')
#### empty cell
enter4 = ttk.Label(tabcalc, text = "________________________________________")
enter4.grid(column = 1, row = 14, sticky = 'W')
#### empty cell
enter5 = ttk.Label(tabcalc, text = "")
enter5.grid(column = 0, row = 15, sticky = 'W')
#### header calculations
header_calc = ttk.Label(tabcalc, text = "Calculations", font = ("Calibri",14))
header_calc.grid(column = 0, row = 16, sticky = 'E')
## status label
label_stat = ttk.Label(tabcalc, text = "Status:",font = ("Calibri",11))
label_stat.grid(column = 1, row = 17, sticky = 'E')
## status 
stat = ttk.Label(tabcalc, text = " No input file",font = ("Calibri",11))
stat.grid(column = 2, row = 17, sticky = 'W')
## Calculation number label
label_calcno = ttk.Label(tabcalc, text = "Calc. no.:" ,font = ("Calibri",11))
label_calcno.grid(column = 1, row = 18, sticky = 'E')
## Calculation number 
calcno = ttk.Label(tabcalc, text = "" ,font = ("Calibri",11))
calcno.grid(column = 2, row = 18, sticky = 'W')
#### empty cell
enter6 = ttk.Label(tabcalc, text = "")
enter6.grid(column = 1, row = 19)
## Calculation button
button_calc = ttk.Button(tabcalc, text="Run calculations", command=Calculate)
button_calc.grid(column = 1, row = 20, sticky = 'E')
## Warning label
warning = ttk.Label(tabcalc, text = "", font = ("Calibri",11),foreground = 'red')
warning.grid(column = 2, row = 20, sticky = 'W')
## Progressbar
pb = ttk.Progressbar(tabcalc, length=300, mode='determinate')
pb.grid(column = 2, row = 21, sticky = 'W')

#### empty cell
enter7 = ttk.Label(tabcalc, text = "")
enter7.grid(column = 0, row = 21)
#### empty cell
enter8 = ttk.Label(tabcalc, text = "")
enter8.grid(column = 0, row = 22)
#### empty cell
enter9 = ttk.Label(tabcalc, text = "")
enter9.grid(column = 0, row = 23)
#### empty cell
enter10 = ttk.Label(tabcalc, text = "")
enter10.grid(column = 0, row = 24)
#### empty cell
enter11 = ttk.Label(tabcalc, text = "")
enter11.grid(column = 0, row = 25)
## COWI A/S
label_cowi = ttk.Label(tabcalc, text = "COWI A/S",font = ("Calibri",9))
label_cowi.grid(column = 0, row = 26, sticky = 'E')
## Log
text = 'Current version: '+Version
label_vers = ttk.Label(tabcalc, text = text,font = ("Calibri",9))
label_vers.grid(column = 2, row = 26, sticky = 'W')

####################### End of Calculation tab #############################

####################### Log tab #########################################
### Logo and header
label_logo = ttk.Label(tablog, text = " COWI", font=("Century Schoolbook", 33), foreground = 'orange red')
label_logo.grid(column = 0, row = 0, sticky = 'SE')
label_header = ttk.Label(tablog, text = "Calculation log", font=("Calibri", 16))
label_header.grid(column = 1, row = 0, sticky = 'S')

logtxt = tkst.ScrolledText(tablog, width=70, height=25)
logtxt.insert(tk.END,'Load file - start calculating.')
logtxt.grid(column=1, row=1)
####################### End of log tab #############################

####################### Version tab #########################################
### Logo and header
label_logo = ttk.Label(tabvers, text = " COWI", font=("Century Schoolbook", 33), foreground = 'orange red')
label_logo.grid(column = 0, row = 0, sticky = 'SE')
label_header = ttk.Label(tabvers, text = "Version", font=("Calibri", 16))
label_header.grid(column = 4, row = 0, sticky = 'SW')
#### empty cell
enter11 = ttk.Label(tabvers, text = "")
enter11.grid(column = 1, row = 1)
#### empty cell
enter12 = ttk.Label(tabvers, text = "")
enter12.grid(column = 1, row = 2)
label_vershead_vers = ttk.Label(tabvers, text = "Version",font = ("Calibri",12))
label_vershead_vers.grid(column = 1, row = 3, sticky = 'W')
label_vers_vers2 = ttk.Label(tabvers, text = "2.0",font = ("Calibri",12))
label_vers_vers2.grid(column = 1, row = 4, sticky = 'W')
label_vers_vers1 = ttk.Label(tabvers, text = "1.0",font = ("Calibri",12))
label_vers_vers1.grid(column = 1, row = 5, sticky = 'W')
label_vers_vers2 = ttk.Label(tabvers, text = "0.1",font = ("Calibri",12))
label_vers_vers2.grid(column = 1, row = 6, sticky = 'W')
label_vershead_date = ttk.Label(tabvers, text = "Date",font = ("Calibri",12))
label_vershead_date.grid(column = 2, row = 3, sticky = 'W')
label_vers_date1 = ttk.Label(tabvers, text = "22.03.2024",font = ("Calibri",12))
label_vers_date1.grid(column = 2, row = 4, sticky = 'W')
label_vers_date1 = ttk.Label(tabvers, text = "12.05.2020",font = ("Calibri",12))
label_vers_date1.grid(column = 2, row = 5, sticky = 'W')
label_vers_date2 = ttk.Label(tabvers, text = "10.01.2020",font = ("Calibri",12))
label_vers_date2.grid(column = 2, row = 6, sticky = 'W')
label_vershead_prep = ttk.Label(tabvers, text = "Prepared",font = ("Calibri",12))
label_vershead_prep.grid(column = 3, row = 3, sticky = 'W')
label_vers_prep1 = ttk.Label(tabvers, text = "EMBT",font = ("Calibri",12))
label_vers_prep1.grid(column = 3, row = 4, sticky = 'W')
label_vers_prep1 = ttk.Label(tabvers, text = "EMBT",font = ("Calibri",12))
label_vers_prep1.grid(column = 3, row = 5, sticky = 'W')
label_vers_prep2 = ttk.Label(tabvers, text = "EMBT",font = ("Calibri",12))
label_vers_prep2.grid(column = 3, row = 6, sticky = 'W')
label_vershead_check = ttk.Label(tabvers, text = "Checked",font = ("Calibri",12))
label_vershead_check.grid(column = 4, row = 3, sticky = 'W')
label_vers_check1 = ttk.Label(tabvers, text = "MLHU",font = ("Calibri",12))
label_vers_check1.grid(column = 4, row = 4, sticky = 'W')
label_vers_check1 = ttk.Label(tabvers, text = "EMSS",font = ("Calibri",12))
label_vers_check1.grid(column = 4, row = 5, sticky = 'W')
label_vers_check2 = ttk.Label(tabvers, text = "EMSS",font = ("Calibri",12))
label_vers_check2.grid(column = 4, row = 6, sticky = 'W')
label_vershead_desc = ttk.Label(tabvers, text = "Description",font = ("Calibri",12))
label_vershead_desc.grid(column = 5, row = 3, sticky = 'W')
label_vers_desc1 = ttk.Label(tabvers, text = "Added sheet pile wall - Add on",font = ("Calibri",12))
label_vers_desc1.grid(column = 5, row = 4, sticky = 'W')
label_vers_desc1 = ttk.Label(tabvers, text = "Report generation and vertical equilibrium added",font = ("Calibri",12))
label_vers_desc1.grid(column = 5, row = 5, sticky = 'W')
label_vers_desc2 = ttk.Label(tabvers, text = "Test version",font = ("Calibri",12))
label_vers_desc2.grid(column = 5, row = 6, sticky = 'W')
####################### End of log tab #############################

tab_parent.pack(expand=1, fill='both')

window.mainloop()