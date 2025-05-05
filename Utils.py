import pandas as pd

class Utils:

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

    ###### This function normalizes the soil profile generation
    def soilprofiles(name, Stratification, SoilProfiles, ilocrange, i):
        #### Soil profile X
        SoilProfile = name
        ## Soil stratigraphy front
        if pd.isnull(Stratification.iloc[ilocrange[0],ilocrange[1]]) == True: ## if no value entered in slope -> value is 0
            Stratification.iloc[ilocrange[0],ilocrange[1]] = 0.00
        
        SoilProfiles[SoilProfile]['Front']['Slope'] = float(format(Stratification.iloc[ilocrange[0],ilocrange[1]], '.2f'))

        ## Start of front stratigraphy layers soil profile 1
        index_start = [k for k, j in enumerate(Stratification.iloc[:,0]) if j == 'Front']
        index_start = index_start[i]
        ## end of front stratigraphy layers soil profile 1
        index_end = [k for k, j in enumerate(Stratification.iloc[:,1]) if j == None and k > index_start]
        if not index_end:
            index_end = [k for k, j in enumerate(Stratification.iloc[:,0]) if j == 10 and k > index_start]
        else:
            index_end = index_end[0]
        
        return_arr = [SoilProfile,'Front',index_start, index_end, SoilProfiles,Stratification]
        return return_arr

    def AppendToSoilProfiles(SoilProfile,Side,index_start, index_end, SoilProfiles,Stratification):
        
        for x in range(index_start+2,index_end):
        
            SoilLayer = {'TopLayer': None,
                        'Gamma_d': None,
                        'Gamma_m': None,
                        'cu': None,
                        'c': None,
                        'phi': None,
                        'i': None,
                        'r': None,
                        'Description': None,
                        'KeepDrained': None}
            
        
            SoilLayer['TopLayer'] = float(format(Stratification.iloc[x,1], '.2f'))
            SoilLayer['Gamma_d'] =  float(format(Stratification.iloc[x,2], '.2f'))
            SoilLayer['Gamma_m'] =  float(format(Stratification.iloc[x,3], '.2f'))
            SoilLayer['cu'] =       float(format(Stratification.iloc[x,4], '.2f'))
            SoilLayer['c'] =        float(format(Stratification.iloc[x,5], '.2f'))
            SoilLayer['phi'] =      float(format(Stratification.iloc[x,6], '.2f'))
            SoilLayer['i'] =        float(format(Stratification.iloc[x,7], '.2f'))
            SoilLayer['r'] =        float(format(Stratification.iloc[x,8], '.2f'))
            SoilLayer['Description'] = Stratification.iloc[x,9]
            SoilLayer['KeepDrained'] = Stratification.iloc[x,10]

        
            ## Append to soil profile dictionary
            
        
            SoilProfiles.get(SoilProfile).get(Side).get('Layers').append(SoilLayer)
