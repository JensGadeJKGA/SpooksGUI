class PDFhelper:
    def generatePDFdict(VerticalEquilibriumOutput):
        GetResultsOutput = VerticalEquilibriumOutput.get('GetResultsOutput')
        Analysis = VerticalEquilibriumOutput.get('Analysis')
        PlotResults = GetResultsOutput.get('PlotResults')

        PDFdict = {
            'Analysis': Analysis,
            'Project': Analysis.get('Project'),
            'Subject': Analysis.get('Subject'),
            'Initials': Analysis.get('Initials'),
            'Checker': Analysis.get('Checker'),
            'Approver': Analysis.get('Approver'),
            'Date': GetResultsOutput.get('Date'),
            'Warning': GetResultsOutput.get('Warnings'),
            'AnalysisNo': Analysis.get('AnalysisNo'),
            'State': Analysis.get('State'),
            'WaterDensity': Analysis.get('WaterDensity'),
            'SoilProfile': Analysis.get('SoilProfile'),
            'SoilLayersFront': Analysis.get('SoilLayersFront'),
            'SoilLayersBack': Analysis.get('SoilLayersBack'),
            'WaterLevelFront': Analysis.get('WaterLevelFront'),
            'WaterLevelBack': Analysis.get('WaterLevelBack'),
            'AddPressureProfile': Analysis.get('AddPressureProfile'),
            'AddPress_z': Analysis.get('AddPress_z'),
            'AddPress_ez': Analysis.get('AddPress_ez'),
            'AddPress_ez_Design': Analysis.get('DesignAddPress_ez'),
            'SlopeFront': Analysis.get('SlopeFront'),
            'SlopeBack': Analysis.get('SlopeBack'),
            'LoadFront': Analysis.get('LoadFront'),
            'LoadBack': Analysis.get('LoadBack'),
            'AxialWallLoad': Analysis.get('AxialWallLoad'),
            'zR': Analysis.get('LevelLoadBack'),
            'Alpha': Analysis.get('Alpha'),
            'ConsequenceClass': Analysis.get('ConsequenceClass'),
            'PartialSafetyFactors': Analysis.get('PartialSafetyFactors'),
            'AnchorLevel': Analysis.get('AnchorLevel'),
            'AnchorForce': GetResultsOutput.get('Results').get('AnchorForce'),
            'AnchorInclination': Analysis.get('AnchorInclination'),
            'PrescrbAnchorForce': Analysis.get('PrescrbAnchorForce'),
            'iA': Analysis.get('iA'),
            'iB': Analysis.get('iB'),
            'iC': Analysis.get('iC'),
            'zB': Analysis.get('zB'),
            'WD': Analysis.get('WD'),
            'CC': Analysis.get('CC'),
            'zT': Analysis.get('zT'),
            'PlotResults': PlotResults,
            'MaxMoment': PlotResults.get('MaxMoment'),
            'MaxShearForce': PlotResults.get('MaxShearForce'),
            'MomentAtAnchor': GetResultsOutput.get('Results').get('MomentAtAnchor'),
            'ToeLevel': GetResultsOutput.get('Results').get('ToeLevel'),
        }  
        return PDFdict, GetResultsOutput
    
    def generateToeLevel(VerticalEquilibriumOutput, Analysis):
        GetResultsOutput = VerticalEquilibriumOutput.get('GetResultsOutput')

        ToeLevel = GetResultsOutput.get('Results').get('ToeLevel')
        if ToeLevel == 'N/A':
            SoilLevelsFront = []
            for SoilLayer in SoilLayersFront:
                SoilLevelsFront.append(SoilLayer.get('TopLayer'))
            GroundLevelFront = max(SoilLevelsFront)
            ToeLevel = GroundLevelFront - 0.1
        print(ToeLevel)

        SumTanForce = VerticalEquilibriumOutput.get('SumTanForce')
        WallMass = Analysis.get('WallMass') 
        WeightWallTotal = (Analysis.get('WallMass') * 9.82 / 1000) * (zT - ToeLevel)

        return ToeLevel,SumTanForce,WallMass,WeightWallTotal