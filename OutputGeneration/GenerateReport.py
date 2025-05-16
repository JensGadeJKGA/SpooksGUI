from SpooksHelperLib.Utils import utils
from SpooksHelperLib.Generators import generators
from SpooksHelperLib.SoilProfiles import soilprofiles
from SpooksHelperLib.SPOOKS import spooksfile

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import os

class generatereport():

    """
    Extracts and organizes necessary data from the VerticalEquilibriumOutput dictionary.
    """
    def extract_data(VerticalEquilibriumOutput, OutputDirList):
        
        GetResultsOutput = VerticalEquilibriumOutput.get('GetResultsOutput', {})
        Analysis = VerticalEquilibriumOutput.get('Analysis', {})
        PlotResults = GetResultsOutput.get('PlotResults', {})
        Results = GetResultsOutput.get('Results', {})

        data = {
            'Project': Analysis.get('Project'),
            'Subject': Analysis.get('Subject'),
            'AnalysisNo': Analysis.get('AnalysisNo'),
            'State': Analysis.get('State'),
            'SoilLayersFront': Analysis.get('SoilLayersFront', []),
            'SoilLayersBack': Analysis.get('SoilLayersBack', []),
            'PlotLevels': PlotResults.get('PlotLevels', []),
            'e1': PlotResults.get('e1', []),
            'e2': PlotResults.get('e2', []),
            'Moment': PlotResults.get('Moment', []),
            'MaxMoment': PlotResults.get('MaxMoment'),
            'ShearForce': PlotResults.get('ShearForce', []),
            'zT': Analysis.get('zT'),
            'SlopeFront': Analysis.get('SlopeFront'),
            'SlopeBack': Analysis.get('SlopeBack'),
            'LoadFront': Analysis.get('LoadFront'),
            'LoadBack': Analysis.get('LoadBack'),
            'LevelLoadBack': Analysis.get('LevelLoadBack'),
            'WaterLevelFront': Analysis.get('WaterLevelFront'),
            'WaterLevelBack': Analysis.get('WaterLevelBack'),
            'AnchorLevel': Analysis.get('AnchorLevel'),
            'AnchorInclination': Analysis.get('AnchorInclination'),
            'AnchorForce': Results.get('AnchorForce'),
            'SumTanForce': VerticalEquilibriumOutput.get('SumTanForce'),
            'WallMass': Analysis.get('WallMass'),
            'DateTime': GetResultsOutput.get('DateTime'),
            'OutputDir': OutputDirList[-1],
            'ToeLevel': Results.get('ToeLevel')
        }

        return data
    
        """
        Calculates additional parameters required for plotting.
        """
    def calculate_additional_parameters(data):
        
        # Calculate Wall Specific Weight
        data['WallSpecificWeight'] = data['WallMass'] * 9.82 / 1000 if data['WallMass'] else 0

        # Determine Ground Levels
        data['GroundLevelBack'] = max([layer.get('TopLayer', 0) for layer in data['SoilLayersBack']], default=0)
        data['GroundLevelFront'] = max([layer.get('TopLayer', 0) for layer in data['SoilLayersFront']], default=0)

        # Determine Toe Level
        if data['ToeLevel'] == 'N/A' or data['ToeLevel'] is None:
            data['ToeLevel'] = data['GroundLevelFront'] - 0.1

        # Calculate Weight Wall Total
        try:
            data['WeightWallTotal'] = data['WallSpecificWeight'] * (data['zT'] - data['ToeLevel'])
        except TypeError:
            data['WeightWallTotal'] = 0

        # Interpolate Moment Curve
        data['m_curve'], data['curve_level'] = utils.interpolate_moment_curve(data['PlotLevels'], data['Moment'])

        return data

        """
        Saves the matplotlib figure to a PDF file in a temporary working directory.
        """
    def save_figure(fig, output_dir):
        
        TemporaryPath = utils.TemporaryWorkingDirectory()
        TempReportFrontPath = os.path.join(TemporaryPath, 'ReportFront.pdf')

        fig.savefig(TempReportFrontPath, dpi='figure', facecolor='w', edgecolor='w',
                    orientation='portrait', format='pdf',
                    transparent=False, bbox_inches=None, pad_inches=0.05, metadata=None)
        plt.close(fig)

        return TempReportFrontPath
    
        """
        Prepares the matplotlib figure with all necessary plot elements.
        """
    def prepare_plot(data):
        
        plt.ioff()
        plt.rcParams.update(plt.rcParamsDefault)
        plt.rcParams['mathtext.fontset'] = 'custom'
        plt.rcParams['mathtext.rm'] = 'Arial'

        fig = plt.figure(figsize=(8.27, 11.69), dpi=80, facecolor='w', edgecolor='k')

        # Plot Earth Pressures
        plt.plot(data['e1'], data['PlotLevels'], color='mediumseagreen', label='$e_{1}$, $e_{2}$ [kPa]', linewidth=1.0)
        plt.plot(data['e2'], data['PlotLevels'], color='mediumseagreen', linewidth=1.0)

        # Plot Moment Curve
        plt.plot(data['m_curve'](data['curve_level']), data['curve_level'], color='red', label='$M_{Ed}$ [kNm/m]', linewidth=1.0)

        # Plot Shear Force
        plt.plot(data['ShearForce'], data['PlotLevels'], color='grey', label='$V_{Ed}$ [kN/m]', linewidth=1.0)

        # Plot Wall
        plt.plot([0, 0], [data['zT'], data['ToeLevel']], color='black', linewidth=1.5)

        # Additional plotting elements like ground levels, water levels, anchors, soil layers, and text boxes
        # would be added here using similar helper functions for clarity and modularity.

        plt.ylabel('Level [m]')
        plt.title(f"{data['Project']}, {data['Subject']}, Calc. no. {data['AnalysisNo']}")
        plt.legend(loc='upper right')

        return fig



        """
        Generates a report front plot based on vertical equilibrium analysis results.
        """
    def ReportFront(self, VerticalEquilibriumOutput, OutputDirList, Version):
        
        print('Generating report front...')

        # Extract necessary data
        data = self.extract_data(VerticalEquilibriumOutput, OutputDirList)

        # Calculate additional parameters
        data = self.calculate_additional_parameters(data)

        # Prepare plot elements
        fig = self.prepare_plot(data)

        # Save the figure
        TempReportFrontPath = self.save_figure(fig, data['OutputDir'])

        return TempReportFrontPath