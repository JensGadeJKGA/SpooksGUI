import numpy as np
import pandas as pd

from SoilProfiles import soilprofiles
from Utils import Utils

class Analysisclass():
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
                        


    def AddDesignParameters(GeneratedAnalyses,LoadComb):
        from Analysis import Analysisclass
        
        LoadCombinations = GeneratePartialCoefficientDictionary(LoadComb)
        
        
        for Analysis in GeneratedAnalyses:
        
            ConsequenceClass = Analysis.get('ConsequenceClass')
            LoadCombination = Analysis.get('LoadCombination')
            Alpha = float(Analysis.get('Alpha'))
            SoilLayersBack = Analysis.get('SoilLayersBack')
            SoilLayersFront = Analysis.get('SoilLayersFront')
            LoadFront = Analysis.get('LoadFront')
            LoadBack = Analysis.get('LoadBack')
            WaterDensity = Analysis.get('WaterDensity')
            AddPress_ez = Analysis.get('AddPress_ez')
            
            
            DesignSoilLayersBack = []
            DesignSoilLayersFront = []
            
            PartialSafetyFactors = LoadCombinations.get(ConsequenceClass).get(LoadCombination)
            
            
            
            ###################### SOILS #######################################
            
            
            ## Generate design soil layers (back)
            Analysis['DesignSoilLayersBack'] = Analysisclass.SoilLayerAnalysis(SoilLayersBack, PartialSafetyFactors, Analysis, 'DesignSoilLayersBack')
            
            
            ## Generate design soil layers (front)
            Analysis['DesignSoilLayersFront'] = Analysisclass.SoilLayerAnalysis(SoilLayersFront, PartialSafetyFactors, Analysis, 'DesignSoilLayersFront')
            
            
            
            
            ###################### ADDITIONAL PRESSURE ##########################  
            
            DesignAddPress_ez = []
            
            for ez in AddPress_ez:
                
                DesignAddPress_ez.append(float(ez)*float(PartialSafetyFactors.get('f_AP')))
                
            
            Analysis['DesignAddPress_ez'] = DesignAddPress_ez
            
            
            ################## LOADS AND WATER DENSITY ###########################
            
            Analysis['DesignLoadFront'] = float(LoadFront)*float(PartialSafetyFactors.get('f_qf'))
            Analysis['DesignLoadBack'] = float(LoadBack)*float(PartialSafetyFactors.get('f_qb'))
            Analysis['DesignWaterDensity'] = float(WaterDensity)*float(PartialSafetyFactors.get('f_wat'))
            Analysis['PartialSafetyFactors'] = PartialSafetyFactors
        
        

    def GenerateAnalyses(input_path):
        
        ## Importing Excel file
        ImportData = ImportExcel(input_path)
        
        InputFileID = ImportData.get('InputFileID')
        Analyses = ImportData.get('Analyses')
        Water = ImportData.get('Water')
        Wall = ImportData.get('Wall')
        Stratification = ImportData.get('Stratification')
        SoilProfiles = soilprofiles.GenerateSoilProfiles(Stratification)
        Add_pres = ImportData.get('AddPress')
        AdditionalPressures = Utils.GenerateAddPressProfiles(Add_pres)
        LoadComb = ImportData.get('LoadComb')
        SheetPileAddOn = ImportData.get('SheetPileAddOn')
        
        
        ## Check if input file version matches GUI version
        InputFileStatus = Utils.InputFileIDChecker(InputFileID)
        
        if InputFileStatus == 'OK':
            print("OK")
        
            ## List holding analyses (output)
            GeneratedAnalyses = []
            ## Initial analysis number
            AnalysisNo = 0
            ## Parent analysis (Referring to Excel input file)
            ParentAnalysis = 0
            
            ## Project
            Project = str(ImportData.get('GeneralInfo').iloc[0,1])
            ## Initials
            Initials = str(ImportData.get('GeneralInfo').iloc[2,1])
            ## Checker
            Checker = str(ImportData.get('GeneralInfo').iloc[3,1])
            ## Approver
            Approver = str(ImportData.get('GeneralInfo').iloc[4,1])
            ## Water density
            gamma_water = WaterDensity(Water)
            ## Wall parameters
            WallParams = WallParameters(Wall)
            WallMass = WallParams.get('Mass')
            TopWall = WallParams.get('zT')
            
            ### Sheet pile add on
            SheetPileAddOnInput = Utils.GenerateSheetPileAddOnInput(SheetPileAddOn)
        
            
            
            ### Ranges of analyses
            RangeOfAnalyses = AnalysesRange(Analyses)
            print(RangeOfAnalyses)
            MinAnalysis = RangeOfAnalyses.get('MinAnalysis')
            MaxAnalysis = RangeOfAnalyses.get('MaxAnalysis')
        
        
            ### Defining correct number of decimals for integers and floating numbers
            for Analysis in range(MinAnalysis,MaxAnalysis):
                for i in range(0, len(Analyses.iloc[Analysis,:])):
                
                    if isinstance(Analyses.iloc[Analysis,i], int) == True or isinstance(Analyses.iloc[Analysis,i], float) == True:  ## add relevant number of decimals if 'i' is integer
                        Analyses.iloc[Analysis,i] = float(format(Analyses.iloc[Analysis,i], '.2f'))
                                
            
            ### Generating analyses
            for Analysis in range(MinAnalysis,MaxAnalysis):
                
                
                ### King Post Wall data
                zB = Analyses.iloc[Analysis,21]
                WD = Analyses.iloc[Analysis,22]
                CC = Analyses.iloc[Analysis,23]
                
                if isinstance(zB,(int,float)) == False or isinstance(WD,(int,float)) == False or isinstance(CC,(int,float)) == False:
                    
                    zB = None
                    WD = None
                    CC = None
                
                
                ## If anchor input is present
                if isinstance(Analyses.iloc[Analysis,16],(int,float)):
                    print(1)
                    AInclination = Analyses.iloc[Analysis,19]
                    
                    PrescrbAnchorForce = Analyses.iloc[Analysis,20]
                    
                    ## If no anchor inclination data is entered inclination is set to 0.00 degrees
                    if isinstance(AInclination,(int,float)) == False:
                        
                        AInclination = 0.00
                        
                    ## If no prescribed anchor force data is entered inclination is set to 0.00 degrees
                    if isinstance(PrescrbAnchorForce,(int,float)) == False:
                        
                        PrescrbAnchorForce = 0.00
                    
                    ## If input is setup for anchor level range analysis
                    if Analyses.iloc[Analysis,16] != Analyses.iloc[Analysis,17] and Analyses.iloc[Analysis,18] != None: ## checking anchor data (Alvl_min, Alvl_max and Astep)
                        print(1.1)
                        
                        ## Generate analysis for all anchor level steps
                        for AnchorLevel in np.arange(Analyses.iloc[Analysis,16],
                                                    Analyses.iloc[Analysis,17]+Analyses.iloc[Analysis,18],
                                                    Analyses.iloc[Analysis,18]):
                
                
                            Analysis_dict = {'AnalysisNo': AnalysisNo,
                                            'ParentAnalysis': ParentAnalysis,
                                            'Project': Project,
                                            'Initials': Initials,
                                            'Checker': Checker,
                                            'Approver': Approver,
                                            'Subject': Analyses.iloc[Analysis,0],
                                            'SoilProfile': Analyses.iloc[Analysis,1],
                                            'SlopeBack': None,
                                            'SlopeFront': None,
                                            'SoilLayersFront': [],
                                            'SoilLayersBack': [],
                                            'zT': float(TopWall),
                                            'WallMass': float(WallMass),
                                            'WaterDensity': float(gamma_water),
                                            'AddPressureProfile': Analyses.iloc[Analysis,11],
                                            'AddPress_z': [],
                                            'AddPress_ez': [],
                                            'State': Analyses.iloc[Analysis,2],
                                            'WaterLevelFront': float(Analyses.iloc[Analysis,3]),
                                            'WaterLevelBack': float(Analyses.iloc[Analysis,4]),
                                            'WDiff': abs(float(Analyses.iloc[Analysis,4])-float(Analyses.iloc[Analysis,4])),
                                            'LoadCombination': Analyses.iloc[Analysis,5],
                                            'ConsequenceClass': Analyses.iloc[Analysis,6],
                                            'Alpha': float(Analyses.iloc[Analysis,7]),
                                            'LoadFront': float(Analyses.iloc[Analysis,8]),
                                            'LoadBack': float(Analyses.iloc[Analysis,9]),
                                            'LevelLoadBack': float(Analyses.iloc[Analysis,10]),
                                            'AxialWallLoad': float(Analyses.iloc[Analysis,12]),
                                            'iA': float(Analyses.iloc[Analysis,13]),
                                            'iB': float(Analyses.iloc[Analysis,14]),
                                            'iC': float(Analyses.iloc[Analysis,15]),
                                            'AnchorLevel': float(AnchorLevel),
                                            'AnchorInclination': float(AInclination),
                                            'PrescrbAnchorForce': float(PrescrbAnchorForce),
                                            'zB': zB,
                                            'WD': WD,
                                            'CC': CC,
                                            'KN': Analyses.iloc[Analysis,24],
                                            'KP': Analyses.iloc[Analysis,25],
                                            'SC': Analyses.iloc[Analysis,26],
                                            'SheetPileAddOnInput': SheetPileAddOnInput}
                            
                            print(Analysis_dict)
                            
                            ## Append to analyses list
                            GeneratedAnalyses.append(Analysis_dict)
                                    
                            ## Update analysis number
                            AnalysisNo = AnalysisNo + 1
                            
        
                    else:
                        print(1.2)
                        Analysis_dict = {'AnalysisNo': AnalysisNo,
                                        'ParentAnalysis': ParentAnalysis,
                                        'Project': Project,
                                        'Initials': Initials,
                                        'Checker': Checker,
                                        'Approver': Approver,
                                        'Subject': Analyses.iloc[Analysis,0],
                                        'SoilProfile': Analyses.iloc[Analysis,1],
                                        'SlopeBack': None,
                                        'SlopeFront': None,
                                        'SoilLayersFront': [],
                                        'SoilLayersBack': [],
                                        'zT': float(TopWall),
                                        'WallMass': float(WallMass),
                                        'WaterDensity': float(gamma_water),
                                        'AddPressureProfile': Analyses.iloc[Analysis,11],
                                        'AddPress_z': [],
                                        'AddPress_ez': [],
                                        'State': Analyses.iloc[Analysis,2],
                                        'WaterLevelFront': float(Analyses.iloc[Analysis,3]),
                                        'WaterLevelBack': float(Analyses.iloc[Analysis,4]),
                                        'WDiff': abs(float(Analyses.iloc[Analysis,4])-float(Analyses.iloc[Analysis,4])),
                                        'LoadCombination': Analyses.iloc[Analysis,5],
                                        'ConsequenceClass': Analyses.iloc[Analysis,6],
                                        'Alpha': float(Analyses.iloc[Analysis,7]),
                                        'LoadFront': float(Analyses.iloc[Analysis,8]),
                                        'LoadBack': float(Analyses.iloc[Analysis,9]),
                                        'LevelLoadBack': float(Analyses.iloc[Analysis,10]),
                                        'AxialWallLoad': float(Analyses.iloc[Analysis,12]),
                                        'iA': float(Analyses.iloc[Analysis,13]),
                                        'iB': float(Analyses.iloc[Analysis,14]),
                                        'iC': float(Analyses.iloc[Analysis,15]),
                                        'AnchorLevel': float(Analyses.iloc[Analysis,16]),
                                        'AnchorInclination': float(AInclination),
                                        'PrescrbAnchorForce': float(PrescrbAnchorForce),
                                        'zB': zB,
                                        'WD': WD,
                                        'CC': CC,
                                        'KN': Analyses.iloc[Analysis,24],
                                        'KP': Analyses.iloc[Analysis,25],
                                        'SC': Analyses.iloc[Analysis,26],
                                        'SheetPileAddOnInput': SheetPileAddOnInput}
                        print(Analysis_dict)
                        ## Append to analyses list
                        GeneratedAnalyses.append(Analysis_dict)
                                
                        ## Update analysis number
                        AnalysisNo = AnalysisNo + 1
                else:        
                    print(2)
                    Analysis_dict = {'AnalysisNo': AnalysisNo,
                                    'ParentAnalysis': ParentAnalysis,
                                    'Project': Project,
                                    'Initials': Initials,
                                    'Checker': Checker,
                                    'Approver': Approver,
                                    'Subject': Analyses.iloc[Analysis,0],
                                    'SoilProfile': Analyses.iloc[Analysis,1],
                                    'SlopeBack': None,
                                    'SlopeFront': None,
                                    'SoilLayersFront': [],
                                    'SoilLayersBack': [],
                                    'zT': float(TopWall),
                                    'WallMass': float(WallMass),
                                    'WaterDensity': float(gamma_water),
                                    'AddPressureProfile': Analyses.iloc[Analysis,11],
                                    'AddPress_z': [],
                                    'AddPress_ez': [],
                                    'State': Analyses.iloc[Analysis,2],
                                    'WaterLevelFront': float(Analyses.iloc[Analysis,3]),
                                    'WaterLevelBack': float(Analyses.iloc[Analysis,4]),
                                    'WDiff': abs(float(Analyses.iloc[Analysis,4])-float(Analyses.iloc[Analysis,4])),
                                    'LoadCombination': Analyses.iloc[Analysis,5],
                                    'ConsequenceClass': Analyses.iloc[Analysis,6],
                                    'Alpha': float(Analyses.iloc[Analysis,7]),
                                    'LoadFront': float(Analyses.iloc[Analysis,8]),
                                    'LoadBack': float(Analyses.iloc[Analysis,9]),
                                    'LevelLoadBack': float(Analyses.iloc[Analysis,10]),
                                    'AxialWallLoad': float(Analyses.iloc[Analysis,12]),
                                    'iA': float(Analyses.iloc[Analysis,13]),
                                    'iB': float(Analyses.iloc[Analysis,14]),
                                    'iC': float(Analyses.iloc[Analysis,15]),
                                    'AnchorLevel': None,
                                    'AnchorInclination': None,
                                    'PrescrbAnchorForce': None,
                                    'zB': zB,
                                    'WD': WD,
                                    'CC': CC,
                                    'KN': Analyses.iloc[Analysis,24],
                                    'KP': Analyses.iloc[Analysis,25],
                                    'SC': Analyses.iloc[Analysis,26],
                                    'SheetPileAddOnInput': SheetPileAddOnInput}
                
                    print(Analysis_dict)
                            
                    ## Append to analyses list
                    GeneratedAnalyses.append(Analysis_dict)
                                
                    ## Update analysis number
                    AnalysisNo = AnalysisNo + 1
                
                ## Update parent analysis number
                ParentAnalysis = ParentAnalysis + 1    
            
            
            ## Append soil layers data to analysis dictionary
            AddSoilToAnalysis(GeneratedAnalyses,SoilProfiles)
            
            ## Append soil layers data to analysis dictionary
            AddPressureToAnalysis(GeneratedAnalyses,AdditionalPressures)
            
            ## Append design soil layers
            AddDesignParameters(GeneratedAnalyses,LoadComb)
            
            
        
            return GeneratedAnalyses
    
    def SoilLayerAnalysis(SoilLayers, PartialSafetyFactors, Analysis, Analysisspot):
        DesignSoilLayers = None
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