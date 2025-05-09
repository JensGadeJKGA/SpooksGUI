import pandas as pd
import numpy as np

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