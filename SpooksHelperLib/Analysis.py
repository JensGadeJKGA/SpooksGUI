import numpy as np
import pandas as pd

from SpooksHelperLib.SoilProfiles import soilprofiles
from SpooksHelperLib.Utils import utils


class analysisclass():
    def __init__(self):
         pass
    
    def AnalysesRange(Analyses):
        null = []
        # This loop aims for the first cell in which the user hasn't entered data in the following order (0: Subject text, 1: Soil profile, 2: Drained or undrained, 3: water front level, 4: water back level, 5: load comb, 6: consequence class, 7: alpha value, 8: front load value, 9: back load value, 10: zR value, 11 is missing, 12: iA value, 13: also iA value, 14: iC value)
        for i in range(15):
            if i != 11:
                null[i] = np.amin(np.where(pd.isnull(Analyses.iloc[:,i])))
            else:
                null[i] = None

        
        ### Overall first row (analysis row) with incomplete data.
        index_maxAnalysis = min(*null)
        
        RangeOfAnalyses = {'MinAnalysis': 2,
                        'MaxAnalysis': index_maxAnalysis}
        
        return RangeOfAnalyses

    
    def AddSoilToAnalysis(GeneratedAnalyses,SoilProfiles):
        
        ## Loop through all generated analyses and append stratigraphy input
        for Analysis in GeneratedAnalyses:
            
            SoilProfile = Analysis.get('SoilProfile')
            
            ## Find analysis soil profile in SoilProfiles
            SP = SoilProfiles.get(SoilProfile)
            
            ## Append slope back
            Analysis['SlopeBack'] = SP.get('Back').get('Slope')
            
            ## Append slope front
            Analysis['SlopeFront'] = SP.get('Front').get('Slope')
            
            ## Append soil profile properties (back)
            for SoilLayer in SP.get('Back').get('Layers'):
            
                    Analysis.get('SoilLayersBack').append(SoilLayer)
                    
            ## Append soil profile properties (front)
            for SoilLayer in SP.get('Front').get('Layers'):
            
                    Analysis.get('SoilLayersFront').append(SoilLayer)
        


    def AddPressureToAnalysis(GeneratedAnalyses,AdditionalPressures):
        
        ## Loop through all generated analyses and append stratigraphy input
        for Analysis in GeneratedAnalyses:
            
            APProfile = Analysis.get('AddPressureProfile')
            
            ## If any of the possible additional pressure profiles is specified
            if APProfile != None:
                
                ## Additional pressure profile
                APProfile = AdditionalPressures.get(APProfile)
            
                ## Append AP levels
                for Level in APProfile.get('z'):
                
                        Analysis.get('AddPress_z').append(Level)
                
                ## Append AP pressures
                for Pressure in APProfile.get('ez'):
                
                        Analysis.get('AddPress_ez').append(Pressure)
                        


    def AddDesignParameters(self,GeneratedAnalyses,LoadComb):
        
        LoadCombinations = utils.GeneratePartialCoefficientDictionary(LoadComb)
        
        
        for Analysis in GeneratedAnalyses:
            PartialSafetyFactors = LoadCombinations.get(Analysis.get('ConsequenceClass')).get(Analysis.get('LoadCombination'))
            
            #Soils
            ## Generate design soil layers (back)
            Analysis['DesignSoilLayersBack'] = self.SoilLayerAnalysis(Analysis.get('SoilLayersBack'), PartialSafetyFactors, Analysis, 'DesignSoilLayersBack')
            
            
            ## Generate design soil layers (front)
            Analysis['DesignSoilLayersFront'] = self.SoilLayerAnalysis(Analysis.get('SoilLayersFront'), PartialSafetyFactors, Analysis, 'DesignSoilLayersFront')
            
            #Additional pressure 
            DesignAddPress_ez = []
            
            for ez in Analysis.get('AddPress_ez'):
                DesignAddPress_ez.append(float(ez)*float(PartialSafetyFactors.get('f_AP')))
                
            Analysis['DesignAddPress_ez'] = DesignAddPress_ez
            
            #Loads and water density
            Analysis['DesignLoadFront'] = float(Analysis.get('LoadFront'))*float(PartialSafetyFactors.get('f_qf'))
            Analysis['DesignLoadBack'] = float(Analysis.get('LoadBack'))*float(PartialSafetyFactors.get('f_qb'))
            Analysis['DesignWaterDensity'] = float(Analysis.get('WaterDensity'))*float(PartialSafetyFactors.get('f_wat'))
            Analysis['PartialSafetyFactors'] = PartialSafetyFactors
    
    def SoilLayerAnalysis(SoilLayers, PartialSafetyFactors, Analysis, Analysisspot):
        DesignSoilLayers = None
        Alpha = float(Analysis.get('Alpha'))
        
        for SoilLayer in SoilLayers:
                
            TopLayer = float(SoilLayer.get('TopLayer'))
            Gamma_d = float(SoilLayer.get('Gamma_d'))
            Gamma_m = float(SoilLayer.get('Gamma_m'))
            cu = float(SoilLayer.get('cu'))
            c = float(SoilLayer.get('c'))
            phi = float(SoilLayer.get('phi'))
            i = float(SoilLayer.get('i'))
            r = float(SoilLayer.get('r'))
            Description = SoilLayer.get('Description')
            KeepDrained = SoilLayer.get('KeepDrained')
                
                
            DesignSoilLayer = {'TopLayer': TopLayer,
                            'Gamma_d':  Gamma_d / (PartialSafetyFactors.get('f_gamb')**Alpha),
                            'Gamma_m':  Gamma_m / (PartialSafetyFactors.get('f_gamb')**Alpha),
                            'cu':       cu / (PartialSafetyFactors.get('f_cub')**Alpha),
                            'c':        c / (PartialSafetyFactors.get('f_cb')**Alpha),
                            'phi':      np.degrees(np.arctan(np.tan(np.radians(phi))/(PartialSafetyFactors.get('f_phib')**Alpha))),
                            'i':        i,
                            'r':        r,
                            'Description': Description,
                            'KeepDrained': KeepDrained}
                
            DesignSoilLayers.append(DesignSoilLayer)
            
        Analysis[Analysisspot] = DesignSoilLayers
        return Analysis[Analysisspot]
