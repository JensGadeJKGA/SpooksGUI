import numpy as np
import matplotlib.pyplot as plt

class plot:
    def __init__(self):
        pass

    def PlotResults(FeederOutput):
    
        print('Plotting results...')
        
        
        WallResults = []
        

        ## List of parent analysis numbers
        ParentAnalyses = []
        for Analysis in FeederOutput:
            
            GetResultsOutput = Analysis.get('GetResultsOutput')
            ParentAnalyses.append(GetResultsOutput.get('Analysis').get('ParentAnalysis'))
        
        ParentAnalyses = list(np.unique(ParentAnalyses))
        
        for ParentAnalysis in ParentAnalyses:
            
            WallResults.append({'ParentAnalysis': ParentAnalysis,
                                'Subject' : [],
                                'PlotIDs': [],
                                'MaxMoments': [],
                                'MaxShearForces': [],
                                'ToeLevels': [],
                                'AnchorForces': []})
            
            
        for WallResult in WallResults:
            
            ParentAnalysis = WallResult.get('ParentAnalysis')
            
        
            ## ID for plotting
            PlotID = 0
        
            for Analysis in FeederOutput:
                
                GetResultsOutput = Analysis.get('GetResultsOutput')
                
                MaxMomentAnalysis = GetResultsOutput.get('PlotResults').get('MaxMoment')
                
                MaxShearForceAnalysis = GetResultsOutput.get('PlotResults').get('MaxShearForce')
                
                ToeLevel = GetResultsOutput.get('Results').get('ToeLevel')
                
                AnchorForce = GetResultsOutput.get('Results').get('AnchorForce')
                
                ParentAnalysisInput = GetResultsOutput.get('Analysis').get('ParentAnalysis')
                
                Subject = GetResultsOutput.get('Analysis').get('Subject')
                
                if ParentAnalysisInput == ParentAnalysis:
                    
                    WallResult.get('Subject').append(Subject)
                    WallResult.get('PlotIDs').append(PlotID)
                    WallResult.get('MaxMoments').append(abs(MaxMomentAnalysis))
                    WallResult.get('MaxShearForces').append(abs(MaxShearForceAnalysis))
                    WallResult.get('ToeLevels').append(ToeLevel)
                    
                    if isinstance(AnchorForce,float):
                        
                        WallResult.get('AnchorForces').append(AnchorForce)
                    else:
                        WallResult.get('AnchorForces').append(0.00)
                
                    ## Updating Plot ID
                    PlotID = PlotID + 1
                
        fig = plt.figure()
        #fig.canvas.set_window_title('WinSpooks Plug-in results')
        ### Max. moment
        ax1 = fig.add_subplot(221)
        color = 'black'
        for Results in WallResults:
            plt.plot(Results.get('PlotIDs'),Results.get('MaxMoments'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
        ax1.set_ylabel('Max. |bending moment| [kNm/m]', color = color)
        ax1.tick_params(axis='y', labelcolor = color)
        plt.grid()
        plt.legend()    


        ax2 = fig.add_subplot(222)
        color = 'black'
        for Results in WallResults:
            plt.plot(Results.get('PlotIDs'),Results.get('MaxShearForces'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
        ax2.set_ylabel('Max. |shear force| [kN/m]', color = color)
        ax2.tick_params(axis='y', labelcolor = color)
        plt.grid()
        plt.legend()
        
        ### Anchor force
        ax3 = fig.add_subplot(223)
        color = 'black'
        for Results in WallResults:
            plt.plot(Results.get('PlotIDs'), Results.get('AnchorForces'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
        ax3.set_ylabel('Anchor force [kN/m]', color = color)
        ax3.set_xlabel('Plot ID')
        ax3.tick_params(axis='y', labelcolor = color)
        plt.grid()
        plt.legend()

        ### Toe level
        ax4 = fig.add_subplot(224)
        color = 'black'
        for Results in WallResults:
            plt.plot(Results.get('PlotIDs'), Results.get('ToeLevels'), marker = 'o', alpha = 0.4, label = Results.get('Subject')[0])
        ax4.set_ylabel('Toe level [m]', color = color)
        ax4.set_xlabel('Plot ID')
        ax4.tick_params(axis='y', labelcolor = color)
        plt.grid()
        plt.legend()
        plt.show()


              



