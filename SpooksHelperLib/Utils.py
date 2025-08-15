import pandas as pd
import numpy as np
import os
import io
from openpyxl import load_workbook
from tkinter import ttk
import tkinter as tk


###In this file you will find miscellaneous utility functions.

class utils:
    def __init__(self):
        self.InputFileIDGUI = 'A3'
        self.stat = ttk.Label(ttk.Frame(ttk.Notebook(tk.Tk())), text = " No input file",font = ("Calibri",11))
        

    ####This function generalises the data row creation. The next function does the same thing, but for multiple cells. It takes an array with a set of ranges, and for those ranges it readies the data rows.
    def data_rows(cellrange):
        data_rows = []
        for row in cellrange:
            data_cols = []
            for cell in row:
                data_cols.append(cell.value)
            data_rows.append(data_cols)
        
        return data_rows
    
    def data_rows_arr(cellrangearr):
        return_array = []
        for cellrange in cellrangearr:
            data_rows = []
            for row in cellrange:
                data_cols = []
                for cell in row:
                    data_cols.append(cell.value)
                data_rows.append(data_cols)
                pd.DataFrame(data_rows)
            return_array.append(data_rows)
        
        return return_array

    def InputFileIDChecker(self,InputFileID):        
        InputFileStatus = None
        
        if InputFileID == self.InputFileIDGUI:
            
            InputFileStatus = 'OK'
            
        else:
            
            self.stat.configure(text = 'Input file version does not match GUI version')
            
        return InputFileStatus


    def TemporaryWorkingDirectory():
        user = "JKGA"
        
        ## output path
        TemporaryPath = os.path.join(r'C:\Users', user)
        TemporaryPath = os.path.join(TemporaryPath, r'AppData\Local\Temp\2')
        
        if not os.path.exists(TemporaryPath): ## if directory does not exist -> create it
            os.makedirs(TemporaryPath)
            
        return TemporaryPath

    ###This function calculates the additional pressures
    def AddPressProfiles(APnum, Add_pres, AdditionalPressures):
        AP = np.where((Add_pres.iloc[:,0]) == 'AP'+str(APnum))
        AP = AP[0]
        null = np.where(pd.isnull(Add_pres.iloc[:,1]))
        index_max = null[0][null[0] > AP] 
        index_max = index_max[0]  ### End index of AP
        
        for x in range(AP[0]+1,index_max):
            AdditionalPressures['AP'+str(APnum)]['z'].append(float(format(Add_pres.iloc[x,1],'.2f')))
            AdditionalPressures['AP'+str(APnum)]['ez'].append(float(format(Add_pres.iloc[x,2],'.2f')))
    
        return AdditionalPressures

    def PartialSafetyFactors(LoadComb, loadcombinations):
        LC = pd.DataFrame(LoadComb)
        
        # Find indices of consequence classes
        index_CC2 = np.where(LC.iloc[:, 0] == 'CC2')[0][0]
        index_CC3 = np.where(LC.iloc[:, 0] == 'CC3')[0][0]
        
        # Define the ranges for each consequence class
        cc_ranges = {
            'CC2': (index_CC2 + 2, index_CC3),
            'CC3': (index_CC3 + 2, len(LC))
        }
        
        for cc, (start, end) in cc_ranges.items():
            if cc not in loadcombinations:
                loadcombinations[cc] = {}
            
            for i in range(start, end):
                if pd.notna(LC.iloc[i, 0]):
                    Loadcombination = str(LC.iloc[i, 0]).strip()
                    
                    PartialSafetyFactors = {
                        'f_gamf': float(LC.iloc[i, 1]),
                        'f_qf':   float(LC.iloc[i, 2]),
                        'f_cf':   float(LC.iloc[i, 3]),
                        'f_cuf':  float(LC.iloc[i, 4]),
                        'f_phif': float(LC.iloc[i, 5]),
                        'f_wat':  float(LC.iloc[i, 6]),
                        'f_AP':   float(LC.iloc[i, 7]),
                        'f_gamb': float(LC.iloc[i, 8]),
                        'f_qb':   float(LC.iloc[i, 9]),
                        'f_cb':   float(LC.iloc[i, 10]),
                        'f_cub':  float(LC.iloc[i, 11]),
                        'f_phib': float(LC.iloc[i, 12])
                    }
                    
                    loadcombinations[cc][Loadcombination] = PartialSafetyFactors

        return loadcombinations

    

    def ImportExcel(input_path):
        #### Loading excel workbook
        xlsx_filename=input_path
        with open(xlsx_filename, "rb") as f:
            in_mem_file = io.BytesIO(f.read())
        
        wb = load_workbook(in_mem_file, data_only=True)
                
        ## Sheets
        INFO =  wb['INFO']
        GeneralInfo = wb['General_information']
        Stratification = wb['Stratification']
        Wall = wb['Wall']
        Water = wb['Water']
        Add_pres = wb['Additional_pressure_profiles']
        Analyses = wb['Analyses']
        LoadComb = wb['Load_combinations']
        SheetPileAddOn = wb['Addon - Sheet Pile Wall']
        
        
        ########### 3.1. LOADING DATA SHEETS TO PANDAS DATAFRAMES #########

        
        data_array = [INFO['A1':'H28'], GeneralInfo['A3':'B7'], Stratification['A4':'K289'], Wall['A3':'B5'], Water['A3':'A5'], Add_pres['A3':'C114'], Analyses['A3':'AA56'], LoadComb['A3':'M42'], SheetPileAddOn['A1':'G30']]
        docready_array = utils.data_rows_arr(data_array)

        ###### This returns an array with all the data post processing. So docready_array[0] is INFO, docready_array[1] is stratification etc.
        INFO = pd.DataFrame(docready_array[0])
        Stratification = docready_array[1]
        InputFileID = str(INFO.iloc[27,1])

        ImportData = {'InputFileID': InputFileID, 
                    'GeneralInfo': pd.DataFrame(docready_array[1]),
                    'Stratification': pd.DataFrame(docready_array[2]),
                    'Wall': pd.DataFrame(docready_array[3]),
                    'Water': pd.DataFrame(docready_array[4]),
                    'AddPress': pd.DataFrame(docready_array[5]),
                    'Analyses': pd.DataFrame(docready_array[6]),
                    'LoadComb': docready_array[7],
                    'SheetPileAddOn': pd.DataFrame(docready_array[8])}
    
    

        return ImportData
    
    def WallParameters(Wall): 
        ############# WALL PARAMETERS
        ### zT (Top wall)
        
        zT = float(format(float(Wall.iloc[1,0]), '.2f'))
        
        ### Mass of wall (for vertical equilibrium)
        wall_mass = float(Wall.iloc[1,1])
        
        WallParams = {'zT': zT,
                    'Mass': wall_mass}
        
        return WallParams


    def WaterDensity(Water):
    ######## WATER DENSITY    
        gamma_water = float(format(float(Water.iloc[1,0]), '.2f'))
        
        return gamma_water
    
    def safe_value(val, default=0.0):
        #returns val if number, else returns default
        return val if isinstance(val, (int, float)) else default
    
    
    def make_analysis_dict(self,Analyses, Analysis, ImportData, anchor_level, anchor_inclination, prescribed_anchor_force, vararr, geninfoarr):
        from SpooksHelperLib.Generators import generators
        sheetpile_addon = ImportData.get('SheetPileAddOn')
        SheetPileAddOnInput = {}
        if sheetpile_addon is not None and not sheetpile_addon.empty:
            SheetPileAddOnInput = generators.GenerateSheetPileAddOnInput(sheetpile_addon)

        return {
                'AnalysisNo': geninfoarr[0],
                'ParentAnalysis': geninfoarr[1],
                'Project': str(ImportData.get('GeneralInfo').iloc[0,1]),
                'Initials': str(ImportData.get('GeneralInfo').iloc[2,1]),
                'Checker': str(ImportData.get('GeneralInfo').iloc[3,1]),
                'Approver': str(ImportData.get('GeneralInfo').iloc[4,1]),
                'Subject': Analyses.iloc[Analysis, 0],
                'SoilProfile': Analyses.iloc[Analysis, 1],
                'SlopeBack': None,
                'SlopeFront': None,
                'SoilLayersFront': [],
                'SoilLayersBack': [],
                'zT': float(utils.WallParameters(ImportData.get('Wall')).get('zT')),
                'WallMass': float(utils.WallParameters(ImportData.get('Wall')).get('Mass')),
                'WaterDensity': utils.WaterDensity(ImportData.get('Water')),
                'AddPressureProfile': Analyses.iloc[Analysis, 11],
                'AddPress_z': [],
                'AddPress_ez': [],
                'State': Analyses.iloc[Analysis, 2],
                'WaterLevelFront': float(Analyses.iloc[Analysis, 3]),
                'WaterLevelBack': float(Analyses.iloc[Analysis, 4]),
                'WDiff': abs(float(Analyses.iloc[Analysis, 4]) - float(Analyses.iloc[Analysis, 4])),
                'LoadCombination': Analyses.iloc[Analysis, 5],
                'ConsequenceClass': Analyses.iloc[Analysis, 6],
                'Alpha': float(Analyses.iloc[Analysis, 7]),
                'LoadFront': float(Analyses.iloc[Analysis, 8]),
                'LoadBack': float(Analyses.iloc[Analysis, 9]),
                'LevelLoadBack': float(Analyses.iloc[Analysis, 10]),
                'AxialWallLoad': float(Analyses.iloc[Analysis, 12]),
                'iA': float(Analyses.iloc[Analysis, 13]),
                'iB': float(Analyses.iloc[Analysis, 14]),
                'iC': float(Analyses.iloc[Analysis, 15]),
                'AnchorLevel': anchor_level,
                'AnchorInclination': anchor_inclination,
                'PrescrbAnchorForce': prescribed_anchor_force,
                'zB': vararr['zB'],
                'WD': vararr['WD'],
                'CC': vararr['CC'],
                'KN': Analyses.iloc[Analysis, 24],
                'KP': Analyses.iloc[Analysis, 25],
                'SC': Analyses.iloc[Analysis, 26],
                'SheetPileAddOnInput': SheetPileAddOnInput
            }
    
    def AddSpaces(items):
        returnitem = ""
        for item in items:
            space = '    ' # 4 spaces default
            if len(str(item)) == 4:
                space = '      ' # 6 spaces
            if len(str(item)) == 5:
                space = '     '  # 5 spaces
            if len(str(item)) == 6:
                space = '    '   # 4 spaces
            returnitem += (space+str(item))
        return returnitem

    def linesplitter(self, lines, check, checkTwo=None, indice=0):
        for line in lines:
            if check in line or (checkTwo and checkTwo in line):
                parts = line.split()
                try:
                    return float(parts[indice])
                except (IndexError, ValueError):
                    return 'N/A'
        return 'N/A'
    
    def linesplitterMult(self,lines,checks,checkTwos,indices):
        if not (len(checks) == len(checkTwos) == len(indices)):
            raise ValueError("checks, checkTwos, and indices must all be the same length.")
        
        results = []
        for check, checkTwo, idx in zip(checks, checkTwos, indices):
            result = self.linesplitter(lines, check, checkTwo, idx)
            results.append(result)
        return results
    
    # Extracts key structural results from the raw SPOOKS output using defined headers and offsets
    def parse_result_variables(self,ExecuteOutput):
        checkArr = ['ENCASTRE LEVEL', 'ENCASTRE MOMENT', 'LEVEL OF YIELD HINGE', 'MOMENT IN YIELD HINGE', 'FOOT LEVEL', 'ANCHOR FORCE', 'MOMENT AT ANCHOR']
        checkTwoArr = [None, None, None, None, 'LEVEL OF FOOT', None, None]
        iArr = [-1,-2,-1,-2,-1,-4,-2]
        return self.linesplitterMult(ExecuteOutput.get('SPOOKSOutput'), checkArr, checkTwoArr, iArr)

    # Reads the SPOOKS plot file (usually a text file) and returns a list of its lines
    def read_plot_file_lines(self,ExecuteOutput):
        with open(ExecuteOutput.get('SPOOKSPlotFile'), 'r') as f:
            return f.readlines()

    # Isolates the section of the file that contains earth pressure data
    def extract_earth_pressure_block(lines):
        index_header = next(i for i, line in enumerate(lines) if 'Kote' in line)
        index_empty = [i for i, line in enumerate(lines) if line.isspace() and i > index_header]

        boundary_low = index_empty[0] if index_empty else len(lines)
        return lines[index_header:boundary_low]

    # Parses the earth pressure block and organizes data into arrays
    def parse_earth_pressure_block(block_lines):
        EarthPressureResults = np.empty((0, 8), int)  # Raw matrix of all values

        # Initialize empty lists for individual result columns
        level_graphic, e1_graphic, e2_graphic = [], [], []
        dw_graphic, enet_graphic = [], []
        shearforce, shearlevel = [], []
        moment, momentlevel = [], []
        ju_graphic = []

        for line in block_lines:
            if 'T' in line:  # Skip header row
                continue

            # Split line into values and reshape to keep as row vector
            splitstrings = np.array(line.split()).reshape((1, -1))
            EarthPressureResults = np.append(EarthPressureResults, splitstrings, axis=0)

            # Parse and assign each value to its corresponding array
            level = float(splitstrings[:, 0])
            level_graphic.append(level)
            e1_graphic.append(float(splitstrings[:, 1]) * -1)  # Negate for graph orientation
            e2_graphic.append(float(splitstrings[:, 2]))
            dw_graphic.append(float(splitstrings[:, 3]))
            enet_graphic.append(float(splitstrings[:, 4]))

            shear = float(splitstrings[:, 5])
            moment_val = float(splitstrings[:, 6])
            ju_val = float(splitstrings[:, 7])

            shearforce.append(shear)
            shearlevel.append(level)
            moment.append(moment_val)
            momentlevel.append(level)
            ju_graphic.append(ju_val)

        return (
            EarthPressureResults,
            level_graphic, e1_graphic, e2_graphic,
            dw_graphic, enet_graphic,
            shearforce, shearlevel,
            moment, momentlevel,
            ju_graphic
        )

    # Computes maximum shear and moment values along with their corresponding levels
    def compute_extreme_forces(shearforce, shearlevel, moment, momentlevel):
        maxshear = max(shearforce, key=abs)
        shear_index = shearforce.index(maxshear)
        maxshearlevel = shearlevel[shear_index]

        maxmom = max(moment, key=abs)
        moment_index = moment.index(maxmom)
        maxmomlvl = momentlevel[moment_index]

        return maxshear, maxshearlevel, maxmom, maxmomlvl

    def safe_float(val, default=None, precision=2):
        try:
            return float(format(float(val), f'.{precision}f'))
        except (ValueError, TypeError):
            return default