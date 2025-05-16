
import os
from SpooksHelperLib.Utils import utils
from SpooksHelperLib.SoilProfiles import soilprofiles

class spooksfile():
    def GenerateSPOOKSInputFile(Analysis):

        Project = Analysis.get('Project')
        Initials = Analysis.get('Initials')
        Checker = Analysis.get('Checker')
        Approver = Analysis.get('Approver')
        Subject = Analysis.get('Subject')
        SlopeFront = Analysis.get('SlopeFront')
        SlopeBack = Analysis.get('SlopeBack')
        LoadFront = Analysis.get('DesignLoadFront')
        LoadBack = Analysis.get('DesignLoadBack')
        WaterLevelBack = Analysis.get('WaterLevelBack')
        WaterLevelFront = Analysis.get('WaterLevelFront')
        WaterDensity = Analysis.get('WaterDensity')
        State = Analysis.get('State')
        DesignSoilLayersFront = Analysis.get('DesignSoilLayersFront')
        DesignSoilLayersBack = Analysis.get('DesignSoilLayersBack')
        iA = Analysis.get('iA')
        iB = Analysis.get('iB')
        iC = Analysis.get('iC')
        zT = Analysis.get('zT')
        zR = Analysis.get('LevelLoadBack')
        AnchorLevel = Analysis.get('AnchorLevel')
        PrescrbAnchorForce = Analysis.get('PrescrbAnchorForce')
        zB = Analysis.get('zB')
        WD = Analysis.get('WD')
        CC = Analysis.get('CC')
        AddPressureProfile = Analysis.get('AddPressureProfile')
        AddPress_z = Analysis.get('AddPress_z')
        AddPress_ez = Analysis.get('DesignAddPress_ez')
        
        Geninf = [format(SlopeFront,'.2f'), 
                format(SlopeBack,'.2f'),
                format(LoadFront,'.2f'), 
                format(LoadBack,'.2f'), 
                format(WaterLevelFront,'.2f'), 
                format(WaterLevelBack,'.2f'), 
                format(WaterDensity,'.2f')]
                
        
        Generalinfo = ""
        
        for item in Geninf: # creates the right amount of space between columns
            if len(str(item)) == 4:
                space = '      ' # 6 spaces
            if len(str(item)) == 5:
                space = '     '  # 5 spaces
            if len(str(item)) == 6:
                space = '    '   # 4 spaces
            Generalinfo += space + str(item)
        
        ############ First lines in SPOOKSWAT input file (L)
        
        L = ['<', 'Project:' +' '+ Project, 'Initials:' +' '+ Initials, 'Subject:' +' '+str(Subject), '>', '<', Generalinfo, '>', '<']
        
        
        
        ################# SOIL FRONT ####################################

        L=soilprofiles.designsoillayer(DesignSoilLayersFront, State, L)
    
        ########################## SOIL BACK ##############################

        L=soilprofiles.designsoillayer(DesignSoilLayersBack, State, L)
        
        ################## FAILURE MODE (ANCHOR COEFFICIENTS) ###################
        
        
        ## If no anchor
        if AnchorLevel == None: 

            if format(iB,'.2f') != '1.00' or format(iC,'.2f') != '0.00':
                print('No compatibility between failure mode and failure coefficients')
            
                Coeff_temp = ['N/A', 
                            'N/A',
                            'N/A', 
                            'N/A', 
                            'N/A']
            else:
                
                Coeff_temp = [format(iA,'.2f'), 
                            format(iB,'.2f'),
                            format(iC,'.2f'), 
                            format(zT,'.2f'), 
                            format(zR,'.2f')]
            
            Coeff = ""
        
            for item in Coeff_temp: # creates the right amount of space between columns
                if len(item) == 4:
                    space = '      ' # 6 spaces
                if len(item) == 5:
                    space = '     '  # 5 spaces
                if len(item) == 6:
                    space = '    '   # 4 spaces
                Coeff += space + item
                
            Endspace = '                    ' ## 20 end spaces (if no anchor)
            
            L.append(Coeff+Endspace)
            
        # if anchor and no prescribed anchor force
        elif AnchorLevel != None and PrescrbAnchorForce == 0.00: 
        
            Coeff_temp = [format(iA,'.2f'), 
                        format(iB,'.2f'),
                        format(iC,'.2f'), 
                        format(zT,'.2f'), 
                        format(zR,'.2f'),
                        format(AnchorLevel,'.2f')]
        
            Coeff = ""
        
            for item in Coeff_temp: # creates the right amount of space between columns
                if len(item) == 4:
                    space = '      ' # 6 spaces
                if len(item) == 5:
                    space = '     '  # 5 spaces
                if len(item) == 6:
                    space = '    '   # 4 spaces
                Coeff += space + item
                
            Endspace = '          ' ## 10 end spaces (if anchor but no prescribed force)
            
            L.append(Coeff+Endspace)
            
        
        # if anchor and prescribed anchor force
        elif AnchorLevel != None and PrescrbAnchorForce != 0.00 and format(iC,'.2f') == '0.00' and float(iB) > 0: 
        
            Coeff_temp = [format(iA,'.2f'), 
                        format(iB,'.2f'),
                        format(iC,'.2f'), 
                        format(zT,'.2f'), 
                        format(zR,'.2f'),
                        format(AnchorLevel,'.2f'),
                        format(PrescrbAnchorForce,'.2f')]
        
            Coeff = ""
        
            for item in Coeff_temp: # creates the right amount of space between columns
                if len(item) == 4:
                    space = '      ' # 6 spaces
                if len(item) == 5:
                    space = '     '  # 5 spaces
                if len(item) == 6:
                    space = '    '   # 4 spaces
                Coeff += space + item
            
            L.append(Coeff)
        
        
        ############ KING POST WALL PARAMETERS (if data is properly entered in excel input file)
            
        if zB != None and WD != None and CC != None:
            
            KingPost_temp = [format(zB,'.2f'),
                            format(WD,'.2f'),
                            format(CC,'.2f')]
            
            KingPostParam = ""
        
            for item in KingPost_temp: # creates the right amount of space between columns
                if len(str(item)) == 4:
                    space = '      ' # 6 spaces
                if len(str(item)) == 5:
                    space = '     '  # 5 spaces
                if len(str(item)) == 6:
                    space = '    '   # 4 spaces
                KingPostParam += space + str(item)
                
            Initspace = '                                        ' ## 40 inital spaces
            
            L.append(Initspace+KingPostParam)
        
        elif zB == None and WD == None and CC == None:
            
            L.append('')
        
        else:
            
            print('Improper King/Post wall parameters')
            
        
        ###### OUTPUT PATHS (SPOOKS working directory - temporary files)
        
        TemporaryPath = utils.TemporaryWorkingDirectory()
        
        ## output plot file path
        plotpath_output = os.path.join(TemporaryPath, r'spooks.plt')
        
        L.append('>'+'    '+plotpath_output)

        
        ############### ADDITIONAL PRESSURE FILE #########################
        
        if AddPressureProfile in ['AP1', 'AP2', 'AP3', 'AP4', 'AP5', 'AP6', 'AP7', 'AP8', 'AP9', 'AP10']:
        
            ## Additional pressure file
            addpressfile = []
        
            
            APlevel = ""
        
            for item in AddPress_z: # creates the right amount of space between columns

                item = format(float(item),'.2f')
                
                if len(item) == 4:
                    space = '      ' # 6 spaces
                if len(item) == 5:
                    space = '     '  # 5 spaces
                if len(item) == 6:
                    space = '    '   # 4 spaces
                APlevel += space + item
            
            addpressfile.append(APlevel+'    ')
            addpressfile.append('  ')
            
            APvalue = ""
        
            for item in AddPress_ez: # creates the right amount of space between columns
                
                item = format(float(item),'.2f')

                if len(item) == 4:
                    space = '      ' # 6 spaces
                if len(item) == 5:
                    space = '     '  # 5 spaces
                if len(item) == 6:
                    space = '    '   # 4 spaces
                APvalue += space + item
            
            addpressfile.append(APvalue+'    ')
            
            ### Generating additional pressure file for input file
            addpressurefile = os.path.join(TemporaryPath, r'addpressfile')
            
            with open(addpressurefile, 'w+') as f:
                for item in addpressfile:
                    f.write("%s\n" % item)
            
            f.close()
                        
            L.append('     '+addpressurefile)
            
        else:
            
            L.append('')
            
        ############### 4.10. END SPOOKSWAT INPUT FILE ###################
        
        L.append('>END')
        
        ###### Export to file
        
        inputfile = os.path.join(TemporaryPath, r'params')
        
        with open(inputfile, 'w+') as f:
            for item in L:
                f.write("%s\n" % item)
        
        f.close()
        
        
        Output = {'Analysis': Analysis,
                'InputFileDir': TemporaryPath,
                'InputFile': inputfile,
                'SPOOKSPlotFile': plotpath_output}
        
        
        return Output