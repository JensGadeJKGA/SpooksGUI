from PDFhelper import PDFhelper as ph
from fpdf import FPDF
from reportFront import reportFront

class generatePDF:

    def PDFGenerator(VerticalEquilibriumOutput, SheetPileAddOnResults, Version):
        
        print('Generating report pages...')
        PDFdict, PlotResults, Analysis = ph.generatePDFdict(VerticalEquilibriumOutput)
        
        ### Max soil layer level front
        ToeLevel, SumTanForce, WallMass, WeightWallTotal = ph.generateToeLevel(VerticalEquilibriumOutput, PDFdict['Analysis'], PDFdict['SoilLayersFront'])
        PlotLevels, e1, e2, Moment, ShearForce, DW, ENet, JU = ph.extractPlotResults(PlotResults)
        
        ##################### Sheet pile add on ######################
        Sheetpiledict, Sheetpile, u_rel, control_Rot, u_rel_lvl = ph.extractSheetPileInput(Analysis)
        
        # ## Font for cowi logo
        # pdf.add_font('century', '', r"C:\Users\EMBT\OneDrive - COWI\Documents\Python\SPOOKS\CENSCBK.TTF", uni=True)
        
        pdf, col_width, th, epw = ph.instantiatePDF(PDFdict['Warnings']) 
                
        
        
        #### GENERAL INFORMATION

        # Header
        pdf.set_font("Courier", size = 15) 
        pdf.cell(200, 10, txt = '1. General information', 
                ln = 10, align = 'L')
        pdf.ln(8)
        pdf.set_font("Courier", size = 12) 
        pdf.cell(200, 10, txt = "1.1 Execution", 
                ln = 11, align = 'L')
        
        # Date
        ph.fillPDF('Date',PDFdict,pdf,col_width,th)
        # Project
        ph.fillPDF('Project',PDFdict,pdf,col_width,th)        
        # Initials
        ph.fillPDF('Initials',PDFdict,pdf,col_width,th)
        # Subject
        ph.fillPDF('Subject',PDFdict,pdf,col_width,th)
        # Calc. no.
        ph.fillPDF('AnalysisNo',PDFdict,pdf,col_width,th,4,'Calculation no.')
        ## Check
        pdf.cell(200, 10, txt = "1.2 Check", 
                ln = 11, align = 'L')
        ph.fillPDF('Checker', PDFdict, pdf, col_width, th)
        pdf.cell(col_width1, 2*th, str('Date:'), border=1)
        pdf.cell(col_width2, 2*th, str(''), border=1)
        pdf.ln(4*th)
        ## Approval
        pdf.cell(200, 10, txt = "1.2 Approval", 
                ln = 11, align = 'L')
        ph.fillPDF('Approver',PDFdict,pdf,col_width,th)
        # Header
        pdf.ln(2*th)
        pdf.set_font("Courier", size = 15) 
        pdf.cell(200, 10, txt = '2. Input parameters', 
                ln = 14, align = 'L')
        ## Width of columns
        col_width[0] = epw/3
        col_width[1] = epw/6
        # Top wall
        pdf.set_font("Courier", size = 12)
        ph.fillPDFext('zT',PDFdict,pdf,col_width,th,'m')

        if PDFdict['Anchorlevel'] != None:
            # Anchor level
            ph.fillPDFext('Anchorlevel',PDFdict,pdf,col_width,th,'m',2,'Anchor level, zA')
            # Anchor inclination
            ph.fillPDFext('AnchorInclination',PDFdict,pdf,col_width,th,'deg.',2,'Anchor inclination:')
            # Prescribed anchor force
            if PDFdict['PrescrAnchorForce'] != 0.00:
                ph.fillPDFext('PrescrAnchorForce',PDFdict,pdf,col_width,th,'kN/m.',2,'Prescr. anchor force:')
            else:
                pdf.cell(col_width1, 2*th, str('Prescr. anchor force:'), border=1)
                pdf.cell(col_width2, 2*th, str('N/A'), border=1)
                pdf.cell(col_width1, 2*th, str('kN/m'), border=1)
                pdf.ln(2*th)
        # Unit weight of wall
        pdf.cell(col_width1, 2*th, str('Mass of wall:'), border=1)
        pdf.cell(col_width2, 2*th, str(WallMass), border=1)
        pdf.cell(col_width1, 2*th, str('kg/m/m of wall'), border=1)
        pdf.ln(2*th)
        # Density of water
        pdf.cell(col_width1, 2*th, str('Water density, gam_w:'), border=1)
        pdf.cell(col_width2, 2*th, str(WaterDensity), border=1)
        pdf.cell(col_width1, 2*th, str('kN/m3'), border=1)
        pdf.ln(2*th)
        # State
        pdf.cell(col_width1, 2*th, str('State:'), border=1)
        pdf.cell(col_width2, 2*th, str(State), border=1)
        pdf.cell(col_width1, 2*th, str('-'), border=1)
        pdf.ln(2*th)
        # Slope back
        pdf.cell(col_width1, 2*th, str('Slope back:'), border=1)
        pdf.cell(col_width2, 2*th, str(SlopeBack), border=1)
        pdf.cell(col_width1, 2*th, str('deg.'), border=1)
        pdf.ln(2*th)
        # Slope front
        pdf.cell(col_width1, 2*th, str('Slope front:'), border=1)
        pdf.cell(col_width2, 2*th, str(SlopeFront), border=1)
        pdf.cell(col_width1, 2*th, str('deg.'), border=1)
        pdf.ln(2*th)
        # Soil profile
        pdf.cell(col_width1, 2*th, str('Soil profile:'), border=1)
        pdf.cell(col_width2, 2*th, str(SoilProfile), border=1)
        pdf.cell(col_width1, 2*th, str('-'), border=1)
        pdf.ln(2*th)
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.1 Characteristic soil parameters back", 
                ln = 13, align = 'L')
        
        ## Width of columns
        col_width1 = epw/12
        col_width2 = epw/6
        
        
        SoilData = [["z_top", "g_d", "g_m", "cu","c'","phi'","i","r","Description","Keep drained"],["m", "kN/m3", "kN/m3", "kN/m2","kN/m2","deg.","-","-","-","-"]]

        for i in range(0,len(SoilLayersBack)): 
            SoilData.append([format(float(SoilLayersBack[i].get('TopLayer')),'.2f'), 
                            format(float(SoilLayersBack[i].get('Gamma_d')),'.0f'), 
                            format(float(SoilLayersBack[i].get('Gamma_m')),'.0f'), 
                            format(float(SoilLayersBack[i].get('cu')),'.0f'), 
                            format(float(SoilLayersBack[i].get('c')),'.0f'), 
                            format(float(SoilLayersBack[i].get('phi')),'.0f'), 
                            format(float(SoilLayersBack[i].get('i')),'.1f'), 
                            format(float(SoilLayersBack[i].get('r')),'.2f'),
                            SoilLayersBack[i].get('Description'), SoilLayersBack[i].get('KeepDrained')])
                            
        for row in SoilData:
            for cellno, datum in enumerate(row):
                if cellno < 8:
                    # Enter data in column
                    pdf.cell(col_width1, 2*th, str(datum), border=1)
        
                else:
                    pdf.cell(col_width2, 2*th, str(datum), border=1)
        
            pdf.ln(2*th)
        
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.2 Characteristic soil parameters front", 
                ln = 13, align = 'L')
        
        SoilData = [["z_top", "g_d", "g_m", "cu","c'","phi'","i","r","Description","Keep drained"],["m", "kN/m3", "kN/m3", "kN/m2","kN/m2","deg.","-","-","-","-"]]

        for i in range(0,len(SoilLayersFront)): 
            SoilData.append([format(float(SoilLayersFront[i].get('TopLayer')),'.2f'), 
                            format(float(SoilLayersFront[i].get('Gamma_d')),'.0f'), 
                            format(float(SoilLayersFront[i].get('Gamma_m')),'.0f'), 
                            format(float(SoilLayersFront[i].get('cu')),'.0f'), 
                            format(float(SoilLayersFront[i].get('c')),'.0f'), 
                            format(float(SoilLayersFront[i].get('phi')),'.0f'), 
                            format(float(SoilLayersFront[i].get('i')),'.1f'), 
                            format(float(SoilLayersFront[i].get('r')),'.2f'),
                            SoilLayersFront[i].get('Description'), SoilLayersFront[i].get('KeepDrained')])
                            
        
        for row in SoilData:
            for cellno, datum in enumerate(row):
                if cellno < 8:
                    # Enter data in colums
                    pdf.cell(col_width1, 2*th, str(datum), border=1)
                else:
                    pdf.cell(col_width2, 2*th, str(datum), border=1)
        
            pdf.ln(2*th)
        
        ### WATER LEVELS
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
        pdf.cell(col_width, 2*th, str(WaterLevelBack), border=1)
        pdf.cell(col_width, 2*th, str(WaterLevelFront), border=1)
        pdf.ln(2*th)
        
        #### ADDITIONAL PRESSURE
        pdf.ln(2*th)
        if AddPressureProfile in ['AP1','AP2','AP3','AP4','AP5','AP6','AP7','AP8','AP9','AP10']:
            pdf.cell(200, 10, txt = "2.4 Additional pressure profile:"+' '+AddPressureProfile, 
                    ln = 4, align = 'L')
            
            zAP = ['z [m]']
            for elem in AddPress_z:
                zAP.append(elem)
            eAP = ['ez_k [kN/m2]']
            for elem in AddPress_ez:
                eAP.append(round(elem,1))
                
            eAPd = ['ez_d [kN/m2]']
            for elem in AddPress_ez_Design:
                eAPd.append(round(elem,1))
            
            AP = [zAP,eAP, eAPd]
            
            ## Width of columns
            col_width1 = epw/12
            col_width2 = epw/6
            
                
            for row in AP:
                for cellno, datum in enumerate(row):
                    if cellno > 0:
                        # Enter data in colums
                        pdf.cell(col_width1, 2*th, str(datum), border=1)
                    else:
                        pdf.cell(col_width2, 2*th, str(datum), border=1)
            
                pdf.ln(2*th)
        else:
            pdf.cell(200, 10, txt = "2.4 Additional pressure profile:"+' '+'no additional pressure', 
                    ln = 4, align = 'L')
        
        #### LOADS
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
        pdf.cell(col_width, 2*th, str(zR), border=1)
        pdf.cell(col_width, 2*th, str(LoadBack), border=1)
        pdf.cell(col_width, 2*th, str(LoadFront), border=1)
        pdf.cell(col_width*2, 2*th, str(AxialWallLoad), border=1)
        pdf.ln(2*th)
        
        #### SAFETY
        # partial safety factors
        col_width1 = epw*3/12
        col_width2 = epw/12
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.6 Safety", 
                ln = 4, align = 'L')
        pdf.cell(col_width1, 2*th, str('Alpha'), border=1)
        pdf.cell(col_width2, 2*th, str(Alpha), border=1)
        pdf.ln(2*th)
        pdf.cell(col_width1, 2*th, str('Consequence class:'), border=1)
        pdf.cell(col_width2, 2*th, str(ConsequenceClass), border=1)
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
        
        ### FAILURE MODE
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.7 Failure mode", 
                ln = 5, align = 'L')
        if AnchorLevel != None:
            pdf.cell(col_width2*3, 2*th, 'Anchored wall', border=1)
        else:
            pdf.cell(col_width2*3, 2*th, 'Free wall', border=1)
        pdf.ln(2*th)
        fail_coeff_header = ['iA', 'iB', 'iC']
        fail_coeff = [iA, iB, iC]
        for fail in fail_coeff_header:
            pdf.cell(col_width2, 2*th, str(fail), border=1)
        pdf.ln(2*th)
        
        for fail in fail_coeff:
            pdf.cell(col_width2, 2*th, str(fail), border=1)
        pdf.ln(2*th)
        
        ### KING POST WALL
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "2.8 King post wall", 
                ln = 6, align = 'L')
        if zB != None and WD != None and CC != None:
            kingpost_header = ['zB', 'WD', 'CC']
            kingpost_unit = ['m','m','m']
            kingpost = [zB, WD, CC]
            for kp in kingpost_header:
                pdf.cell(col_width2, 2*th, str(kp), border=1)
            pdf.ln(2*th)
            
            for kp in kingpost_unit:
                pdf.cell(col_width2, 2*th, str(kp), border=1)
            pdf.ln(2*th)
            
            for kp in kingpost:
                pdf.cell(col_width2, 2*th, str(kp), border=1)
        else:
            pdf.cell(200, 10, txt = "Not king post wall.", 
                ln = 6, align = 'L')
        pdf.ln(2*th)
        
        pdf.add_page('P')
        
        #### Results
        # Header
        pdf.set_font("Courier", size = 15) 
        pdf.cell(200, 10, txt = '3. Results', 
                ln = 6, align = 'L')
        
        pdf.ln(8)
        
        pdf.set_font("Courier", size = 12)
        pdf.cell(200, 10, txt = "3.1 Summary", 
                ln = 6, align = 'L')
        col_width1 = epw*6/12
        col_width2 = epw*2/12
        # Max. moment
        pdf.cell(col_width1, 2*th, str('Max. |moment|:'), border=1)
        pdf.cell(col_width2, 2*th, str(format(abs(MaxMoment),'.1f')), border=1)
        pdf.cell(col_width2, 2*th, str('kNm/m'), border=1)
        pdf.ln(2*th)
        # Max. shear force
        pdf.cell(col_width1, 2*th, str('Max. |shear force|:'), border=1)
        pdf.cell(col_width2, 2*th, str(format(abs(MaxShearForce),'.1f')), border=1)
        pdf.cell(col_width2, 2*th, str('kN/m'), border=1)
        pdf.ln(2*th)
        # Toe level
        pdf.cell(col_width1, 2*th, str('Toe level:'), border=1)
        pdf.cell(col_width2, 2*th, str(format(ToeLevel,'.1f')), border=1)
        pdf.cell(col_width2, 2*th, str('m'), border=1)
        pdf.ln(2*th)

        if AnchorLevel != None:
            # Anchor force
            pdf.cell(col_width1, 2*th, str('Anchor force, Ad:'), border=1)
            pdf.cell(col_width2, 2*th, str(format(AnchorForce,'.1f')), border=1)
            pdf.cell(col_width2, 2*th, str('kN/m'), border=1)
            pdf.ln(2*th)
            # Axial anchor force
            AnchorAxial = AnchorForce/np.cos(np.radians(AnchorInclination))
            pdf.cell(col_width1, 2*th, str('Axial anchor force:'), border=1)
            pdf.cell(col_width2, 2*th, str(format(AnchorAxial,'.1f')), border=1)
            pdf.cell(col_width2, 2*th, str('kN/m'), border=1)
            pdf.ln(2*th)
            # Moment at anchor
            pdf.cell(col_width1, 2*th, str('|Moment| at anchor level:'), border=1)
            pdf.cell(col_width2, 2*th, str(format(abs(float(MomentAtAnchor)),'.1f')), border=1)
            pdf.cell(col_width2, 2*th, str('kNm/m'), border=1)
            pdf.ln(2*th)
        # Tangential earth pressure resultant
        pdf.cell(col_width1, 2*th, str('Sum of tangential earth pressure*:'), border=1)
        pdf.cell(col_width2, 2*th, str(format(SumTanForce,'.1f')), border=1)
        pdf.cell(col_width2, 2*th, str('kN/m'), border=1)
        pdf.ln(2*th)
        # Sum of vertical forces
        pdf.cell(col_width1, 2*th, str('Sum of vertical forces*:'), border=1)
        if AnchorLevel != None:
            pdf.cell(col_width2, 2*th, str(format(SumTanForce-AnchorAxial*np.sin(np.radians(float(AnchorInclination)))-WeightWallTotal,'.1f')), border=1)
        else:
            pdf.cell(col_width2, 2*th, str(format(SumTanForce-WeightWallTotal,'.1f')), border=1)
        pdf.cell(col_width2, 2*th, str('kN/m'), border=1)
        pdf.ln(2*th)
        # Note
        pdf.cell(epw*10/12, 2*th, str('*Tangential pressure and vertical forces are positive upwards.'), border=1)
        pdf.ln(2*th)
        
        ## Pressure and structural forces
        pdf.ln(2*th)
        pdf.cell(200, 10, txt = "3.2 Pressure and structural forces", 
                ln = 6, align = 'L')
        
        col_width = epw/8
        forces_header = ['Level','e1','e2','dw','e-net','Ved','Med','Ju']
        forces_units = ['m','kN/m2','kN/m2','kN/m2','kN/m2','kN/m','kNm/m','-']
        for force in forces_header:
            pdf.cell(col_width, 2*th, str(force), border=1)
        pdf.ln(2*th)
        for force in forces_units:
            pdf.cell(col_width, 2*th, str(force), border=1)
        pdf.ln(2*th)
        for i in range(len(PlotLevels)):
            pdf.cell(col_width, 2*th, str(format(PlotLevels[i],'.1f')), border=1)
            pdf.cell(col_width, 2*th, str(format(e1[i],'.1f')), border=1)
            pdf.cell(col_width, 2*th, str(format(e2[i],'.1f')), border=1)
            pdf.cell(col_width, 2*th, str(format(DW[i],'.1f')), border=1)
            pdf.cell(col_width, 2*th, str(format(ENet[i],'.1f')), border=1)
            pdf.cell(col_width, 2*th, str(format(ShearForce[i],'.1f')), border=1)
            pdf.cell(col_width, 2*th, str(format(Moment[i],'.1f')), border=1)
            pdf.cell(col_width, 2*th, str(format(JU[i],'.1f')), border=1)
            pdf.ln(2*th)
            
        if UseAddOn == 'Yes':
            ## Sheet pile add on
            # Header
            pdf.set_font("Courier", size = 15) 
            pdf.cell(200, 10, txt = '4. Sheet pile add on', 
                    ln = 6, align = 'L')
            
            pdf.ln(2*th)
            pdf.set_font("Courier", size = 12)
            pdf.cell(200, 10, txt = "4.1 Input", 
                    ln = 6, align = 'L')
            
            col_width1 = epw*7/12
            col_width2 = epw*2/12
            # Use add on?
            pdf.cell(col_width1, 2*th, str('Add on active?:'), border=1)
            pdf.cell(col_width2, 2*th, str(UseAddOn), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # Limit state
            pdf.cell(col_width1, 2*th, str('Limit state:'), border=1)
            pdf.cell(col_width2, 2*th, str(LimitState), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # Control class
            pdf.cell(col_width1, 2*th, str('Control class:'), border=1)
            pdf.cell(col_width2, 2*th, str(ControlClass), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # Optimize
            pdf.cell(col_width1, 2*th, str('Optimize:'), border=1)
            pdf.cell(col_width2, 2*th, str(Optimize), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # Max utilization
            pdf.cell(col_width1, 2*th, str('Max. utilization:'), border=1)
            pdf.cell(col_width2, 2*th, str(MaxUtilization), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # fyk
            pdf.cell(col_width1, 2*th, str('fyk:'), border=1)
            pdf.cell(col_width2, 2*th, str(fyk), border=1)
            pdf.cell(col_width2, 2*th, str('MPa'), border=1)
            pdf.ln(2*th)
            # Beta B
            pdf.cell(col_width1, 2*th, str('Beta_B:'), border=1)
            pdf.cell(col_width2, 2*th, str(BetaB), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # Beta D
            pdf.cell(col_width1, 2*th, str('Beta_D:'), border=1)
            pdf.cell(col_width2, 2*th, str(BetaD), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # Design Life
            pdf.cell(col_width1, 2*th, str('Design life:'), border=1)
            pdf.cell(col_width2, 2*th, str(DesignLife), border=1)
            pdf.cell(col_width2, 2*th, str('Years'), border=1)
            pdf.ln(2*th)
            # Soil compaction
            pdf.cell(col_width1, 2*th, str('Soil compaction:'), border=1)
            pdf.cell(col_width2, 2*th, str(SoilDeposit), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            # corrosion rate at max. M, front
            pdf.cell(epw*11/12, 2*th, str('Corrosion rates (total)'), border=1)
            pdf.ln(2*th)
            pdf.cell(col_width1, 2*th, str('Level (m)'), border=1)
            pdf.cell(col_width2, 2*th, str('Rate'), border=1)
            pdf.cell(col_width2, 2*th, str('Unit'), border=1)
            pdf.ln(2*th)
            for i in range(len(tCor)):
                # total corrosion rates
                pdf.cell(col_width1, 2*th, str(tCorLevel[i]), border=1)
                pdf.cell(col_width2, 2*th, str(tCor[i]), border=1)
                pdf.cell(col_width2, 2*th, str('mm/yr'), border=1)
                pdf.ln(2*th)

            
            
            pdf.ln(2*th)
            pdf.set_font("Courier", size = 12)
            pdf.cell(200, 10, txt = "4.2 Results", 
                    ln = 6, align = 'L')
            col_width1 = epw*6/12
            col_width1a = epw*7/12
            col_width2 = epw*2/12
            col_width2a = epw*5/12
            
            # Sheet pile profile
            pdf.cell(col_width1, 2*th, str('Sheet pile profile:'), border=1)
            pdf.cell(col_width2a, 2*th, str(Sheetpile), border=1)
            pdf.ln(2*th)
            pdf.cell(col_width1a, 2*th, str('Max. relative utilization ratio:'), border=1)
            pdf.cell(col_width2, 2*th, str(u_rel), border=1)
            pdf.cell(col_width2, 2*th, str('-'), border=1)
            pdf.ln(2*th)
            pdf.cell(col_width1a, 2*th, str('Rotational capacity:'), border=1)
            pdf.cell(col_width2*2, 2*th, str(control_Rot), border=1)
            pdf.ln(2*th)
            pdf.cell(col_width1a, 2*th, str('Level (m)'), border=1)
            pdf.cell(col_width2*2, 2*th, str('Rel. utilisation ratio'), border=1)
            pdf.ln(2*th)
            try:
                for index, row in u_rel_lvl.iterrows():
                    print(index, row['u_rel'])
                    pdf.cell(col_width1a, 2*th, str(index), border=1)
                    pdf.cell(col_width2, 2*th, str(round(row['u_rel'],3)), border=1)
                    pdf.cell(col_width2, 2*th, str('-'), border=1)
                    pdf.ln(2*th)
            except:
                
                pass


        
        # save the pdf with name .pdf

        TemporaryPath = TemporaryWorkingDirectory()
        
        TemporaryPath = os.path.join(TemporaryPath, r'pdfresults.pdf')
        
        ## Save pdf
        pdf.output(TemporaryPath)
        
        
        return TemporaryPath