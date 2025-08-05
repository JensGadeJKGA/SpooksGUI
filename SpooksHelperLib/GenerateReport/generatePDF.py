import os
from SpooksHelperLib.GenerateReport.PDFhelper import PDFhelper as ph
from SpooksHelperLib.Utils import utils

import numpy as np

class generatePDF:
    def __init__(self):
        pass

    def PDFGenerator(self, VerticalEquilibriumOutput, SheetPileAddOnResults, Version):

        print('Generating report pages...')

        # === Input Parsing ===
        PDFdict, PlotResults, Analysis = ph.generatePDFdict(VerticalEquilibriumOutput)
        ToeLevel, SumTanForce, WallMass, WeightWallTotal = ph.generateToeLevel(
            VerticalEquilibriumOutput, PDFdict['Analysis'], PDFdict['SoilLayersFront']
        )
        PlotLevels, e1, e2, Moment, ShearForce, DW, ENet, JU = ph.extractPlotResults(PlotResults)
        Sheetpiledict, Sheetpile, u_rel, control_Rot, u_rel_lvl = ph.extractSheetPileInput(Analysis)

        # === PDF Setup ===
        pdf, col_width, th, epw = ph.instantiatePDF(PDFdict['Warnings'])

        # === SECTION 1: General Information ===
        pdf.set_font("Courier", size=15)
        pdf.cell(200, 10, txt='1. General information', ln=10, align='L')
        pdf.ln(8)

        pdf.set_font("Courier", size=12)
        pdf.cell(200, 10, txt="1.1 Execution", ln=11, align='L')
        pdf = ph.fillPDF('Date', PDFdict, pdf, col_width, th)
        pdf = ph.fillPDF('Project', PDFdict, pdf, col_width, th)
        pdf = ph.fillPDF('Initials', PDFdict, pdf, col_width, th)
        pdf = ph.fillPDF('Subject', PDFdict, pdf, col_width, th)
        pdf = ph.fillPDF('AnalysisNo', PDFdict, pdf, col_width, th, 4, 'Calculation no.')

        # === Check ===
        pdf.cell(200, 10, txt="1.2 Check", ln=11, align='L')
        pdf = ph.fillPDF('Checker', PDFdict, pdf, col_width, th)
        pdf.cell(col_width[0], 2 * th, str('Date:'), border=1)
        pdf.cell(col_width[1], 2 * th, str(''), border=1)
        pdf.ln(4 * th)

        # === Approval ===
        pdf.cell(200, 10, txt="1.2 Approval", ln=11, align='L')
        pdf = ph.fillPDF('Approver', PDFdict, pdf, col_width, th)

        # === SECTION 2: Input Parameters ===
        pdf.ln(2 * th)
        pdf.set_font("Courier", size=15)
        pdf.cell(200, 10, txt='2. Input parameters', ln=14, align='L')

        col_width[0] = epw / 3
        col_width[1] = epw / 6

        pdf.set_font("Courier", size=12)
        pdf = ph.fillPDFext('zT', PDFdict, pdf, col_width, th, 'm')

        # === Anchors ===
        if PDFdict['Anchorlevel'] is not None:
            pdf = ph.fillPDFext('Anchorlevel', PDFdict, pdf, col_width, th, 'm', 2, 'Anchor level, zA')
            pdf = ph.fillPDFext('AnchorInclination', PDFdict, pdf, col_width, th, 'deg.', 2, 'Anchor inclination:')

            if PDFdict['PrescrAnchorForce'] != 0.00:
                pdf = ph.fillPDFext('PrescrAnchorForce', PDFdict, pdf, col_width, th, 'kN/m.', 2, 'Prescr. anchor force:')
            else:
                pdf.cell(col_width[0], 2 * th, str('Prescr. anchor force:'), border=1)
                pdf.cell(col_width[1], 2 * th, str('N/A'), border=1)
                pdf.cell(col_width[0], 2 * th, str('kN/m'), border=1)
                pdf.ln(2 * th)

        # === Wall Mass and Water Density ===
        pdf.cell(col_width[0], 2 * th, str('Mass of wall:'), border=1)
        pdf.cell(col_width[1], 2 * th, str(WallMass), border=1)
        pdf.cell(col_width[0], 2 * th, str('kg/m/m of wall'), border=1)
        pdf.ln(2 * th)

        pdf = ph.fillPDFext('WaterDensity', PDFdict, pdf, col_width, th, 'kN/m3', 2, 'Water density, gam_w')

        # === Geometry and Soil ===
        pdf = ph.fillPDFext('State', PDFdict, pdf, col_width, th, '-')
        pdf = ph.fillPDFext('SlopeBack', PDFdict, pdf, col_width, th, 'deg.', 2, 'Slope back')
        pdf = ph.fillPDFext('SlopeFront', PDFdict, pdf, col_width, th, 'deg.', 2, 'Slope Front')
        pdf = ph.fillPDFext('SoilProfile', PDFdict, pdf, col_width, th, '-', 2, 'Soil profile')

        # === Soil Layers ===
        col_width = [epw / 12, epw / 6]
        SoilData = [
            ["z_top", "g_d", "g_m", "cu", "c'", "phi'", "i", "r", "Description", "Keep drained"],
            ["m", "kN/m3", "kN/m3", "kN/m2", "kN/m2", "deg.", "-", "-", "-", "-"]
        ]

        pdf = ph.appendSoillayerData(SoilData, PDFdict['SoilLayersBack'], pdf, col_width, th,
                                    "2.1 Characteristic soil parameters back")
        pdf = ph.appendSoillayerData(SoilData, PDFdict['SoilLayersFront'], pdf, col_width, th,
                                    "2.2 Characteristic soil parameters front")

        # === Water Levels ===
        pdf = self.waterlevel(epw, pdf, PDFdict, th)

        # === Additional Pressure ===
        pdf = self.addPressure(pdf, PDFdict, epw, th)

        # === Loads ===
        pdf = self.loads(epw, pdf, th, PDFdict)

        # === Safety Factors ===
        pdf = self.partialSafetyFactors(epw, pdf, PDFdict, th)

        # === Failure Mode ===
        pdf = self.failureMode(pdf, epw, PDFdict, th)

        # === King Post Wall ===
        pdf = self.kingPostWall(pdf, PDFdict, epw, th)

        # === Results Summary ===
        pdf = self.results(pdf, th, epw, PDFdict, SumTanForce, WeightWallTotal)

        # === Pressure and Structural Forces ===
        pdf = self.pressAndStructForce(pdf, th, epw, Analysis, PlotResults, Sheetpiledict)

        # === Save PDF ===
        TemporaryPath = utils.TemporaryWorkingDirectory()
        TemporaryPath = os.path.join(TemporaryPath, r'pdfresults.pdf')
        pdf.output(TemporaryPath)

        return TemporaryPath


    def waterlevel(self, epw, pdf, PDFdict,th):
        col_width = epw/6
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.3 Water levels", 
                ln = 1, align = 'L')
        pdf.cell(col_width, 2*th, str('w_b'), border=1)
        pdf.cell(col_width, 2*th, str('w_f'), border=1)
        pdf.ln(2*th)
        pdf.cell(col_width, 2*th, str('[m]'), border=1)
        pdf.cell(col_width, 2*th, str('[m]'), border=1)
        pdf.ln(2*th)
        pdf.cell(col_width, 2*th, str(PDFdict['WaterLevelBack']), border=1)
        pdf.cell(col_width, 2*th, str(PDFdict['WaterLevelFront']), border=1)
        pdf.ln(2*th)

        return pdf

    def addPressure(self, pdf, PDFdict, epw, th):
        pdf.ln(2*th)
        if PDFdict['AddPressureProfile'] in ['AP1','AP2','AP3','AP4','AP5','AP6','AP7','AP8','AP9','AP10']:
            pdf.cell(200, 10, txt = "2.4 Additional pressure profile:"+' '+ PDFdict['AddPressureProfile'], 
                    ln = 4, align = 'L')
            
            zAP = ['z [m]']
            for elem in PDFdict['AddPress_z']:
                zAP.append(elem)
            eAP = ['ez_k [kN/m2]']
            for elem in PDFdict['AddPress_ez']:
                eAP.append(round(elem,1))
                
            eAPd = ['ez_d [kN/m2]']
            for elem in PDFdict['AddPress_ez_Design']:
                eAPd.append(round(elem,1))
            
            AP = [zAP,eAP, eAPd]
                
            for row in AP:
                for cellno, datum in enumerate(row):
                    if cellno > 0:
                        # Enter data in colums
                        pdf.cell(epw/12, 2*th, str(datum), border=1)
                    else:
                        pdf.cell(epw/6, 2*th, str(datum), border=1)
            
                pdf.ln(2*th)
        else:
            pdf.cell(200, 10, txt = "2.4 Additional pressure profile:"+' '+'no additional pressure', 
                    ln = 4, align = 'L')
        return pdf
        
    def loads(self,epw,pdf,th,PDFdict):
        col_width = epw/6
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.5 Loads", 
                ln = 3, align = 'L')
        pdf.cell(col_width, 2*th, str('zR'), border=1)
        pdf.cell(col_width, 2*th, str('q_bk'), border=1)
        pdf.cell(col_width, 2*th, str('q_fk'), border=1)
        pdf.cell(col_width*2, 2*th, str('Axial wall load (design)'), border=1)
        pdf.ln(2*th)
        pdf.cell(col_width, 2*th, str('m'), border=1)
        pdf.cell(col_width, 2*th, str('kN/m2'), border=1)
        pdf.cell(col_width, 2*th, str('kN/m2'), border=1)
        pdf.cell(col_width*2, 2*th, str('kN/m'), border=1)
        pdf.ln(2*th)
        pdf.cell(col_width, 2*th, str(PDFdict['zR']), border=1)
        pdf.cell(col_width, 2*th, str(PDFdict['LoadBack']), border=1)
        pdf.cell(col_width, 2*th, str(PDFdict['LoadFront']), border=1)
        pdf.cell(col_width*2, 2*th, str(PDFdict['AxialWallLoad']), border=1)
        pdf.ln(2*th)
        return pdf

    def partialSafetyFactors(self,epw,pdf,PDFdict,th):
        PartialSafetyFactors = PDFdict['PartialSafetyFactors']
        col_width1 = epw*3/12
        col_width2 = epw/12
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.6 Safety", 
                ln = 4, align = 'L')
        pdf.cell(col_width1, 2*th, str('Alpha'), border=1)
        pdf.cell(col_width2, 2*th, str(PDFdict['Alpha']), border=1)
        pdf.ln(2*th)
        pdf.cell(col_width1, 2*th, str('Consequence class:'), border=1)
        pdf.cell(col_width2, 2*th, str(PDFdict['ConsequenceClass']), border=1)
        pdf.ln(2*th)
        pdf.set_font("Courier", size = 11) 
        psf_header = ['f_gamf','f_qf','f_cf','f_cuf','f_phif','f_wat','f_AP','f_gamb','f_qb','f_cb','f_cub','f_phib']
        for psf in psf_header:
            pdf.cell(col_width2, 2*th, str(psf), border=1)
        pdf.ln(2*th)
        pdf.set_font("Courier", size = 12) 
        psfs = [PartialSafetyFactors.get('f_gamf'),
                PartialSafetyFactors.get('f_qf'),
                PartialSafetyFactors.get('f_cf'),
                PartialSafetyFactors.get('f_cuf'),
                PartialSafetyFactors.get('f_phif'),
                PartialSafetyFactors.get('f_wat'),
                PartialSafetyFactors.get('f_AP'),
                PartialSafetyFactors.get('f_gamb'),
                PartialSafetyFactors.get('f_qb'),
                PartialSafetyFactors.get('f_cb'),
                PartialSafetyFactors.get('f_cub'),
                PartialSafetyFactors.get('f_phib')]
        for psf in psfs:
            pdf.cell(col_width2, 2*th, str(np.round(psf,2)), border=1)
        pdf.ln(2*th)
        return pdf
    
    def failureMode(self,pdf,epw,PDFdict,th,):
        col_width = epw/6
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.7 Failure mode", 
                ln = 5, align = 'L')
        if PDFdict['AnchorLevel'] != None:
            pdf.cell(col_width*3, 2*th, 'Anchored wall', border=1)
        else:
            pdf.cell(col_width*3, 2*th, 'Free wall', border=1)
        pdf.ln(2*th)
        fail_coeff_header = ['iA', 'iB', 'iC']
        fail_coeff = [PDFdict['iA'], PDFdict['iB'], PDFdict['iC']]
        for fail in fail_coeff_header:
            pdf.cell(col_width, 2*th, str(fail), border=1)
        pdf.ln(2*th)
        
        for fail in fail_coeff:
            pdf.cell(col_width, 2*th, str(fail), border=1)
        pdf.ln(2*th)
        return pdf
    
    def kingPostWall(self,pdf,PDFdict,epw,th):
        col_width = epw/6
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.8 King post wall", 
                ln = 6, align = 'L')
        if PDFdict['zB'] != None and PDFdict['WD'] != None and PDFdict['CC'] != None:
            kingpost_header = ['zB', 'WD', 'CC']
            kingpost_unit = ['m','m','m']
            kingpost = [PDFdict['zB'], PDFdict['WD'], PDFdict['CC']]
            for kp in kingpost_header:
                pdf.cell(col_width, 2*th, str(kp), border=1)
            pdf.ln(2*th)
            
            for kp in kingpost_unit:
                pdf.cell(col_width, 2*th, str(kp), border=1)
            pdf.ln(2*th)
            
            for kp in kingpost:
                pdf.cell(col_width, 2*th, str(kp), border=1)
        else:
            pdf.cell(200, 10, txt = "Not king post wall.", 
                ln = 6, align = 'L')
        pdf.ln(2*th)
        
        pdf.add_page('P')

        return pdf

    def results(self,pdf,th,epw,PDFdict,SumTanForce,WeightWallTotal):
        
        #### Results
        # Header
        pdf.set_font("Courier", size = 15) 
        pdf.cell(200, 10, txt = '3. Results', 
                ln = 6, align = 'L')
        
        pdf.ln(8)
        
        pdf.set_font("Courier", size = 12)
        pdf.cell(200, 10, txt = "3.1 Summary", 
                ln = 6, align = 'L')
        col_width = [epw*6/12,epw*2/12]
        AnchorAxial = PDFdict['AnchorForce']/np.cos(np.radians(PDFdict['AnchorInclination']))

        # Max. moment
        ph.fillResultext(pdf,abs(PDFdict['MaxMoment']),th,col_width,'Max. |moment|','kNm/m')
       
        # Max. shear force
        ph.fillResultext(pdf,abs(PDFdict['MaxShearForce']),th,col_width,'Max. |shear force|','kN/m')

        # Toe level
        ph.fillResultext(pdf,PDFdict['ToeLevel'],th,col_width,'Toe level','m')

        if PDFdict['AnchorLevel'] != None:
            # Anchor force
            ph.fillResultext(pdf,PDFdict['AnchorForce'],th,col_width,'Anchor force, Ad', 'kN/m')
            # Axial anchor force
            ph.fillResultext(pdf,AnchorAxial,th,col_width,'Axial anchor force', 'kN/m')
            # Moment at anchor
            ph.fillResultext(pdf,abs(PDFdict['MomentAtAnchor']),th,col_width,'|Moment| at anchor level','kNm/m')
        # Tangential earth pressure resultant
        ph.fillResultext(pdf,PDFdict['SUmTanForce'],th,col_width,'Sum of tangential earth pressure*','kN/m')
        # Sum of vertical forces
        pdf.cell(col_width[0], 2*th, str('Sum of vertical forces*:'), border=1)
        if PDFdict['AnchorLevel'] != None:
            pdf.cell(col_width[1], 2*th, str(format(SumTanForce-AnchorAxial*np.sin(np.radians(float(PDFdict['AnchorInclination'])))-PDFdict['WeightWallTotal'],'.1f')), border=1)
        else:
            pdf.cell(col_width[1], 2*th, str(format(SumTanForce-WeightWallTotal,'.1f')), border=1)
        pdf.cell(col_width[1], 2*th, str('kN/m'), border=1)
        pdf.ln(2*th)
        # Note
        pdf.cell(epw*10/12, 2*th, str('*Tangential pressure and vertical forces are positive upwards.'), border=1)
        pdf.ln(2*th)

        return pdf
    
    def pressAndStructForce(self,pdf,th,epw,Analysis,PlotResults,Sheetpiledict):
        #Extract inputs
        plotres = ph.extractPlotResults(PlotResults)
        Sheetpiledict, Sheetpile, u_rel, control_Rot, u_rel_lvl = ph.extractSheetPileInput(Analysis)

        #section 3.2 title
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "3.2 Pressure and structural forces", 
                ln = 6, align = 'L')
        
        #forces table
        col_width = epw/8
        forces_header = ['Level','e1','e2','dw','e-net','Ved','Med','Ju']
        forces_units = ['m','kN/m2','kN/m2','kN/m2','kN/m2','kN/m','kNm/m','-']

        ph.writeTableRow(pdf, forces_header, col_width, 2 * th)
        ph.writeTableRow(pdf, forces_units, col_width, 2 * th)

        for i in range(len(plotres[0])):
            row = [format(plot[i], '1f') for plot in plotres]
            ph.writeTableRow(pdf,row,col_width,2*th)
        
        ## Sheet pile add on
        if Sheetpiledict['UseAddOn'] == 'Yes':
            
            # Header
            pdf.set_font("Courier", size=15)
            pdf.ln(2 * th)
            pdf.cell(200, 10, txt='4. Sheet pile add on', ln=6, align='L')
            
            # 4.1 Input
            pdf.set_font("Courier", size=12)
            pdf.ln(2 * th)
            pdf.cell(200, 10, txt="4.1 Input", ln=6, align='L')
            
            col_widths = [epw*7/12,epw*2/12]
            text = ['Add on active?','Limit state','Control class','Optimize','Max. utilization','fyk','Beta_B','Beta_D','Design life','Soil compaction']
            name = ['-','-','-','-','-','MPa','-','-','Years','-']
            ph.fillSheetpileAddOn(name,text,Sheetpiledict,th,col_widths,pdf)

            # corrosion rate at max. M, front
            pdf.cell(epw*11/12, 2*th, str('Corrosion rates (total)'), border=1)
            pdf.ln(2*th)

            pdf.cell(col_width1, 2*th, str('Level (m)'), border=1)
            pdf.cell(col_width2, 2*th, str('Rate'), border=1)
            pdf.cell(col_width2, 2*th, str('Unit'), border=1)
            pdf.ln(2*th)

            for lvl, rate in zip(Sheetpiledict['tCorLevel'], Sheetpiledict['tCor']):
                pdf.cell(col_widths[0], 2 * th, str(lvl), border=1)
                pdf.cell(col_widths[1], 2 * th, str(rate), border=1)
                pdf.cell(col_widths[1], 2 * th, 'mm/yr', border=1)
                pdf.ln(2 * th)

            
            #4.2 results
            pdf.ln(2 * th)
            pdf.set_font("Courier", size=12)
            pdf.cell(200, 10, txt="4.2 Results", ln=6, align='L')

            col_width1 = epw*6/12
            col_width1a = epw*7/12
            col_width2 = epw*2/12
            col_width2a = epw*5/12
            
            # Sheet pile profile
            ph.writeKeyValueRow(pdf,'Sheet pile profile:',Sheetpile,col_width1,col_width2a,th)
            ph.writeKeyValueRow(pdf,'Max. relative utilization ratio:',u_rel,col_width1a,col_width2,th,unit='-')
            ph.writeKeyValueRow(pdf, 'Rotational capacity:', control_Rot, col_width1, col_width2 * 2, th)

            pdf.cell(col_width1a, 2*th, str('Level (m)'), border=1)
            pdf.cell(col_width2*2, 2*th, str('Rel. utilisation ratio'), border=1)
            pdf.ln(2*th)
            
            if u_rel_lvl is not None:
                for index, row in u_rel_lvl.iterrows():
                    pdf.cell(col_width1, 2 * th, str(index), border=1)
                    pdf.cell(col_width2, 2 * th, str(round(row['u_rel'], 3)), border=1)
                    pdf.cell(col_width2, 2 * th, '-', border=1)
                    pdf.ln(2 * th)
            
            return pdf