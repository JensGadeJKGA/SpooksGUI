import pandas as pd
from SpooksHelperLib.Utils import utils
import numpy as np


### In this file you will find the function generate soil profiles and the function to append them. 


###### This function normalizes the soil profile generation
class soilprofiles():
    def soilprofiles(name, Stratification, SoilProfiles, ilocrange, i, side):

        SoilProfile = name

        # If slope cell is empty, set to 0.00
        if pd.isnull(Stratification.iloc[ilocrange[0], ilocrange[1]]):
            Stratification.iloc[ilocrange[0], ilocrange[1]] = 0.00

        # Save slope to the correct side
        SoilProfiles[SoilProfile][side]['Slope'] = utils.safe_float(
            Stratification.iloc[ilocrange[0], ilocrange[1]]
        )

        # Find start index for this side's layers
        index_start_list = [k for k, j in enumerate(Stratification.iloc[:, 0]) if j == side]
        if i >= len(index_start_list):
            raise IndexError(f"No {side} section found for profile {SoilProfile} at index {i}")
        index_start = index_start_list[i]

        # Find end index for layers
        index_end_list = [k for k, j in enumerate(Stratification.iloc[:, 1])
                        if j is None and k > index_start]
        if not index_end_list:
            index_end_list = [k for k, j in enumerate(Stratification.iloc[:, 0])
                            if j == 10 and k > index_start]
        index_end = index_end_list[0] if index_end_list else len(Stratification)
        
        return SoilProfile, side, index_start, index_end, SoilProfiles, Stratification
        


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
                
            
            SoilLayer['TopLayer'] = float(format(utils.floatify(Stratification.iloc[x,1]), '.2f'))
            SoilLayer['Gamma_d'] =  float(format(utils.floatify(Stratification.iloc[x,2]), '.2f'))
            SoilLayer['Gamma_m'] =  float(format(utils.floatify(Stratification.iloc[x,3]), '.2f'))
            SoilLayer['cu'] =       float(format(utils.floatify(Stratification.iloc[x,4]), '.2f'))
            SoilLayer['c'] =        float(format(utils.floatify(Stratification.iloc[x,5]), '.2f'))
            SoilLayer['phi'] =      float(format(utils.floatify(Stratification.iloc[x,6]), '.2f'))
            SoilLayer['i'] =        float(format(utils.floatify(Stratification.iloc[x,7]), '.2f'))
            SoilLayer['r'] =        float(format(utils.floatify(Stratification.iloc[x,8]), '.2f'))
            SoilLayer['Description'] = Stratification.iloc[x,9]
            SoilLayer['KeepDrained'] = Stratification.iloc[x,10]

            
            ## Append to soil profile dictionary
            SoilProfiles.get(SoilProfile).get(Side).get('Layers').append(SoilLayer)

    def designsoillayer(DesignSoilLayers, State, L):
        for Layer in DesignSoilLayers:  # creates lines for soil on front
            
            if State.lower() == 'undrained' and Layer.get('KeepDrained') == 'No':
            
                S_temp = [format(Layer.get('TopLayer'),'.2f'), 
                        format(Layer.get('Gamma_d'),'.2f'), 
                        format(Layer.get('Gamma_m'),'.2f'), 
                        format(Layer.get('i'),'.2f'), 
                        '0.00',
                        format(Layer.get('cu'),'.2f'), 
                        format(Layer.get('r'),'.2f')]
            
            elif State.lower() == 'drained' or Layer.get('KeepDrained') == 'Yes':
                
                S_temp = [format(Layer.get('TopLayer'),'.2f'), 
                        format(Layer.get('Gamma_d'),'.2f'), 
                        format(Layer.get('Gamma_m'),'.2f'), 
                        format(Layer.get('i'),'.2f'),
                        format(Layer.get('phi'),'.2f'), 
                        format(Layer.get('c'),'.2f'), 
                        format(Layer.get('r'),'.2f')]
                
        
            Soil = ""
        
            Soil = utils.AddSpaces(S_temp)
            L.append(Soil)
        
        L.append('>')
        L.append('<')

        return L