
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
from SpooksHelperLib.Utils import utils
from SpooksHelperLib.Generators import generators
from SpooksHelperLib.SoilProfiles import soilprofiles
from SpooksHelperLib.SPOOKS import spooksfile
from SpooksHelperLib.Vequilibrium import verticalEquilibrium
from SpooksHelperLib.GenerateReport.generatePDF import generatePDF
from SpooksHelperLib.GenerateReport.reportFront import reportFront
from SpooksHelperLib.GenerateReport.generateReport import generateReport

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf
import subprocess
import io
import os
import tkinter as tk
import tkinter.scrolledtext as tkst
import contextlib
import PyPDF2
import subprocess
import time

from fpdf import FPDF
from getpass import getuser
from datetime import datetime
from openpyxl import load_workbook
from tkinter import ttk
from tkinter import filedialog
from scipy.interpolate import interp1d
from shutil import copyfile


################ Version ##################

Version = '2.1'

################ Input file ID ############

InputFileIDGUI = 'A3'


############### IMPORT SHEET PILE WALL PLUG IN ###################

from Steel_Sheet_Pile_Wall import steel_sheet_pile_implementer


def log_usage():

    import getpass
    import socket
    try:
        log_path = r"O:\Organisation\DK_1551\Diverse\SpooksLog"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user = getpass.getuser()
        pc_name = socket.gethostname()
        log = os.path.join(log_path, "log.log")
        with open(log, "a") as f:
            f.write(f"{timestamp}\t{user.upper()}\t{pc_name.upper()}\n")
    except:
        pass

################### FUNCTIONS ####################################
        
def TemporaryWorkingDirectory():
    

    user = "MLHU"
    
    ## output path
    TemporaryPath = os.path.join(r'C:\Users', user)
    TemporaryPath = os.path.join(TemporaryPath, r'AppData\Local\Temp\2')
    
    if not os.path.exists(TemporaryPath): ## if directory does not exist -> create it
        os.makedirs(TemporaryPath)
        
    return TemporaryPath


def PlotResults(FeederOutput):
    
    print('Plotting results...')
    
    
    WallResults = []
    

    ## List of parent analysis numbers
    ParentAnalyses = []
    for Analysis in FeederOutput:
        
        GetResultsOutput = Analysis.get('GetResultsOutput')
        ParentAnalyses.append(GetResultsOutput.get('Analysis').get('ParentAnalysis'))
    
    ParentAnalyses = list(np.unique(ParentAnalyses))
    
    for ParentAnalysis in ParentAnalyses:
        
        WallResults.append({'ParentAnalysis': ParentAnalysis,
                            'Subject' : [],
                            'PlotIDs': [],
                            'MaxMoments': [],
                            'MaxShearForces': [],
                            'ToeLevels': [],
                            'AnchorForces': []})
        
        
    for WallResult in WallResults:
        
        ParentAnalysis = WallResult.get('ParentAnalysis')
        
    
        ## ID for plotting
        PlotID = 0
    
        for Analysis in FeederOutput:
            
            GetResultsOutput = Analysis.get('GetResultsOutput')
            
            MaxMomentAnalysis = GetResultsOutput.get('PlotResults').get('MaxMoment')
            
            MaxShearForceAnalysis = GetResultsOutput.get('PlotResults').get('MaxShearForce')
            
            ToeLevel = GetResultsOutput.get('Results').get('ToeLevel')
            
            AnchorForce = GetResultsOutput.get('Results').get('AnchorForce')
            
            ParentAnalysisInput = GetResultsOutput.get('Analysis').get('ParentAnalysis')
            
            Subject = GetResultsOutput.get('Analysis').get('Subject')
            
            if ParentAnalysisInput == ParentAnalysis:
                
                WallResult.get('Subject').append(Subject)
                WallResult.get('PlotIDs').append(PlotID)
                WallResult.get('MaxMoments').append(abs(MaxMomentAnalysis))
                WallResult.get('MaxShearForces').append(abs(MaxShearForceAnalysis))
                WallResult.get('ToeLevels').append(ToeLevel)
                
                if isinstance(AnchorForce,float):
                    
                    WallResult.get('AnchorForces').append(AnchorForce)
                else:
                    WallResult.get('AnchorForces').append(0.00)
            
                ## Updating Plot ID
                PlotID = PlotID + 1
                    


                

    fig = plt.figure()
    #fig.canvas.set_window_title('WinSpooks Plug-in results')
    ### Max. moment
    ax1 = fig.add_subplot(221)
    color = 'black'
    for Results in WallResults:
        plt.plot(Results.get('PlotIDs'),Results.get('MaxMoments'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
    ax1.set_ylabel('Max. |bending moment| [kNm/m]', color = color)
    ax1.tick_params(axis='y', labelcolor = color)
    plt.grid()
    plt.legend()    


    ax2 = fig.add_subplot(222)
    color = 'black'
    for Results in WallResults:
        plt.plot(Results.get('PlotIDs'),Results.get('MaxShearForces'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
    ax2.set_ylabel('Max. |shear force| [kN/m]', color = color)
    ax2.tick_params(axis='y', labelcolor = color)
    plt.grid()
    plt.legend()
    
    ### Anchor force
    ax3 = fig.add_subplot(223)
    color = 'black'
    for Results in WallResults:
        plt.plot(Results.get('PlotIDs'), Results.get('AnchorForces'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
    ax3.set_ylabel('Anchor force [kN/m]', color = color)
    ax3.set_xlabel('Plot ID')
    ax3.tick_params(axis='y', labelcolor = color)
    plt.grid()
    plt.legend()

    ### Toe level
    ax4 = fig.add_subplot(224)
    color = 'black'
    for Results in WallResults:
        plt.plot(Results.get('PlotIDs'), Results.get('ToeLevels'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
    ax4.set_ylabel('Toe level [m]', color = color)
    ax4.set_xlabel('Plot ID')
    ax4.tick_params(axis='y', labelcolor = color)
    plt.grid()
    plt.legend()
    plt.show()

    

def ExportResultsAsTxt(FeederOutput, OutputDirList):
    
    if FeederOutput[0].get('GetResultsOutput')['Analysis']['SheetPileAddOnInput']['UseAddOn'] == "Yes":
        printlist = [['Analysis No.','Subject', 'Soil Profile',
                     'State', 'Load Combination', 'AnchorLevel',
                     'AnchorForce', 'Moment at Anchor Level', 
                     'Level of Max. Moment', 'Max. Moment',
                     'Encastre Level', 'Encastre Moment',
                     'Yield Level', 'Yield Moment', 'Max. Shear Force',
                     'Toe Level', 'Sum of vertical forces','Profile',
                     'Max utilization','Lvl of Max utilization']]
    else:
        printlist = [['Analysis No.','Subject', 'Soil Profile',
                     'State', 'Load Combination', 'AnchorLevel',
                     'AnchorForce', 'Moment at Anchor Level', 
                     'Level of Max. Moment', 'Max. Moment',
                     'Encastre Level', 'Encastre Moment',
                     'Yield Level', 'Yield Moment', 'Max. Shear Force',
                     'Toe Level', 'Sum of vertical forces']]
    
    
    
    for Analysis in FeederOutput:
        GetResultsOutput = Analysis.get('GetResultsOutput')
        
        print(GetResultsOutput)
        
        if GetResultsOutput['Analysis']['SheetPileAddOnInput']['UseAddOn'] == 'Yes':
            
            try:
                SheetPileAddOnResults = steel_sheet_pile_implementer(GetResultsOutput)
            except Exception as e:
                print(f"Error processing sheet pile results: {e}")
                SheetPileAddOnResults = {'SheetPileProfile': 'N/A',
                                         'RUR': 'N/A',
                                         'RURLevel': 'N/A',
                                         'RURLevel_max': 'N/A',
                                         'RotCap': 'N/A'}                
        else:
            
            SheetPileAddOnResults = {'SheetPileProfile': 'N/A',
                                     'RUR': 'N/A',
                                     'RURLevel': 'N/A',
                                     'RURLevel_max': 'N/A',
                                     'RotCap': 'N/A'}
        
        ## Vertical equilibrium
        VerticalEquilibriumOutput = verticalEquilibrium.VerticalEquilibrium(GetResultsOutput)
        
        AnalysisNo = GetResultsOutput.get('Analysis').get('AnalysisNo')
        zT = GetResultsOutput.get('Analysis').get('zT')
        Subject = GetResultsOutput.get('Analysis').get('Subject')
        SoilProfile = GetResultsOutput.get('Analysis').get('SoilProfile')
        LoadCombination = GetResultsOutput.get('Analysis').get('LoadCombination')
        State = GetResultsOutput.get('Analysis').get('State')
        AxialWallLoad = GetResultsOutput.get('Analysis').get('AxialWallLoad')
        try: 
            AnchorLevel = GetResultsOutput.get('Analysis').get('AnchorLevel')
            AnchorInclination = GetResultsOutput.get('Analysis').get('AnchorInclination')
            AnchorForce = GetResultsOutput.get('Results').get('AnchorForce')
            AnchorAxial = AnchorForce/np.cos(np.radians(AnchorInclination))
            MomentAtAnchor = GetResultsOutput.get('Results').get('MomentAtAnchor')
        except:
            AnchorLevel = 'N/A'
            AnchorInclination = 'N/A'
            AnchorForce = 'N/A'
            AnchorAxial = 'N/A'
            MomentAtAnchor = 'N/A'
        LevelMaxMoment = GetResultsOutput.get('PlotResults').get('LevelMaxMoment')
        MaxMoment = GetResultsOutput.get('PlotResults').get('MaxMoment')
        EncastreLevel = GetResultsOutput.get('Results').get('EncastreLevel')
        EncastreMoment = GetResultsOutput.get('Results').get('EncastreMoment')
        YieldHingeLevel = GetResultsOutput.get('Results').get('YieldHingeLevel')
        YieldMoment = GetResultsOutput.get('Results').get('YieldHingeMoment')
        MaxShearForce = GetResultsOutput.get('PlotResults').get('MaxShearForce')
        ToeLevel = GetResultsOutput.get('Results').get('ToeLevel')
        if ToeLevel == "N/A":
            DesignSoilLayersFront = GetResultsOutput.get('Analysis').get('SoilLayersFront')
            SoilLevelsFront = []
            for SoilLayer in DesignSoilLayersFront:
                SoilLevelsFront.append(SoilLayer.get('TopLayer'))
            GroundLevelFront = max(SoilLevelsFront)
            ToeLevel = GroundLevelFront - 0.1
        SumTanForce = VerticalEquilibriumOutput.get('SumTanForce')
        WallMass = GetResultsOutput.get('Analysis').get('WallMass')
        WallSpecificWeight = WallMass * 9.82 / 1000
        WeightWallTotal = WallSpecificWeight * (zT - ToeLevel)
        
        sel_profile = SheetPileAddOnResults.get('SheetPileProfile')
        max_util = SheetPileAddOnResults.get('RUR')
        max_util_lvl = SheetPileAddOnResults.get('RURLevel_max')
        
        
        if AnchorLevel != 'N/A':
            SumVertForces = SumTanForce-AnchorAxial*np.sin(np.radians(float(AnchorInclination)))-WeightWallTotal-AxialWallLoad
        else:
            SumVertForces =  SumTanForce-WeightWallTotal-AxialWallLoad
        
    
    #### Generating analyses results list
    
        if GetResultsOutput['Analysis']['SheetPileAddOnInput']['UseAddOn'] == 'Yes':
            printlist_temp = [AnalysisNo, Subject, SoilProfile, 
                              State, LoadCombination, AnchorLevel, 
                              AnchorForce, MomentAtAnchor, LevelMaxMoment, 
                              MaxMoment, EncastreLevel, EncastreMoment, 
                              YieldHingeLevel, YieldMoment, MaxShearForce, 
                              ToeLevel, SumVertForces, sel_profile, max_util,
                              max_util_lvl]
        else:
            printlist_temp = [AnalysisNo, Subject, SoilProfile, 
                              State, LoadCombination, AnchorLevel, 
                              AnchorForce, MomentAtAnchor, LevelMaxMoment, 
                              MaxMoment, EncastreLevel, EncastreMoment, 
                              YieldHingeLevel, YieldMoment, MaxShearForce, 
                              ToeLevel, SumVertForces]

        printlist.append(printlist_temp)
    
    results_path = OutputDirList[-1]
    results_path = os.path.join(results_path, r'Results.txt')
    np.savetxt(results_path, printlist, delimiter=';', fmt='%s')
        
        ###############################
    


def ExportEarthPressureResultsAsTxt(FeederOutput, OutputDirList):
    
    ## Temporary file dir
    #TemporaryFile = TemporaryWorkingDirectory()
    ## Initial empty array
    EarthPressureResults = np.empty((0,8), int) # Empty array
    
    for Analysis in FeederOutput:

        #GetResultsOutput = Analysis.get('GetResultsOutput')
        
        EarthPressureResultsOutput = Analysis.get('GetResultsOutput').get('EarthPressureResults')
        
        try:
            AnalysisNo = 'Analysis no. '+ Analysis.get('AnalysisNo')
        except:
            AnalysisNo = 'N/A'
        AnalysisNoArray = np.empty((0,8), int) ## empty array
        np.append(AnalysisNoArray, ['AnalysisNo', AnalysisNo,'','','','','',''])
        
    
        EarthPressureResults = np.concatenate((EarthPressureResults, AnalysisNoArray, EarthPressureResultsOutput), axis=0)
        
    
    
    # Exporting earth pressure results as text file
    results_path = OutputDirList[-1] ## results path
    EP_results = os.path.join(results_path, r'EarthPressureResults.txt')
    np.savetxt(EP_results, EarthPressureResults, delimiter='\t', fmt='%s')
    
    
    return EarthPressureResults

              





############### GUI Functions

def OpenSpooks():
    
    ################### OPEN WINSPOOKS ###################################
    ######### Check in WinSpooks is running - if not -> Run
    ######### (necessary for license check)

    res = subprocess.check_output(['tasklist']).splitlines()
    winspooks = []
    for i in range(0,len(res)):
        p = str(res[i])
        if 'WinSpooks.exe' in p:
            winspooks.append(i) 
    
    if winspooks == []:

        subprocess.Popen(['C:\Program Files (x86)\WinSpooks\WinSpooks.exe'])
        time.sleep(0.5)
    
    res = None  ## Deleting list
    
    


################### 1. OPEN WINSPOOKS ###################################
######### Check in WinSpooks is running - if not -> Run
######### (necessary for license check)


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
            
            PlotResults(FeederOutput)
            
        ## Export results
        if checkexp.get() == 1:
            
            stat.configure(text = "Exporting results...")
            tabcalc.update_idletasks()
            
            ExportResultsAsTxt(FeederOutput,OutputDirList)
            
        
        ## Export earth pressure results
        if checkexp_ep.get() == 1:
            
            stat.configure(text = "Exporting results...")
            tabcalc.update_idletasks()
            
            ExportEarthPressureResultsAsTxt(FeederOutput, OutputDirList)
            
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