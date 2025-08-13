import numpy as np

from SpooksHelperLib.Analysis import analysisclass
from SpooksHelperLib.Generators import generators
from SpooksHelperLib.SoilProfiles import soilprofiles
from SpooksHelperLib.SPOOKS import spooksfile
from SpooksHelperLib.Utils import utils
from SpooksHelperLib.SPOOKS import spooksfile

class verticalEquilibrium():
    def soilLayer(self, soillayer):
        retarr = []
        for soil in soillayer:
            retarr.append(soil.get('Toplayer'))
        groundlevel = max(retarr)
        
        return(retarr,groundlevel)
        

        #Parameters:
            #GetResultsOutput (obj or dict i think) output values
            #DesignSoilLayers (str) which soillayer 
            #State (str): 'drained' or 'undrained'
            #i (int): Current index in loop
    def compute_tangential_force(GetResultsOutput, DesignSoilLayers, State, i):
        tan_force = 0
        PlotLevels = GetResultsOutput.get('PlotResults').get('PlotLevels')
        e = ""

        if DesignSoilLayers == 'DesignSoilLayersBack':
            e = GetResultsOutput.get('PlotResults').get('e1')
        elif DesignSoilLayers == 'DesignSoilLayersFront':
            e = GetResultsOutput.get('PlotResults').get('e2')
        else: e = "Unknown Error"

        (SoilLevels, GroundLevel) = SoilLayer(GetResultsOutput.get('Analysis').get(DesignSoilLayers))

        if GetResultsOutput.get('PlotResults').get('PlotLevels')[i+1] < GroundLevel:
            force = abs(np.trapz(e[i:i+2], PlotLevels[i:i+2]))  # Area under pressure curve

            if DesignSoilLayers == 'DesignSoilLayersFront' and PlotLevels[i] == GroundLevel:
                index = 0
            else:
                index = [j for j, k in enumerate(SoilLevels) if float(k) > PlotLevels[i+1]]
                index = index[-1]  # Closest soil layer above

            SoilLayer = DesignSoilLayers[index]

            if State.lower() == 'drained' or SoilLayer.get('KeepDrained') == 'Yes':
                tan_delta = float(SoilLayer.get('r')) * np.tan(np.radians(SoilLayer.get('phi')))
                tan_force = force * tan_delta + float(SoilLayer.get('c')) * (PlotLevels[i] - PlotLevels[i+1]) * float(SoilLayer.get('r'))
            elif State.lower() == 'undrained' and SoilLayer.get('KeepDrained') == 'No':
                tan_force = float(SoilLayer.get('cu')) * (PlotLevels[i] - PlotLevels[i+1]) * float(SoilLayer.get('r'))

        return tan_force


    def VerticalEquilibrium(self, GetResultsOutput):
        
        ### tangential earthpressure calculated as qs = e * tan(delta) + adhesion , where r = tan(delta)/tan(phi) = adhesion/cohesion
        ### for undrained layers qs = cu * r
        
        Analysis = GetResultsOutput.get('Analysis')
        
        ## Initialise
        sum_tanforce_back = 0  
        sum_tanforce_front = 0
        
        
        for i in range(len(GetResultsOutput.get('PlotResults').get('e1'))-1):
        
            ##### back side of wall (active)
            tan_force_back = self.compute_tangential_force('DesignSoilLayersBack', GetResultsOutput.get('Analysis').get('State'), i)
                ## Sum of tangential forces back    
            sum_tanforce_back = sum_tanforce_back + abs(tan_force_back)
            
            ##### Front side of wall (passive)
            tan_force_front = self.compute_tangential_force('DesignSoilLayersFront', GetResultsOutput.get('Analysis').get('State'), i)
                ## Sum of tangential forces front
            sum_tanforce_front = sum_tanforce_front + abs(tan_force_front)

        ## Total sum of tangential forces
        sum_tanforce = sum_tanforce_front - sum_tanforce_back - Analysis.get('AxialWallLoad')
        
        
        VerticalEquilibriumOutput = {'Analysis': Analysis,
                                    'GetResultsOutput': GetResultsOutput,
                                    'SumTanForceBack':  sum_tanforce_back,
                                    'SumTanForceFront': sum_tanforce_front,
                                    'SumTanForce':      sum_tanforce}
            
            
        return VerticalEquilibriumOutput
    
    def SPOOKSFeeder(input_path,calcno,pb,tabcalc,logtxt,tk):    
        FeederOutput = []
        g = generators()
        
        
        GeneratedAnalyses = g.GenerateAnalyses(input_path)
        
        
        ## Progress bar maximum
        pb['maximum'] = len(GeneratedAnalyses)-1
        pb.update() ## update progress bar
        
        ## Loop through all generated analyses and append output to FeederOutput
        ReportErrors = []
        for Analysis in GeneratedAnalyses:
            #print(Analysis)
            
            ### PROGRESS BAR AND CALCULATION NO UPDATE
            AnalysisNo = Analysis.get('AnalysisNo')
            calcno.configure(text = str(AnalysisNo)) ## Calculation number for GUI
            tabcalc.update_idletasks()
            pb['value'] = AnalysisNo
            pb.update() ## update progress bar
            sf = spooksfile()
            ExecuteOutput = sf.ExecuteSPOOKS(Analysis,logtxt,tk)
            
            ReportErrors = ExecuteOutput.get('Errors')
        
            GetResultsOutput = sf.GetResults(ExecuteOutput)
        
        
        #else:
        #    print("FAILED")
        #    calcno.configure(text = 'Calculation failed') ## Calculation number for GUI
        #    tabcalc.update_idletasks()
        #    break

                
            
            FeederOutput.append({'FeedAnalysis': Analysis,
                                'ExecuteOutput': ExecuteOutput,
                                'GetResultsOutput': GetResultsOutput})
            
        
        return FeederOutput