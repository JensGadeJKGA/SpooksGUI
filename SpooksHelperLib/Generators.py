from SpooksHelperLib.SoilProfiles import soilprofiles
        
class generators():
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
    
    def GenerateSoilProfiles(Stratification):

        SoilProfiles = {'SP1': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP2': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP3': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP4': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP5': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP6': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP7': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP8': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP9': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}},
                        'SP10': {'Back': {'Slope': None,'Layers': []}, 'Front': {'Slope': None,'Layers': []}}}


        
        #front soils
        for i in range(10):
            sp = "SP"+str(i+1)
            soilprofile = soilprofiles.soilprofiles(sp, Stratification, SoilProfiles, [29*i,5], i)
            soilprofiles.AppendToSoilProfiles(soilprofile[0], soilprofile[1], soilprofile[2], soilprofile[3], soilprofile[4], soilprofile[5])

        #back soils    
        for i in range(10):
            soilprofile = soilprofiles.soilprofiles(sp, Stratification, SoilProfiles, [29*i,2], i)
            soilprofiles.AppendToSoilProfiles(soilprofile[0], soilprofile[1], soilprofile[2], soilprofile[3], soilprofile[4], soilprofile[5])
        
        return SoilProfiles