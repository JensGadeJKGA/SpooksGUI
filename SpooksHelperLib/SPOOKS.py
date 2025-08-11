
from datetime import datetime
import os
import subprocess
from SpooksHelperLib.Utils import utils
from SpooksHelperLib.SoilProfiles import soilprofiles

class spooksfile():
    def __init__(self):
        pass

    def anchorLevel(self, Anchorlevel, PrescrbAnchorForce, anchCoeffVars):
        baseArr = [format(anchCoeffVars["iA"],'.2f'), 
                        format(anchCoeffVars["iB"],'.2f'),
                        format(anchCoeffVars["iC"],'.2f'), 
                        format(anchCoeffVars["zT"],'.2f'), 
                        format(anchCoeffVars["zR"],'.2f')]
        
        ## If no anchor
        if Anchorlevel == None: 

            if format(anchCoeffVars["iB"],'.2f') != '1.00' or format(anchCoeffVars["iB"],'.2f') != '0.00':
                print('No compatibility between failure mode and failure coefficients')
                return ['N/A', 
                            'N/A',
                            'N/A', 
                            'N/A', 
                            'N/A']
            else:
                return baseArr
        
        # if anchor and no prescribed anchor force
        elif Anchorlevel != None and PrescrbAnchorForce == 0.00: 
            baseArr.append(format(Anchorlevel,'.2f'))

            return baseArr
        
        # if anchor and prescribed anchor force
        elif Anchorlevel != None and PrescrbAnchorForce != 0.00 and format(anchCoeffVars["iC"],'.2f') == '0.00' and float(anchCoeffVars["iB"]) > 0: 
            baseArr.append(format(Anchorlevel,'.2f'))
            baseArr.append(format(PrescrbAnchorForce,'.2f'))

            return baseArr
        
        
           
        

    def GenerateSPOOKSInputFile(self, Analysis):
        State = Analysis.get('State')

        Geninf = [format(Analysis.get('SlopeFront'),'.2f'), 
                format(Analysis.get('SlopeBack'),'.2f'),
                format(Analysis.get('DesignLoadFront'),'.2f'), 
                format(Analysis.get('DesignLoadBack'),'.2f'), 
                format(Analysis.get('WaterLevelFront'),'.2f'), 
                format(Analysis.get('WaterLevelBack'),'.2f'), 
                format(Analysis.get('WaterDensity'),'.2f')]
    
        Generalinfo = utils.AddSpaces(Geninf)
        ############ First lines in SPOOKSWAT input file (L)
        
        L = ['<', 'Project:' +' '+ Analysis.get('Project'), 'Initials:' +' '+ Analysis.get('Initials'), 'Subject:' +' '+str(Analysis.get('Subject')), '>', '<', Generalinfo, '>', '<']
        
        
        
        ################# SOIL FRONT ####################################

        L=soilprofiles.designsoillayer(Analysis.get('DesignSoilLayersFront'), State, L)
    
        ########################## SOIL BACK ##############################

        L=soilprofiles.designsoillayer(Analysis.get('DesignSoilLayersBack'), State, L)
        
        ################## FAILURE MODE (ANCHOR COEFFICIENTS) ###################
        AnchCoeffVars = {
            "iA": Analysis.get('iA'),
            "iB": Analysis.get('iB'),
            "iC": Analysis.get('iC'),
            "zT": Analysis.get('zT'),
            "zR": Analysis.get('LevelLoadBack')
        }
        Coeff_temp = self.anchorLevel(Analysis.get('AnchorLevel'), Analysis.get('PrescrbAnchorForce'), AnchCoeffVars)
        Coeff = utils.AddSpaces(Coeff_temp)
        L.append(Coeff)
        if Analysis.get('AnchorLevel') == None:
            L.append('                    ')
        
        ############ KING POST WALL PARAMETERS (if data is properly entered in excel input file)
        zB = Analysis.get('zB')
        WD = Analysis.get('WD')
        CC = Analysis.get('CC')

        if zB != None and WD != None and CC != None:
            
            KingPostParam = ""

            KingPostParam = utils.AddSpaces([format(zB,'.2f'),
                            format(WD,'.2f'),
                            format(CC,'.2f')])
            L.append('                                        ' + KingPostParam) #+40 init spaces
        
        elif zB == None and WD == None and CC == None:
            
            L.append('')
        
        else:
            
            print('Improper King/Post wall parameters')
            
        
        ###### OUTPUT PATHS (SPOOKS working directory - temporary files)
        
        TemporaryPath = utils.TemporaryWorkingDirectory()
        
        ## output plot file path
        plotpath_output = os.path.join(TemporaryPath, r'spooks.plt')
        
        L.append('>'+'    '+plotpath_output)

        
        ############### ADDITIONAL PRESSURE FILE #########################
        
        if Analysis.get('AddPressureProfile') in ['AP1', 'AP2', 'AP3', 'AP4', 'AP5', 'AP6', 'AP7', 'AP8', 'AP9', 'AP10']:
        
            ## Additional pressure file
            addpressfile = []
        
            
            APlevel = utils.AddSpaces(Analysis.get('AddPress_z'))
            
            addpressfile.append(APlevel+'    ')
            addpressfile.append('  ')
            
            APvalue = utils.AddSpaces(Analysis.get('AddPress_ez'))
            
            addpressfile.append(APvalue+'    ')
            
            ### Generating additional pressure file for input file
            addpressurefile = os.path.join(TemporaryPath, r'addpressfile')
            
            with open(addpressurefile, 'w+') as f:
                for item in addpressfile:
                    f.write("%s\n" % item)
            
            f.close()
                        
            L.append('     '+addpressurefile)
            
        else:
            
            L.append('')
            
        ############### 4.10. END SPOOKSWAT INPUT FILE ###################
        
        L.append('>END')
        
        ###### Export to file
        
        inputfile = os.path.join(TemporaryPath, r'params')
        
        with open(inputfile, 'w+') as f:
            for item in L:
                f.write("%s\n" % item)
        
        f.close()
        
        
        Output = {'Analysis': Analysis,
                'InputFileDir': TemporaryPath,
                'InputFile': inputfile,
                'SPOOKSPlotFile': plotpath_output}
        
        
        return Output
    
    def LogFile(InputFileDir,AnalysisNo,SPOOKSOut):
        logfile = os.path.join(InputFileDir, r'log_file.txt')
        
        if AnalysisNo == 0:  ### Creates (or overwrites existing) log file
            with open(logfile, 'w') as f:
                for item in SPOOKSOut[13:]:
                    f.write("%s\n" % item)
        else:                ### Appends to new log file
            with open(logfile, 'a') as f:
                for item in SPOOKSOut[13:]:
                    f.write("%s\n" % item)
        f.close()
    
    def ExecuteSPOOKS(self, Analysis,logtxt,tk):
    
        Output = self.GenerateSPOOKSInputFile(Analysis)
        
        Analysis = Output.get('Analysis')
        AnalysisNo = dict(Analysis).get('AnalysisNo')
        InputFile = Output.get('InputFile')
        InputFileDir = Output.get('InputFileDir')
        SPOOKSPlotFile = Output.get('SPOOKSPlotFile')
        
        
        
        ## Date and time
        Now = datetime.now() # current date and time
        DateTime = Now.strftime("%d.%m.%Y, %H:%M:%S")
        Date = Now.strftime("%d.%m.%Y")
        
        args = r'spookswat.exe'+' '+'/CALC:"'+InputFile+'"'
            
        process = subprocess.Popen(args, cwd = r'C:\Program Files (x86)\WinSpooks', shell=True, stdin = None, stderr = subprocess.PIPE, stdout = subprocess.PIPE, universal_newlines=True)
        
        SPOOKSOut = process.stdout.readlines()
        
        logtxt.insert(tk.END, SPOOKSOut)
        
        print(SPOOKSOut) ### Printing output if script run as script

        #logtxt.insert(tk.END, out) ### Print "out" to log tab in GUI
        
        ReportWarnings = []
        ReportErrors = []
        
        ###### If "STOPPED", "WARNING" or "*ERR*" is contained in SPOOKSWAT output, status changes
        for i in range(0,len(SPOOKSOut)):
            p = str(SPOOKSOut[i])
            if 'STOPPED' in p:
                print('Calculation stopped - check log file')
                ReportErrors.append('Calculation stopped - check log file')
            if 'WARNING' in p:
                print('Calculation stopped')
                ReportWarnings.append('WinSPOOKS warning: check log file')
            if '*ERR*' in p:
                print('Calculation stopped due to error')
                ReportErrors.append('WinSPOOKS error: check log file')
            if 'The input contains boundaries below the encastre level.' in p: ## warning in report if generation of reports is checked off:
                ReportWarnings.append('The input contains boundaries below the encastre level.')
                
        self.LogFile(InputFileDir,AnalysisNo,SPOOKSOut)
        
        ExecuteOutput = {'Analysis': Analysis,
                        'Date': Date,
                        'DateTime': DateTime,
                        'SPOOKSOutput': SPOOKSOut,
                        'Warnings': ReportWarnings,
                        'Errors': ReportErrors,
                        'InputFileDir': InputFileDir,
                        'SPOOKSPlotFile': SPOOKSPlotFile}
        
        
        return ExecuteOutput
    
    # Main function that coordinates the full result extraction and structuring
    def GetResults(ExecuteOutput):
        # Step 1: Parse basic results
        ResultVar = utils.parse_result_variables(ExecuteOutput)

        # Step 2: Read plot file
        lines = utils.read_plot_file_lines(ExecuteOutput)

        # Step 3: Parse earth pressure block
        (
            EarthPressureResults, level_graphic, e1_graphic, e2_graphic,
            dw_graphic, enet_graphic, shearforce, shearlevel,
            moment, momentlevel, ju_graphic
        ) = utils.parse_earth_pressure_block(utils.extract_earth_pressure_block(lines))

        # Step 4: Calculate extreme forces
        maxshear, maxshearlevel, maxmom, maxmomlvl = utils.compute_extreme_forces(
            shearforce, shearlevel, moment, momentlevel
        )

        # Step 5: Organize plot-related results
        PlotResults = {
            'MaxShearForce': maxshear,
            'LevelMaxShearforce': maxshearlevel,
            'MaxMoment': maxmom,
            'LevelMaxMoment': maxmomlvl,
            'PlotLevels': level_graphic,
            'e1': e1_graphic,
            'e2': e2_graphic,
            'DW': dw_graphic,
            'enet': enet_graphic,
            'ShearForce': shearforce,
            'ShearForceLevel': shearlevel,
            'Moment': moment,
            'MomentLevel': momentlevel,
            'JU': ju_graphic
        }

        # Step 6: Organize tabular result variables
        Results = {
            'EncastreLevel': ResultVar[0],
            'EncastreMoment': ResultVar[1],
            'YieldHingeLevel': ResultVar[2],
            'YieldHingeMoment': ResultVar[3],
            'ToeLevel': ResultVar[4],
            'AnchorForce': ResultVar[5],
            'MomentAtAnchor': ResultVar[6]
        }

        # Step 7: Final combined result dictionary
        return {
            'Analysis': ExecuteOutput.get('Analysis'),
            'DateTime': ExecuteOutput.get('DateTime'),
            'Date': ExecuteOutput.get('Date'),
            'Warnings': ExecuteOutput.get('Warnings'),
            'Errors': ExecuteOutput.get('Errors'),
            'PlotResults': PlotResults,
            'EarthPressureResults': EarthPressureResults,
            'Results': Results
        }