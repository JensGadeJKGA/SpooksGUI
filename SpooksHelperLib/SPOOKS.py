
import os
from SpooksHelperLib.Utils import utils
from SpooksHelperLib.SoilProfiles import soilprofiles

class spooksfile():
    def anchorLevel(Anchorlevel, PrescrbAnchorForce, anchCoeffVars):
        baseArr = [format(anchCoeffVars["iA"],'.2f'), 
                        format(anchCoeffVars["iB"],'.2f'),
                        format(anchCoeffVars["iC"],'.2f'), 
                        format(anchCoeffVars["zT"],'.2f'), 
                        format(anchCoeffVars["zR"],'.2f')]
        
        ## If no anchor
        if Anchorlevel == None: 

            if format(anchCoeffVars["iB"],'.2f') != '1.00' or format(anchCoeffVars["iB"],'.2f') != '0.00':
                print('No compatibility between failure mode and failure coefficients')
                return ['N/A', 
                            'N/A',
                            'N/A', 
                            'N/A', 
                            'N/A']
            else:
                return baseArr
        
        # if anchor and no prescribed anchor force
        elif Anchorlevel != None and PrescrbAnchorForce == 0.00: 
            baseArr.append(format(Anchorlevel,'.2f'))

            return baseArr
        
        # if anchor and prescribed anchor force
        elif Anchorlevel != None and PrescrbAnchorForce != 0.00 and format(anchCoeffVars["iC"],'.2f') == '0.00' and float(anchCoeffVars["iB"]) > 0: 
            baseArr.append(format(Anchorlevel,'.2f'))
            baseArr.append(format(PrescrbAnchorForce,'.2f'))

            return baseArr
        
        
           
        

    def GenerateSPOOKSInputFile(self, Analysis):
        State = Analysis.get('State')

        Geninf = [format(Analysis.get('SlopeFront'),'.2f'), 
                format(Analysis.get('SlopeBack'),'.2f'),
                format(Analysis.get('DesignLoadFront'),'.2f'), 
                format(Analysis.get('DesignLoadBack'),'.2f'), 
                format(Analysis.get('WaterLevelFront'),'.2f'), 
                format(Analysis.get('WaterLevelBack'),'.2f'), 
                format(Analysis.get('WaterDensity'),'.2f')]
    
        Generalinfo = utils.AddSpaces(Geninf)
        ############ First lines in SPOOKSWAT input file (L)
        
        L = ['<', 'Project:' +' '+ Analysis.get('Project'), 'Initials:' +' '+ Analysis.get('Initials'), 'Subject:' +' '+str(Analysis.get('Subject')), '>', '<', Generalinfo, '>', '<']
        
        
        
        ################# SOIL FRONT ####################################

        L=soilprofiles.designsoillayer(Analysis.get('DesignSoilLayersFront'), State, L)
    
        ########################## SOIL BACK ##############################

        L=soilprofiles.designsoillayer(Analysis.get('DesignSoilLayersBack'), State, L)
        
        ################## FAILURE MODE (ANCHOR COEFFICIENTS) ###################
        AnchCoeffVars = {
            "iA": Analysis.get('iA'),
            "iB": Analysis.get('iB'),
            "iC": Analysis.get('iC'),
            "zT": Analysis.get('zT'),
            "zR": Analysis.get('LevelLoadBack')
        }
        Coeff_temp = self.anchorLevel(Analysis.get('AnchorLevel'), Analysis.get('PrescrbAnchorForce'), AnchCoeffVars)
        Coeff = utils.AddSpaces(Coeff_temp)
        L.append(Coeff)
        if Analysis.get('AnchorLevel') == None:
            L.append('                    ')
        
        ############ KING POST WALL PARAMETERS (if data is properly entered in excel input file)
        zB = Analysis.get('zB')
        WD = Analysis.get('WD')
        CC = Analysis.get('CC')

        if zB != None and WD != None and CC != None:
            
            KingPostParam = ""

            KingPostParam = utils.AddSpaces([format(zB,'.2f'),
                            format(WD,'.2f'),
                            format(CC,'.2f')])
            L.append('                                        ' + KingPostParam) #+40 init spaces
        
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
        
        if Analysis.get('AddPressureProfile') in ['AP1', 'AP2', 'AP3', 'AP4', 'AP5', 'AP6', 'AP7', 'AP8', 'AP9', 'AP10']:
        
            ## Additional pressure file
            addpressfile = []
        
            
            APlevel = utils.AddSpaces(Analysis.get('AddPress_z'))
            
            addpressfile.append(APlevel+'    ')
            addpressfile.append('  ')
            
            APvalue = utils.AddSpaces(Analysis.get('AddPress_ez'))
            
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