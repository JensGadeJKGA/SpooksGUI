from SpooksHelperLib.SoilProfiles import soilprofiles
from SpooksHelperLib.Analysis import analysisclass
from SpooksHelperLib.Utils import utils
import numpy as np
        
class generators():
    def __init__(self):
        pass
    
    def GenerateAddPressProfiles(self,Add_pres):
        
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
            AdditionalPressures = utils.AddPressProfiles(i+1, Add_pres, AdditionalPressures)
        
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
    
    def GenerateSoilProfiles(self, Stratification):

        # Initialize the SoilProfiles dictionary
        SoilProfiles = {f'SP{i+1}': {'Back': {'Slope': None,'Layers': []}, 
                                    'Front': {'Slope': None,'Layers': []}} for i in range(10)}

        # Loop over front and back soils
        for side, col_index in [('Front', 5), ('Back', 2)]:
            for i in range(10):
                sp = f"SP{i+1}"
                # Get all info needed for AppendToSoilProfiles
                soilprofile_args = soilprofiles.soilprofiles(sp, Stratification, SoilProfiles, [29*i, col_index], i, side)
                # Append layers
                soilprofiles.AppendToSoilProfiles(*soilprofile_args)
                
        return SoilProfiles

    
   
    def GenerateAnalyses(self,input_path):
        u = utils()
        ## Importing Excel file
        ImportData = utils.ImportExcel(input_path)
        Analyses = ImportData.get('Analyses')

        ## Check if input file version matches GUI version
        InputFileStatus = u.InputFileIDChecker(ImportData.get('InputFileID'))

        if InputFileStatus == 'OK':
            print("OK")

            ## List holding analyses (output)
            GeneratedAnalyses = []
            geninfoarr = []
            ## Initial analysis number
            geninfoarr.append(0)  # geninfoarr[0]
            ## Parent analysis (Referring to Excel input file)
            geninfoarr.append(0)  # geninfoarr[1]

            ### Ranges of analyses
            RangeOfAnalyses = analysisclass.AnalysesRange(Analyses)
            
            print("Range of analyses: ",RangeOfAnalyses)
            MinAnalysis = RangeOfAnalyses.get('MinAnalysis')
            MaxAnalysis = RangeOfAnalyses.get('MaxAnalysis')
            u = utils()

            ### Defining correct number of decimals for integers and floating numbers
            for Analysis in range(MinAnalysis, MaxAnalysis):
                for i in range(0, len(Analyses.iloc[Analysis,:])):
                    if isinstance(Analyses.iloc[Analysis,i], (int, float)):
                        Analyses.iloc[Analysis,i] = float(format(Analyses.iloc[Analysis,i], '.2f'))

            ### Generating analyses
            for Analysis in range(MinAnalysis, MaxAnalysis):

                # Define vararr as dict instead of list
                vararr = {
                    'zB': Analyses.iloc[Analysis,21],
                    'WD': Analyses.iloc[Analysis,22],
                    'CC': Analyses.iloc[Analysis,23]
                }

                # Handle invalid values
                for key in vararr:
                    if not isinstance(vararr[key], (int, float)):
                        vararr[key] = None

                if isinstance(Analyses.iloc[Analysis,16], (int, float)):
                    AInclination = Analyses.iloc[Analysis,19]
                    PrescrbAnchorForce = Analyses.iloc[Analysis,20]

                    if not isinstance(AInclination, (int, float)):
                        AInclination = 0.00
                    if not isinstance(PrescrbAnchorForce, (int, float)):
                        PrescrbAnchorForce = 0.00

                    if Analyses.iloc[Analysis,16] != Analyses.iloc[Analysis,17] and Analyses.iloc[Analysis,18] is not None:
                        for AnchorLevel in np.arange(
                            Analyses.iloc[Analysis,16],
                            Analyses.iloc[Analysis,17] + Analyses.iloc[Analysis,18],
                            Analyses.iloc[Analysis,18]
                        ):
                            Analysis_dict = u.make_analysis_dict(
                                Analyses, Analysis, ImportData,
                                AnchorLevel,
                                AInclination,
                                PrescrbAnchorForce,
                                vararr,
                                geninfoarr
                            )
                            #print(Analysis_dict)
                            GeneratedAnalyses.append(Analysis_dict)
                            geninfoarr[0] += 1
                    else:
                        Analysis_dict = u.make_analysis_dict(
                            Analyses, Analysis, ImportData,
                            Analyses.iloc[Analysis,16],
                            AInclination,
                            PrescrbAnchorForce,
                            vararr,
                            geninfoarr
                        )
                        #print(Analysis_dict)
                        GeneratedAnalyses.append(Analysis_dict)
                        geninfoarr[0] += 1
                else:
                    Analysis_dict = u.make_analysis_dict(
                        Analyses, Analysis, ImportData,
                        None,
                        None,
                        None,
                        vararr,
                        geninfoarr
                    )
                    #print(Analysis_dict)
                    GeneratedAnalyses.append(Analysis_dict)
                    geninfoarr[0] += 1

                geninfoarr[1] += 1
            a = analysisclass()
            ## Append soil layers data to analysis dictionary
            a.AddSoilToAnalysis(GeneratedAnalyses, self.GenerateSoilProfiles(ImportData.get('Stratification')))

            ## Append additional pressure profiles
            a.AddPressureToAnalysis(GeneratedAnalyses, self.GenerateAddPressProfiles(ImportData.get('AddPress')))

            ## Append design parameters
            a.AddDesignParameters(GeneratedAnalyses, ImportData.get('LoadComb'))

            return GeneratedAnalyses