from SpooksHelperLib.Utils import utils
from SpooksHelperLib.Generators import generators
from SpooksHelperLib.SoilProfiles import soilprofiles
from SpooksHelperLib.SPOOKS import spooksfile

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

def ReportFront(VerticalEquilibriumOutput,OutputDirList,Version):
    
    print('Generating report front...')

    GetResultsOutput = VerticalEquilibriumOutput.get('GetResultsOutput')
        
    Analysis = VerticalEquilibriumOutput.get('Analysis')
    Project = Analysis.get('Project')
    Subject = Analysis.get('Subject')
    AnalysisNo = Analysis.get('AnalysisNo')
    State = Analysis.get('State')
    SoilLayersFront = Analysis.get('SoilLayersFront')
    SoilLayersBack = Analysis.get('SoilLayersBack')
    PlotResults = GetResultsOutput.get('PlotResults')
    PlotLevels = PlotResults.get('PlotLevels')
    e1 = PlotResults.get('e1')
    e2 = PlotResults.get('e2')
    Moment = PlotResults.get('Moment')
    MaxMoment = PlotResults.get('MaxMoment')
    ShearForce = PlotResults.get('ShearForce')
    zT = Analysis.get('zT')
    SlopeFront = Analysis.get('SlopeFront')
    SlopeBack = Analysis.get('SlopeBack')
    LoadFront = Analysis.get('LoadFront')
    LoadBack = Analysis.get('LoadBack')
    zR = Analysis.get('LevelLoadBack')
    WaterLevelFront = Analysis.get('WaterLevelFront')
    WaterLevelBack = Analysis.get('WaterLevelBack')
    AnchorLevel = Analysis.get('AnchorLevel')
    AnchorForce = GetResultsOutput.get('Results').get('AnchorForce')
    AnchorInclination = Analysis.get('AnchorInclination')
    SumTanForce = VerticalEquilibriumOutput.get('SumTanForce')
    WallSpecificWeight = Analysis.get('WallMass') * 9.82 / 1000
    DateTime = GetResultsOutput.get('DateTime')
    OutputDir = OutputDirList[-1]
    
    ### Max soil layer level back
    SoilLevelsBack = []
    for SoilLayer in SoilLayersBack:
        SoilLevelsBack.append(SoilLayer.get('TopLayer'))
    GroundLevelBack = max(SoilLevelsBack)
    
    ### Max soil layer level front
    SoilLevelsFront = []
    for SoilLayer in SoilLayersFront:
        SoilLevelsFront.append(SoilLayer.get('TopLayer'))
    GroundLevelFront = max(SoilLevelsFront)
    
    ToeLevel = GetResultsOutput.get('Results').get('ToeLevel')
    if ToeLevel == 'N/A':
        ToeLevel = GroundLevelFront - 0.1
    print(ToeLevel)
    
    try:
        WeightWallTotal = WallSpecificWeight * (zT - ToeLevel)
    except TypeError:
        WeightWallTotal = 'N/A'
    print(WeightWallTotal)
    
    
    
    
    ### Turning interactive plotting off
    plt.ioff()
        
    ## Customising math text
    plt.rcParams.update(plt.rcParamsDefault)
    
    plt.rcParams['mathtext.fontset'] = 'custom'
    plt.rcParams['mathtext.rm'] = 'Arial'
    
    ######## Cubic interpolation of moment curve (smoothing of moment curve)##
    level_plot_unique = [] ## list of unique level values
    m_plot_unique = []
    for i in range(len(PlotLevels)-1):
        if PlotLevels[i] != PlotLevels[i+1]:
            level_plot_unique.append(PlotLevels[i])
            m_plot_unique.append(Moment[i])
    
    level_plot_unique.append(PlotLevels[-1])
    m_plot_unique.append(Moment[-1])
    
    x = np.asarray(level_plot_unique)
    y = np.asarray(m_plot_unique)
    m_curve = interp1d(x, y, kind='quadratic')
    
    curve_level = np.linspace(min(level_plot_unique),max(level_plot_unique) , 100)
    ############## End of cubic interpolation ###############################
    

    
    #### Ground levels for graphic representation
    maxval = max(max(ShearForce),max(e1),max(e2),max(Moment))
    minval = min(min(ShearForce),min(e1),min(e2),min(Moment))
    grnextent = max(abs(minval),abs(maxval))
    ## Plot limits
    xmin = grnextent*1.05*-1
    xmax = grnextent*1.05
    ymin = ToeLevel-0.02*(float(zT)-ToeLevel)
    ymax = float(zT)+0.1*(float(zT)-ToeLevel)
    ### Aspect ratio (for graphical proportionality)
    aspectratio = ((xmax-xmin)/6.41) / ((ymax-ymin)/9.00)  ## 6.41 and 9.00 are the respective frame dimensions
    grnextent_front = [0, grnextent*-1]
    grnlevel_front = [GroundLevelFront, GroundLevelFront-grnextent_front[1]*np.tan(np.radians(SlopeFront))/aspectratio]
    grnextent_back = [0,grnextent]
    grnlevel_back = [GroundLevelBack, GroundLevelBack+grnextent_back[1]*np.tan(np.radians(SlopeBack))/aspectratio]
    
    #### Water levels for graphic representation
    waterlvl_front = [WaterLevelFront-0.005*(ymax-ymin), WaterLevelFront-0.005*(ymax-ymin)]
    waterlvl_back = [WaterLevelBack-0.005*(ymax-ymin), WaterLevelBack-0.005*(ymax-ymin)]
        
    #### Graphic wall parameters
    wall_x = [0,0] ## horisontal location of wall
    wall_y = [zT, ToeLevel]

    ### Assigning figure for report
    fig = plt.figure(num=None, figsize=(8, 8), dpi=80, facecolor='w', edgecolor='k')
    
    ### Forces, pressures and structures
    ## Earth pressures
    plt.plot(e1,PlotLevels, alpha = 1.0, color = 'mediumseagreen', label = '$e_{1}$, $e_{2}$ [kPa]', linewidth = 1.0)
    plt.plot(e2,PlotLevels, alpha = 1.0, color = 'mediumseagreen', linewidth = 1.0)
    ## Structural forces
    ### Smoothened moment curve
    plt.plot(m_curve(curve_level),curve_level, alpha = 1.0, color = 'red', label = '$M_{Ed}$ [kNm/m]', linewidth = 1.0)
    plt.plot(ShearForce,PlotLevels, alpha = 1.0, color = 'grey', label = '$V_{Ed}$ [kN/m]', linewidth = 1.0)
    ## Sheet pile wall
    plt.plot(wall_x,wall_y, alpha = 1.0, color = 'black', linewidth = 1.5)
    ## Ground level front/back
    plt.plot(grnextent_back,grnlevel_back, alpha = 1.0, color = 'black', linewidth = 1.5)
    plt.plot(grnextent_front,grnlevel_front, alpha = 1.0, color = 'black', linewidth = 1.5)
    ## Water level fron/back
    plt.plot(grnextent_back, waterlvl_back, alpha = 1.0, color = 'dodgerblue', linewidth = 1.2, linestyle='dashed')
    plt.plot(grnextent_front, waterlvl_front, alpha = 1.0, color = 'dodgerblue', linewidth = 1.2, linestyle='dashed')
    
    ### Anchor
    if AnchorLevel != None:
        ## Axial anchor force
        AnchorAxial = AnchorForce/np.cos(np.radians(AnchorInclination))
        plt.annotate("", xy=(1.5*aspectratio, AnchorLevel), xytext=(0.0, AnchorLevel), arrowprops=dict(headwidth=15, headlength=10, width=0.1, color='black'))

    
    ### WinSpooks Plug-in text
    props = dict(boxstyle='round', facecolor='white', alpha=0.0)
    plt.text(grnextent*-1, ymin+(ymax-ymin)*0.02, 'COWI WinSpooks Plug-in '+Version+' ,'+DateTime+'\n'+'Saved to: '+OutputDir, fontsize=5.0, verticalalignment='top', bbox=props)
    
    plt.ylabel('Level [m]')
    plt.title(Project+', '+Subject+', '+'Calc. no. '+str(AnalysisNo))
    plt.ylim(top=ymax, bottom=ymin)
    plt.xlim(xmin, xmax)
    plt.legend(loc='upper right')
    
    ### Text box soil parameters
    for i in range(0,len(SoilLayersBack)):  ## soil stratigraphies back excluding ground level
        
        SoilLayer = SoilLayersBack[i]
        
        if float(SoilLayer.get('TopLayer')) > ToeLevel: ## does not plot soil layers deeper than toe level
        
            if i > 0:
                Stratigraphy = [SoilLayer.get('TopLayer'), SoilLayer.get('TopLayer')]
                plt.plot(grnextent_back, Stratigraphy, alpha = 0.8, color = 'black', linewidth = 1.0)
            
            if State.lower() == 'drained' or SoilLayer.get('KeepDrained') == 'Yes':
                                        
                textstr = ', '.join((
                r'$\rm \gamma_d/ \gamma_m=%.0f/%.0f$ $\rm kN/m^{3}$' % (SoilLayer.get('Gamma_d'),SoilLayer.get('Gamma_m')),
                r'$\rm \phi\prime_{k}=%.0f ^{\circ}$' % (SoilLayer.get('phi'), ),
                r'$\rm c\prime_{k}=%.0f$ $\rm kPa$' % (SoilLayer.get('c'), ),
                r'$\rm r=%.1f$' % (SoilLayer.get('r'), ),
                r'$\rm i=%.1f$' % (SoilLayer.get('i'), )))
                textstr = '\n'.join((SoilLayer.get('Description'),textstr))
                props = dict(boxstyle='round', facecolor='grey', alpha=0.0)
            
            elif State.lower() == 'undrained' and SoilLayer.get('KeepDrained') == 'No':
                
                textstr = ', '.join((
                r'$\rm \gamma_d/\gamma_m=%.0f/%.0f$ $\rm kN/m^{3}$' % (SoilLayer.get('Gamma_d'),SoilLayer.get('Gamma_m')),
                r'$\rm cu_{k}=%.0f$ $\rm kPa$' % (SoilLayer.get('cu'), ),
                r'$\rm r=%.1f$' % (SoilLayer.get('r'), ),
                r'$\rm i=%.1f$' % (SoilLayer.get('i'), )))
                textstr = '\n'.join((SoilLayer.get('Description'),textstr))
                props = dict(boxstyle='round', facecolor='grey', alpha=0.0)
                
            
            if i != len(SoilLayersBack)-1 and SoilLayersBack[i+1].get('TopLayer') > ToeLevel: ## Vertical position of soil parameters data
                VertPos = (SoilLayer.get('TopLayer') + SoilLayersBack[i+1].get('TopLayer'))/2
            else:
                VertPos = (SoilLayer.get('TopLayer') + ToeLevel) / 2
            plt.text(grnextent*0.05, VertPos, textstr, fontsize=8.0, verticalalignment='center', bbox=props)
    
    
    for i in range(0,len(SoilLayersFront)):  ## soil stratigraphies front excluding ground level
        
        SoilLayer = SoilLayersFront[i]
        
        if float(SoilLayer.get('TopLayer')) > ToeLevel: ## does not plot soil layers deeper than toe level
        
            if i > 0:
                Stratigraphy = [SoilLayer.get('TopLayer'), SoilLayer.get('TopLayer')]
                plt.plot(grnextent_front, Stratigraphy, alpha = 0.8, color = 'black', linewidth = 1.0)
            
            if State.lower() == 'drained' or SoilLayer.get('KeepDrained') == 'Yes':
                
                textstr = ', '.join((
                r'$\rm \gamma_d/ \gamma_m=%.0f/%.0f$ $\rm kN/m^{3}$' % (SoilLayer.get('Gamma_d'),SoilLayer.get('Gamma_m')),
                r'$\rm \phi\prime_{k}=%.0f ^{\circ}$' % (SoilLayer.get('phi'), ),
                r'$\rm c\prime_{k}=%.0f$ $\rm kPa$' % (SoilLayer.get('c'), ),
                r'$\rm r=%.1f$' % (SoilLayer.get('r'), ),
                r'$\rm i=%.1f$' % (SoilLayer.get('i'), )))
                textstr = '\n'.join((SoilLayer.get('Description'),textstr))
                props = dict(boxstyle='round', facecolor='grey', alpha=0.0)
            
            elif State.lower() == 'undrained' and SoilLayer.get('KeepDrained') == 'No':
                
                textstr = ', '.join((
                r'$\rm \gamma_d/\gamma_m=%.0f/%.0f$ $\rm kN/m^{3}$' % (SoilLayer.get('Gamma_d'),SoilLayer.get('Gamma_m')),
                r'$\rm cu_{k}=%.0f$ $\rm kPa$' % (SoilLayer.get('cu'), ),
                r'$\rm r=%.1f$' % (SoilLayer.get('r'), ),
                r'$\rm i=%.1f$' % (SoilLayer.get('i'), )))
                textstr = '\n'.join((SoilLayer.get('Description'),textstr))
                props = dict(boxstyle='round', facecolor='grey', alpha=0.0)
                
            
            if i != len(SoilLayersFront)-1 and SoilLayersFront[i+1].get('TopLayer') > ToeLevel: ## Vertical position of soil parameters data
                VertPos = (SoilLayer.get('TopLayer') + SoilLayersFront[i+1].get('TopLayer'))/2
            else:
                VertPos = (SoilLayer.get('TopLayer') + ToeLevel) / 2
            plt.text(grnextent_front[1], VertPos, textstr, fontsize=8.0, verticalalignment='center', bbox=props)
            
            
    ### PLOT LOADS
    ## front load
    textstr = ''.join(r'$\rm q_{fk}=%.0f$ $\rm kPa$' % (LoadFront), )
    plt.text((grnextent_front[0] + grnextent_front[1])/2, grnlevel_front[0], textstr, fontsize=8.0, verticalalignment='bottom', bbox=props)
    ## back load
    textstr = ''.join(r'$\rm q_{bk}=%.0f$ $\rm kPa$' % (LoadBack), )
    plt.text((grnextent_back[0] + grnextent_back[1])/2, grnlevel_back[0], textstr, fontsize=8.0, verticalalignment='bottom', bbox=props)
        

    ### Text box results
    if AnchorLevel != None:
        textstr = '\n'.join((
        r'$\rm |M_{Ed,max}|=%.0f$ kNm/m' % (float(abs(MaxMoment)), ),
        #r'$\rm V_{Ed,max}=%.1f$ kN/m' % (vmax, ),
        r'$\rm Toe_{level}=%.1f$ m' % (float(ToeLevel), ),
        r'$\rm A_{d}=%.0f$ kN/m' % (float(AnchorForce), ),
        r'$\rm \Sigma F↑=%.0f$ kN/m' % (float(SumTanForce-WeightWallTotal-AnchorAxial*np.sin(np.radians(AnchorInclination))), )))
        props = dict(boxstyle='round', facecolor='grey', alpha=0.1)
        plt.text(-1*grnextent, ymax-0.017*(ymax-ymin), textstr, fontsize=10, verticalalignment='top', bbox=props)
   
    else:
        textstr = '\n'.join((
        r'$\rm |M_{Ed,max}|=%.0f$ kNm/m' % (float(abs(MaxMoment)), ),
        #r'$\rm V_{Ed,max}=%.1f$ kN/m' % (vmax, ),
        r'$\rm Toe_{level}=%.1f$ m' % (float(ToeLevel), ),
        r'$\rm \Sigma F↑=%.0f$ kN/m' % (float(SumTanForce-WeightWallTotal), )))
        props = dict(boxstyle='round', facecolor='grey', alpha=0.1)
        plt.text(-1*grnextent, ymax-0.017*(ymax-ymin), textstr, fontsize=10, verticalalignment='top', bbox=props)
   
    
    ### Text box logo
    plt.text(grnextent, ymin,'COWI', fontsize=20, fontname='Century Schoolbook', color='orangered',ha='right', va='bottom', alpha=1.0)
    
    fig.set_size_inches(8.27,11.69)

    
    ## Save report front plot in temporary working directory
    
    TemporaryPath = TemporaryWorkingDirectory()
    
    TempReportFrontPath = os.path.join(TemporaryPath, r'ReportFront.pdf')
    
    # plt.savefig(TempReportFrontPath, dpi='figure', facecolor='w', edgecolor='w',
    #     orientation='portrait', format='pdf',
    #     transparent=False, bbox_inches=None, pad_inches=0.05,
    #     frameon=None, metadata=None)
    
    plt.savefig(TempReportFrontPath, dpi='figure', facecolor='w', edgecolor='w',
        orientation='portrait', format='pdf',
        transparent=False, bbox_inches=None, pad_inches=0.05, metadata=None)
    
    
    ## Close figures
    plt.close()
    
    return TempReportFrontPath
