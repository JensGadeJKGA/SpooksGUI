import pandas as pd
import numpy as np

from GUI_SPOOKSFunctions_2_0 import InputFileIDGUI, stat
from SpooksHelperLib.Generators import generators

###In this file you will find miscellaneous utility functions.

class utils:
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

    def InputFileIDChecker(InputFileID):        
        InputFileStatus = None
        
        if InputFileID == InputFileIDGUI:
            
            InputFileStatus = 'OK'
            
        else:
            
            stat.configure(text = 'Input file version does not match GUI version')
            
        return InputFileStatus


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

    def PartialSafetyFactors(LoadComb, loadcombinations, cc):
        index_CC2 = np.where((LoadComb.iloc[:,0]) == 'CC2')
        index_CC2 = index_CC2[0][0]
        index_CC3 = np.where((LoadComb.iloc[:,0]) == 'CC3')
        index_CC3 = index_CC3[0][0]
        
        for i in range(index_CC2+2,index_CC3):
            if LoadComb.iloc[i,0] != None:
                Loadcombination = LoadComb.iloc[i,0]

                            
                PartialSafetyFactors = {'f_gamf': float(LoadComb.iloc[i,1]),
                                        'f_qf':   float(LoadComb.iloc[i,2]),
                                        'f_cf':   float(LoadComb.iloc[i,3]),
                                        'f_cuf':  float(LoadComb.iloc[i,4]),
                                        'f_phif': float(LoadComb.iloc[i,5]),
                                        'f_wat':  float(LoadComb.iloc[i,6]),
                                        'f_AP':   float(LoadComb.iloc[i,7]),
                                        'f_gamb': float(LoadComb.iloc[i,8]),
                                        'f_qb':   float(LoadComb.iloc[i,9]),
                                        'f_cb':   float(LoadComb.iloc[i,10]),
                                        'f_cub':  float(LoadComb.iloc[i,11]),
                                        'f_phib': float(LoadComb.iloc[i,12])}
                
                loadcombinations.get(cc)[str(Loadcombination)] = PartialSafetyFactors
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
                    'GeneralInfo': docready_array[1],
                    'Stratification': docready_array[2],
                    'Wall': docready_array[3],
                    'Water': docready_array[4],
                    'AddPress': docready_array[5],
                    'Analyses': docready_array[6],
                    'LoadComb': docready_array[7],
                    'SheetPileAddOn': docready_array[8]}
    
    

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
    
    
    def GeneratePartialCoefficientDictionary(LoadComb):
        LoadCombinations = {'CC2': {},
                            'CC3': {}}
                
        ### Find CC2 partial safety factors
        LoadCombinations.get('CC2') = utils.PartialSafetyFactors(LoadComb, LoadCombinations, 'CC2')
            
        ### Find CC3 partial safety factors
        LoadCombinations.get('CC3') = utils.PartialSafetyFactors(LoadComb, LoadCombinations, 'CC3')

    def make_analysis_dict(Analyses, Analysis, ImportData, anchor_level, anchor_inclination, prescribed_anchor_force, vararr, geninfoarr):
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
                'SheetPileAddOnInput': generators.GenerateSheetPileAddOnInput(ImportData.get('SheetPileAddOn'))
            }
