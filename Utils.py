import pandas as pd
import numpy as np
from GUI_SPOOKSFunctions_2_0 import InputFileIDGUI, stat

###In this file you will find miscellaneous utility functions.

class Utils:
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
    
    def GenerateAddPressProfiles(Add_pres):
        
        AdditionalPressures = {'AP1':{'z': [],'ez':[]},
                            'AP2': {'z': [],'ez':[]},
                            'AP3': {'z': [],'ez':[]},
                            'AP4': {'z': [],'ez':[]},
                            'AP5': {'z': [],'ez':[]},
                            'AP6': {'z': [],'ez':[]},
                            'AP7': {'z': [],'ez':[]},
                            'AP8': {'z': [],'ez':[]},
                            'AP9': {'z': [],'ez':[]},
                            'AP10': {'z': [],'ez':[]}}
        
        #### APn
        for i in range(9):
            AdditionalPressures = Utils.AddPressProfiles(i+1, Add_pres, AdditionalPressures)
        
        return AdditionalPressures
    
    def GenerateSheetPileAddOnInput(SheetPileAddOn):
        
        UseAddOn = SheetPileAddOn.iloc[0,4]
        LimitState = SheetPileAddOn.iloc[3,6]
        ControlClass = SheetPileAddOn.iloc[4,6]
        KFI = SheetPileAddOn.iloc[5,6]
        Optimize = SheetPileAddOn.iloc[8,6]
        MaxUtilization = SheetPileAddOn.iloc[9,6]
        fyk = SheetPileAddOn.iloc[10,6]
        BetaB = SheetPileAddOn.iloc[11,6]
        BetaD = SheetPileAddOn.iloc[12,6]
        DesignLife = SheetPileAddOn.iloc[15,6]
        tCor = list(SheetPileAddOn.iloc[17:27,6])
        tCorLevel = list(SheetPileAddOn.iloc[17:27,0])
        SoilDeposit = SheetPileAddOn.iloc[29,6]
        
        
        
        SheetPileAddOnInput = {'UseAddOn': UseAddOn,
                            'LimitState': LimitState,
                            'ControlClass': ControlClass,
                            'KFI': KFI,
                            'Optimize': Optimize,
                            'MaxUtilization': MaxUtilization,
                            'fyk': fyk,
                            'BetaB': BetaB,
                            'BetaD': BetaD,
                            'DesignLife': DesignLife,
                            'tCor': tCor,
                            'tCorLevel': tCorLevel,
                            'SoilDeposit': SoilDeposit}
        
        return SheetPileAddOnInput