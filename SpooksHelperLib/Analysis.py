import numpy as np
import pandas as pd

from SpooksHelperLib.SoilProfiles import soilprofiles
from SpooksHelperLib.Utils import utils


class analysisclass():
    def __init__(self):
         pass
    
    def AnalysesRange(Analyses):
        null = []
        for i in range(15):
            if i != 11:
                try:
                    # Find first row with null in column i
                    first_null = np.amin(np.where(pd.isnull(Analyses.iloc[:, i])))
                except ValueError:
                    # No nulls found — assume end of DataFrame is valid
                    first_null = len(Analyses)
                null.append(first_null)
            else:
                null.append(None)

        # Get the minimum valid analysis index
        filtered_nulls = [val for val in null if val is not None]
        index_maxAnalysis = min(filtered_nulls)

        RangeOfAnalyses = {
            'MinAnalysis': 2,
            'MaxAnalysis': index_maxAnalysis
        }

        return RangeOfAnalyses


    
    def AddSoilToAnalysis(self,GeneratedAnalyses,SoilProfiles):
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
            
        return GeneratedAnalyses
        

        


    def AddPressureToAnalysis(self,GeneratedAnalyses,AdditionalPressures):
        
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
        
        return GeneratedAnalyses


    def AddDesignParameters(self, GeneratedAnalyses, LoadComb):
        LoadCombinations = {'CC2': {},
                            'CC3': {}}
        LoadCombinatione = utils.PartialSafetyFactors(LoadComb, LoadCombinations)

        for analysis in GeneratedAnalyses:
            cc = analysis.get('ConsequenceClass')
            lc_raw = analysis.get('LoadCombination')
            
            # Clean the LoadCombination string
            lc = str(lc_raw).strip()
            PartialSafetyFactors = LoadCombinatione.get(cc).get(lc)

            # Get the consequence class dictionary
            partial_class = LoadCombinations.get(cc)

            if partial_class is None:
                raise ValueError(f"Unknown ConsequenceClass: {cc}")

            # Try exact match first
            #PartialSafetyFactors = partial_class.get(lc)

            # If not found, try case-insensitive & strip match
            if PartialSafetyFactors is None:
                for key in partial_class.keys():
                    if key.strip().lower() == lc.lower():
                        PartialSafetyFactors = partial_class[key]
                        break

            # If still not found, raise error
            if PartialSafetyFactors is None:
                raise ValueError(f"No PartialSafetyFactors found for ConsequenceClass={cc} and LoadCombination={lc}")

            alpha = float(analysis.get('Alpha'))

            # --- SOILS ---
            analysis['DesignSoilLayersBack'] = self.SoilLayerAnalysisBack(
                analysis.get('SoilLayersBack'), PartialSafetyFactors, alpha
            )
            analysis['DesignSoilLayersFront'] = self.SoilLayerAnalysisFront(
                analysis.get('SoilLayersFront'), PartialSafetyFactors, alpha
            )

            # --- ADDITIONAL PRESSURE ---
            analysis['DesignAddPress_ez'] = [
                float(ez) * float(PartialSafetyFactors.get('f_AP'))
                for ez in analysis.get('AddPress_ez')
            ]

            # --- LOADS & WATER DENSITY ---
            analysis['DesignLoadFront'] = float(analysis.get('LoadFront')) * float(PartialSafetyFactors.get('f_qf'))
            analysis['DesignLoadBack'] = float(analysis.get('LoadBack')) * float(PartialSafetyFactors.get('f_qb'))
            analysis['DesignWaterDensity'] = float(analysis.get('WaterDensity')) * float(PartialSafetyFactors.get('f_wat'))

            # Store the partial safety factors for reference
            analysis['PartialSafetyFactors'] = PartialSafetyFactors
        
        return GeneratedAnalyses



    def SoilLayerAnalysisBack(self, SoilLayers, PartialSafetyFactors, alpha):
        """Apply partial safety factors for BACK soil layers."""
        import numpy as np
        return [
            {
                'TopLayer': float(sl.get('TopLayer')),
                'Gamma_d':  float(sl.get('Gamma_d')) / (PartialSafetyFactors.get('f_gamb') ** alpha),
                'Gamma_m':  float(sl.get('Gamma_m')) / (PartialSafetyFactors.get('f_gamb') ** alpha),
                'cu':       float(sl.get('cu')) / (PartialSafetyFactors.get('f_cub') ** alpha),
                'c':        float(sl.get('c')) / (PartialSafetyFactors.get('f_cb') ** alpha),
                'phi':      np.degrees(np.arctan(np.tan(np.radians(float(sl.get('phi')))) /
                                                (PartialSafetyFactors.get('f_phib') ** alpha))),
                'i':        float(sl.get('i')),
                'r':        float(sl.get('r')),
                'Description': sl.get('Description'),
                'KeepDrained': sl.get('KeepDrained')
            }
            for sl in SoilLayers
        ]


    def SoilLayerAnalysisFront(self, SoilLayers, PartialSafetyFactors, alpha):
        """Apply partial safety factors for FRONT soil layers."""
        import numpy as np
        return [
            {
                'TopLayer': float(sl.get('TopLayer')),
                'Gamma_d':  float(sl.get('Gamma_d')) / (PartialSafetyFactors.get('f_gamf') ** alpha),
                'Gamma_m':  float(sl.get('Gamma_m')) / (PartialSafetyFactors.get('f_gamf') ** alpha),
                'cu':       float(sl.get('cu')) / (PartialSafetyFactors.get('f_cuf') ** alpha),
                'c':        float(sl.get('c')) / (PartialSafetyFactors.get('f_cf') ** alpha),
                'phi':      np.degrees(np.arctan(np.tan(np.radians(float(sl.get('phi')))) /
                                                (PartialSafetyFactors.get('f_phif') ** alpha))),
                'i':        float(sl.get('i')),
                'r':        float(sl.get('r')),
                'Description': sl.get('Description'),
                'KeepDrained': sl.get('KeepDrained')
            }
            for sl in SoilLayers
        ]

    
    def SoilLayerAnalysis(self, SoilLayers, PartialSafetyFactors, Analysis, Analysisspot):
        DesignSoilLayers = []
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
