import numpy as np
import os

from SpooksHelperLib.Export.exportHelper import exportHelper as eh
from SpooksHelperLib.Steel_Sheet_Pile_Wall import steel_sheet_pile_implementer
from SpooksHelperLib.Vequilibrium import verticalEquilibrium

class export:
    def __init__(self):
        pass

    def ExportResultsAsTxt(feeder_output, output_dir_list):
        print("Exporting as TxT")
        use_addon = feeder_output[0].get('GetResultsOutput', {}).get('Analysis', {}).get('SheetPileAddOnInput', {}).get('UseAddOn') == "Yes"
        base_headers = ['Analysis No.', 'Subject', 'Soil Profile', 'State', 'Load Combination', 'AnchorLevel',
                        'AnchorForce', 'Moment at Anchor Level', 'Level of Max. Moment', 'Max. Moment',
                        'Encastre Level', 'Encastre Moment', 'Yield Level', 'Yield Moment',
                        'Max. Shear Force', 'Toe Level', 'Sum of vertical forces']
        addon_headers = ['Profile', 'Max utilization', 'Lvl of Max utilization'] if use_addon else []

        printlist = [base_headers + addon_headers]

        for analysis in feeder_output:
            result = analysis.get('GetResultsOutput', {})

            addon_used = result.get('Analysis', {}).get('SheetPileAddOnInput', {}).get('UseAddOn') == 'Yes'
            addon_results = eh.get_sheet_pile_addon_results(result) if addon_used else {
                'SheetPileProfile': 'N/A',
                'RUR': 'N/A',
                'RURLevel': 'N/A',
                'RURLevel_max': 'N/A',
                'RotCap': 'N/A'
            }
            ve = verticalEquilibrium()
            vertical_eq = ve.VerticalEquilibrium(result)
            sum_tan_force = vertical_eq.get('SumTanForce', 0)

            analysis_no = result['Analysis'].get('AnalysisNo', 'N/A')
            subject = result['Analysis'].get('Subject', 'N/A')
            profile = result['Analysis'].get('SoilProfile', 'N/A')
            state = result['Analysis'].get('State', 'N/A')
            combination = result['Analysis'].get('LoadCombination', 'N/A')
            axial_load = result['Analysis'].get('AxialWallLoad', 0)

            anchor_level, anchor_incl, anchor_force, anchor_axial, moment_anchor = eh.get_anchor_data(result)

            level_max_moment = result['PlotResults'].get('LevelMaxMoment', 'N/A')
            max_moment = result['PlotResults'].get('MaxMoment', 'N/A')
            encastre_lvl = result['Results'].get('EncastreLevel', 'N/A')
            encastre_moment = result['Results'].get('EncastreMoment', 'N/A')
            yield_lvl = result['Results'].get('YieldHingeLevel', 'N/A')
            yield_moment = result['Results'].get('YieldHingeMoment', 'N/A')
            max_shear = result['PlotResults'].get('MaxShearForce', 'N/A')

            toe_level = eh.get_toe_level(result)
            wall_weight = eh.compute_wall_weight(result, toe_level)

            sum_vert_forces = eh.compute_sum_vertical_forces(anchor_axial, anchor_incl, wall_weight, axial_load, sum_tan_force, anchor_level)

            row = [
                analysis_no, subject, profile, state, combination,
                anchor_level, anchor_force, moment_anchor,
                level_max_moment, max_moment, encastre_lvl, encastre_moment,
                yield_lvl, yield_moment, max_shear, toe_level, sum_vert_forces
            ]

            if addon_used:
                row += [
                    addon_results.get('SheetPileProfile', 'N/A'),
                    addon_results.get('RUR', 'N/A'),
                    addon_results.get('RURLevel_max', 'N/A')
                ]

            printlist.append(row)

        results_path = os.path.join(output_dir_list[-1], 'Results.txt')
        np.savetxt(results_path, printlist, delimiter=';', fmt='%s')
        


    def ExportEarthPressureResultsAsTxt(FeederOutput, OutputDirList):
        print("Exporting Earth pressure as TXT")
        
        ## Temporary file dir
        #TemporaryFile = TemporaryWorkingDirectory()
        ## Initial empty array
        EarthPressureResults = np.empty((0,8), int) # Empty array
        
        for Analysis in FeederOutput:

            #GetResultsOutput = Analysis.get('GetResultsOutput')
            
            EarthPressureResultsOutput = Analysis.get('GetResultsOutput').get('EarthPressureResults')
            
            try:
                AnalysisNo = 'Analysis no. '+ Analysis.get('AnalysisNo')
            except:
                AnalysisNo = 'N/A'
            AnalysisNoArray = np.empty((0,8), int) ## empty array
            np.append(AnalysisNoArray, ['AnalysisNo', AnalysisNo,'','','','','',''])
            
        
            EarthPressureResults = np.concatenate((EarthPressureResults, AnalysisNoArray, EarthPressureResultsOutput), axis=0)
            
        
        
        # Exporting earth pressure results as text file
        results_path = OutputDirList[-1] ## results path
        EP_results = os.path.join(results_path, r'EarthPressureResults.txt')
        np.savetxt(EP_results, EarthPressureResults, delimiter='\t', fmt='%s')
        
        
        return EarthPressureResults