from fpdf import FPDF


class PDFhelper:
    def __init__(self):
        pass
        
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
            'Warnings': GetResultsOutput.get('Warnings'),
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
        return PDFdict, PlotResults, Analysis
    
    def generateToeLevel(VerticalEquilibriumOutput, Analysis, SoilLayersFront, zT):
        GetResultsOutput = VerticalEquilibriumOutput.get('GetResultsOutput')

        ToeLevel = GetResultsOutput.get('Results').get('ToeLevel')
        if ToeLevel == 'N/A':
            SoilLevelsFront = []
            for SoilLayer in SoilLayersFront:
                SoilLevelsFront.append(SoilLayer.get('TopLayer'))
            GroundLevelFront = max(SoilLevelsFront)
            ToeLevel = GroundLevelFront - 0.1

        SumTanForce = VerticalEquilibriumOutput.get('SumTanForce')
        WallMass = Analysis.get('WallMass') 
        WeightWallTotal = (Analysis.get('WallMass') * 9.82 / 1000) * (zT - ToeLevel)

        return ToeLevel,SumTanForce,WallMass,WeightWallTotal
    
    def extractPlotResults(PlotResults):
        return [PlotResults.get('PlotLevels'),
            PlotResults.get('e1'),
            PlotResults.get('e2'),
            PlotResults.get('Moment'),
            PlotResults.get('ShearForce'),
            PlotResults.get('DW'),
            PlotResults.get('enet'),
            PlotResults.get('JU'),
        ]

    def extractSheetPileInput(Analysis, SheetPileAddOnResults):
        Sheetpile = SheetPileAddOnResults.get('SheetPileProfile')
        u_rel = SheetPileAddOnResults.get('RUR')
        control_Rot = SheetPileAddOnResults.get('RotCap')
        u_rel_lvl = SheetPileAddOnResults.get('RURLevel')

        return {'UseAddOn': Analysis.get('SheetPileAddOnInput').get('UseAddOn'),
            'LimitState': Analysis.get('SheetPileAddOnInput').get('LimitState'),
            'ControlClass': Analysis.get('SheetPileAddOnInput').get('ControlClass'),
            'Optimize': Analysis.get('SheetPileAddOnInput').get('Optimize'),
            'MaxUtilization': Analysis.get('SheetPileAddOnInput').get('MaxUtilization'),
            'fyk': Analysis.get('SheetPileAddOnInput').get('fyk'),
            'BetaB': Analysis.get('SheetPileAddOnInput').get('BetaB'),
            'BetaD': Analysis.get('SheetPileAddOnInput').get('BetaD'),
            'DesignLife': Analysis.get('SheetPileAddOnInput').get('DesignLife'),
            'tCor': Analysis.get('SheetPileAddOnInput').get('tCor'),
            'tCorLevel': Analysis.get('SheetPileAddOnInput').get('tCorLevel'),
            'SoilDeposit': Analysis.get('SheetPileAddOnInput').get('SoilDeposit')
        },Sheetpile,u_rel,control_Rot,u_rel_lvl
    
    def instantiatePDF(PDFdict):

        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', '', 20)
                self.cell(0, 10, 'COWI', 0, 0, 'L')
                self.set_font('Courier', '', 9)
                self.cell(0, 10, PDFdict['Project']+', '+PDFdict['Subject']+', '+PDFdict['Date'], 0, 0, 'R')
                # Line break
                self.ln(10)
        
            # Page footer
            def footer(self):
                version = '3'
                # Position at 1.5 cm from bottom
                self.set_y(-15)
                self.set_font('Courier', '', 7)
                self.cell(0, 10, 'COWI WinSpooks Plug-in '+ version, 0, 0, 'L')
                # Page number
                self.set_font('Courier', '', 9)
                self.cell(0, 10, 'Page ' + str(self.page_no()) + ' / {nb}', 0, 0, 'R')

        # Instantiation of inherited class
        pdf = PDF()
        pdf.alias_nb_pages()
        
        # Add a page 
        pdf.add_page('P') 
        
        # style and size of font  
        pdf.set_font("Courier", size = 12) 
        
        # Effective page width
        epw = pdf.w - 2*pdf.l_margin
        ## Width of columns
        col_width1 = epw/3
        col_width2 = epw/2
        # Text height is the same as current font size
        th = pdf.font_size
        
        #### WARNINGS
        pdf.set_font("Courier", size = 15) 
        pdf.cell(200, 10, txt = '0. Warnings', 
                ln = 6, align = 'L')
        pdf.ln(2)
        ## Warning
        pdf.set_font("Courier", size = 12)
        if len(PDFdict['Warnings']) != 0:
            
            for Warning_ in PDFdict['Warnings']:
            
                if Warning_ == 'The input contains boundaries below the encastre level.':
                    pdf.cell(200, 10, txt = 'The input contains boundaries below the encastre level.', 
                            ln = 6, align = 'L')
                    pdf.cell(200, 10, txt = 'Properties below such boundaries are not used in this program version.', 
                            ln = 7, align = 'L')
                    pdf.cell(200, 10, txt = 'The effect should be examined by using a boundary immediately above the', 
                            ln = 8, align = 'L')
                    pdf.cell(200, 10, txt = 'encastre level with suitably adjusted parameters.', 
                            ln = 9, align = 'L')
                elif Warning_ == 'WinSPOOKS warning: check log file':
                    pdf.cell(200, 10, txt = 'WinSPOOKS warning: check log file.', 
                            ln = 6, align = 'L')
                    
                elif Warning_ == 'WinSPOOKS error: check log file':
                    pdf.cell(200, 10, txt = 'WinSPOOKS error: check log file.', 
                            ln = 6, align = 'L')
        else:
            pdf.cell(200, 10, txt = 'No warnings.', 
                    ln = 6, align = 'L')
        
        pdf.ln(2)
        return pdf, [col_width1, col_width2], th, epw
    
    def fillPDF(identifier, pdfdict, pdf, col_width, th, i=2, text=None):
        if text:
            pdf.cell(col_width[0], 2*th, str(text+':'), border=1)
        else: pdf.cell(col_width[0], 2*th, str(identifier+':'), border=1)
        pdf.cell(col_width[1], 2*th, str(pdfdict[identifier]), border=1)
        pdf.ln(i*th)
        return pdf

    def fillPDFext(identifier, pdfdict, pdf, col_width, th, name, i=2, text=None):
        if text:
            pdf.cell(col_width[0], 2*th, str(text+':'), border=1)
        else: pdf.cell(col_width[0], 2*th, str(identifier+':'), border=1)
        pdf.cell(col_width[1], 2*th, str(pdfdict[identifier]), border=1)
        pdf.cell(col_width[0], 2*th, str(name), border=1)
        pdf.ln(i*th)
        return pdf
        
    def fillResultext(pdf,pdfdictentry,th, col_width,text,name):
        pdf.cell(col_width[0], 2*th, str(text+':'), border=1)
        pdf.cell(col_width[1], 2*th, str(format(pdfdictentry,'.1f')), border=1)
        pdf.cell(col_width[0], 2*th, str(name), border=1)
        pdf.ln(2*th)
        return pdf
    
    def fillSheetpileAddOn(names,texts,sheetpileinput,th,col_width,pdf):
        for name,text,sheetpile in zip(names,texts,sheetpileinput):
            pdf.cell(col_width[0], 2*th, str(text+':'), border=1)
            pdf.cell(col_width[1], 2*th, str(sheetpile), border=1)
            pdf.cell(col_width[1], 2*th, str(name), border=1)
            pdf.ln(2*th)
        return pdf


    def appendSoillayerData(SoilData, SoilLayers, pdf, col_width, th, sidetxt):
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = sidetxt, 
                ln = 13, align = 'L')
    
        for i in range(0,len(SoilLayers)): 
            SoilData.append([format(float(SoilLayers[i].get('TopLayer')),'.2f'), 
                            format(float(SoilLayers[i].get('Gamma_d')),'.0f'), 
                            format(float(SoilLayers[i].get('Gamma_m')),'.0f'), 
                            format(float(SoilLayers[i].get('cu')),'.0f'), 
                            format(float(SoilLayers[i].get('c')),'.0f'), 
                            format(float(SoilLayers[i].get('phi')),'.0f'), 
                            format(float(SoilLayers[i].get('i')),'.1f'), 
                            format(float(SoilLayers[i].get('r')),'.2f'),
                            SoilLayers[i].get('Description'), SoilLayers[i].get('KeepDrained')])
                            
        for row in SoilData:
            for cellno, datum in enumerate(row):
                if cellno < 8:
                    # Enter data in column
                    pdf.cell(col_width[0], 2*th, str(datum), border=1)
        
                else:
                    pdf.cell(col_width[1], 2*th, str(datum), border=1)
        
            pdf.ln(2*th)
        return pdf
    
    # Fill a single row of cells
    def writeTableRow(pdf, values, col_width, height):
        for val in values:
            pdf.cell(col_width, height, str(val), border=1)
        pdf.ln(height)

    # Fill a row with a key, value, and optional unit
    def writeKeyValueRow(pdf, key, value, col1_width, col2_width, height, unit=None):
        pdf.cell(col1_width, height, str(key), border=1)
        pdf.cell(col2_width, height, str(value), border=1)
        if unit:
            pdf.cell(col2_width, height, str(unit), border=1)
        pdf.ln(height)
            