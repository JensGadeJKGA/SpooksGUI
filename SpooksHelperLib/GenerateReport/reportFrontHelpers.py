import os
from scipy.interpolate import interp1d
import numpy as np

class reportFrontHelpers:
    def generateReportDict(VerticalEquilibriumOutput, OutputDirList):
        GetResultsOutput = VerticalEquilibriumOutput.get('GetResultsOutput')

        Analysis = VerticalEquilibriumOutput.get('Analysis')
        PlotResults = GetResultsOutput.get('PlotResults')
        reportDict = {
            'Analysis': Analysis,
            'Project': Analysis.get('Project'),
            'Subject': Analysis.get('Subject'),
            'AnalysisNo': Analysis.get('AnalysisNo'),
            'State': Analysis.get('State'),
            'SoilLayersFront': Analysis.get('SoilLayersFront'),
            'SoilLayersFront': Analysis.get('SoilLayersBack'),
            'PlotResults': PlotResults,
            'PlotLevels': PlotResults.get('PlotLevels'),
            'e1': PlotResults.get('e1'),
            'e2': PlotResults.get('e2'),
            'Moment': PlotResults.get('Moment'),
            'MaxMoment': PlotResults.get('MaxMoment'),
            'ShearForce': PlotResults.get('ShearForce'),
            'zT': Analysis.get('zT'),
            'SlopeFront': Analysis.get('SlopeFront'),
            'SlopeBack': Analysis.get('SlopeBack'),
            'LoadFront': Analysis.get('LoadBack'),
            'LoadBack': Analysis.get('LoadBack'),
            'zR': Analysis.get('LevelLoadBack'),
            'WaterLevelFront': Analysis.get('WaterLevelFront'),
            'WaterLevelBack': Analysis.get('WaterLevelBack'),
            'AnchorLevel': Analysis.get('AnchorLevel'),
            'AnchorForce': GetResultsOutput.get('Results').get('AnchorForce'),
            'AnchorInclination': Analysis.get('AnchorInclination'),
            'SumTanForce': VerticalEquilibriumOutput.get('SumTanForce'),
            'WallSpecificWeight': Analysis.get('WallMass') * 9.82 / 1000,
            'DateTime': GetResultsOutput.get('DateTime'),
            'OutputDir': OutputDirList[-1]

        }
        return reportDict

    def TemporaryWorkingDirectory():
        

        user = "MLHU"
        
        ## output path
        TemporaryPath = os.path.join(r'C:\Users', user)
        TemporaryPath = os.path.join(TemporaryPath, r'AppData\Local\Temp\2')
        
        if not os.path.exists(TemporaryPath): ## if directory does not exist -> create it
            os.makedirs(TemporaryPath)
            
        return TemporaryPath

    def maxsoillayer(SoilLayers):
        SoilLevels = []
        for SoilLayer in SoilLayers:
            SoilLevels.append(SoilLayer.get('TopLayer'))
        GroundLevel = max(SoilLevels)
        return GroundLevel
    
    def toelevel(Toelevel, GroundLevelFront):
        if ToeLevel == 'N/A':
            ToeLevel = GroundLevelFront - 0.1
        print(ToeLevel)
        return ToeLevel

    def weightwalltotal(Toelevel, zT, wallweight):
        try:
            WeightWallTotal = wallweight * (zT-Toelevel)
        except TypeError:
            WeightWallTotal = 'N/A'
        print(WeightWallTotal)
        return WeightWallTotal

#INPUT PROCESSING
    def get_ground_levels(self, report_dict):
        return (
            self.maxsoillayer(report_dict['SoilLayersBack']),
            self.maxsoillayer(report_dict['SoilLayersFront'])
        )

    def get_toe_and_wall_weight(self, results, ground_front, zT, wall_weight):
        toe = self.toelevel(results.get('ToeLevel'), ground_front)
        weight = self.weightwalltotal(toe, zT, wall_weight)
        return toe, weight

#DATA PREP
    def smooth_moment_curve(levels, moments):
        # Remove duplicate levels for interpolation
        x, y = [], []
        for i in range(len(levels) - 1):
            if levels[i] != levels[i + 1]:
                x.append(levels[i])
                y.append(moments[i])
        x.append(levels[-1])
        y.append(moments[-1])
        return interp1d(np.array(x), np.array(y), kind='quadratic')

    def get_plot_limits(shear, e1, e2, moment, toe, zT):
        maxval = max(max(shear), max(e1), max(e2), max(moment))
        minval = min(min(shear), min(e1), min(e2), min(moment))
        grnextent = max(abs(minval), abs(maxval))
        xmin, xmax = grnextent * -1.05, grnextent * 1.05
        ymin = toe - 0.02 * (zT - toe)
        ymax = zT + 0.1 * (zT - toe)
        return grnextent, xmin, xmax, ymin, ymax

    def compute_aspect_ratio(xmin, xmax, ymin, ymax, width=6.41, height=9.0):
        return ((xmax - xmin) / width) / ((ymax - ymin) / height)

#GEOMETRY
    def get_ground_line(grnextent, ground_level, slope, aspect):
        return (
            [0, grnextent],
            [ground_level, ground_level + grnextent * np.tan(np.radians(slope)) / aspect]
        )

    def get_water_level_line(water_level, ymin, ymax):
        adj = 0.005 * (ymax - ymin)
        return [water_level - adj, water_level - adj]
    
#TEXT AND ANNOTATION
    def format_soil_layer_text(layer, state):
        desc = layer.get('Description')
        if state.lower() == 'drained' or layer.get('KeepDrained') == 'Yes':
            txt = r"$\rm \gamma_d/\gamma_m=%.0f/%.0f$ $\rm kN/m^3$, $\phi_k'=%.0f^\circ$, $c_k'=%.0f$ kPa, $r=%.1f$, $i=%.1f$" % (
                layer['Gamma_d'], layer['Gamma_m'], layer['phi'], layer['c'], layer['r'], layer['i']
            )
        else:
            txt = r"$\rm \gamma_d/\gamma_m=%.0f/%.0f$ $\rm kN/m^3$, $cu_k=%.0f$ kPa, $r=%.1f$, $i=%.1f$" % (
                layer['Gamma_d'], layer['Gamma_m'], layer['cu'], layer['r'], layer['i']
            )
        return '\n'.join((desc, txt))

    def annotate_anchor_force(ax, level, inclination, aspect):
        ax.annotate(
            "", 
            xy=(1.5 * aspect, level), 
            xytext=(0.0, level),
            arrowprops=dict(headwidth=15, headlength=10, width=0.1, color='black')
        )

#SOIL LAYER PLOT
    def plot_soil_layers(ax, layers, grn_extent, toe_level, state, side='back'):
        for i, layer in enumerate(layers):
            top = float(layer['TopLayer'])
            if top <= toe_level:
                continue

            if i > 0:
                strat = [top, top]
                ax.plot(grn_extent, strat, alpha=0.8, color='black', linewidth=1.0)

            text = rfh.format_soil_layer_text(layer, state)
            vert_pos = (
                (top + layers[i+1]['TopLayer']) / 2 if i < len(layers)-1 and layers[i+1]['TopLayer'] > toe_level
                else (top + toe_level) / 2
            )
            xpos = grn_extent[1] if side == 'front' else grn_extent[0]
            ax.text(xpos, vert_pos, text, fontsize=8, va='center', bbox=dict(boxstyle='round', facecolor='grey', alpha=0.0))
