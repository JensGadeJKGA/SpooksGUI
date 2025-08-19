import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt
import numpy as np
import os

from SpooksHelperLib.GenerateReport.reportFrontHelpers import reportFrontHelpers as rfh
from SpooksHelperLib.Utils import utils

class reportFront:
    def ReportFront(self, VerticalEquilibriumOutput, OutputDirList, Version):
        print("Generating report front...")
        rfhelper = rfh()
        # Generate report dictionary ---
        reportDict = rfh.generateReportDict(VerticalEquilibriumOutput, OutputDirList)

        # Get geometry values ---
        GroundLevelBack, GroundLevelFront = rfhelper.get_ground_levels(reportDict)
        ToeLevel, WeightWallTotal = rfhelper.get_toe_and_wall_weight(
            VerticalEquilibriumOutput['GetResultsOutput']['Results'],
            GroundLevelFront,
            reportDict['zT'],
            reportDict['WallSpecificWeight']
        )

        # Plot limits and aspect ratio ---
        grnextent, xmin, xmax, ymin, ymax = rfh.get_plot_limits(
            reportDict['ShearForce'],
            reportDict['e1'],
            reportDict['e2'],
            reportDict['Moment'],
            ToeLevel,
            reportDict['zT']
        )
        aspect = rfh.compute_aspect_ratio(xmin, xmax, ymin, ymax)

        grnextent_front, grnlevel_front = rfh.get_ground_line(-grnextent, GroundLevelFront, reportDict['SlopeFront'], aspect)
        grnextent_back, grnlevel_back = rfh.get_ground_line(grnextent, GroundLevelBack, reportDict['SlopeBack'], aspect)

        waterlvl_front = rfh.get_water_level_line(reportDict['WaterLevelFront'], ymin, ymax)
        waterlvl_back = rfh.get_water_level_line(reportDict['WaterLevelBack'], ymin, ymax)

        wall_x = [0, 0]
        wall_y = [reportDict['zT'], ToeLevel]

        # Interpolated moment curve ---
        m_curve = rfh.smooth_moment_curve(reportDict['PlotLevels'], reportDict['Moment'])
        curve_level = np.linspace(min(reportDict['PlotLevels']), max(reportDict['PlotLevels']), 100)

        # Plotting setup ---
        plt.ioff()
        plt.rcParams.update(plt.rcParamsDefault)
        plt.rcParams['mathtext.fontset'] = 'custom'
        plt.rcParams['mathtext.rm'] = 'Arial'

        fig, ax = plt.subplots(figsize=(8.27, 11.69))

        # Forces and structure ---
        ax.plot(reportDict['e1'], reportDict['PlotLevels'], color='mediumseagreen', label='$e_{1}$, $e_{2}$ [kPa]', linewidth=1.0)
        ax.plot(reportDict['e2'], reportDict['PlotLevels'], color='mediumseagreen', linewidth=1.0)
        ax.plot(m_curve(curve_level), curve_level, color='red', label='$M_{Ed}$ [kNm/m]', linewidth=1.0)
        ax.plot(reportDict['ShearForce'], reportDict['PlotLevels'], color='grey', label='$V_{Ed}$ [kN/m]', linewidth=1.0)
        ax.plot(wall_x, wall_y, color='black', linewidth=1.5)
        ax.plot(grnextent_back, grnlevel_back, color='black', linewidth=1.5)
        ax.plot(grnextent_front, grnlevel_front, color='black', linewidth=1.5)
        ax.plot(grnextent_back, waterlvl_back, color='dodgerblue', linewidth=1.2, linestyle='dashed')
        ax.plot(grnextent_front, waterlvl_front, color='dodgerblue', linewidth=1.2, linestyle='dashed')

        if reportDict['AnchorLevel'] is not None:
            rfh.annotate_anchor_force(ax, reportDict['AnchorLevel'], reportDict['AnchorInclination'], aspect)

        # Plugin info text ---
        ax.text(
            xmin, ymin + (ymax - ymin) * 0.02,
            f"COWI WinSpooks Plug-in {Version}, {reportDict['DateTime']}\nSaved to: {reportDict['OutputDir']}",
            fontsize=5.0, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.0)
        )

        # Titles and axis ---
        ax.set_ylabel('Level [m]')
        ax.set_title(f"{reportDict['Project']}, {reportDict['Subject']}, Calc. no. {reportDict['AnalysisNo']}")
        ax.set_ylim(ymin, ymax)
        ax.set_xlim(xmin, xmax)
        ax.legend(loc='upper right')

        # Plot soil layers front and back ---
        rfhelper.plot_soil_layers(ax, reportDict['SoilLayersBack'], grnextent_back, ToeLevel, reportDict['State'], side='back')
        rfhelper.plot_soil_layers(ax, reportDict['SoilLayersFront'], grnextent_front, ToeLevel, reportDict['State'], side='front')

        # Loads ---
        ax.text(
            sum(grnextent_front) / 2, grnlevel_front[0],
            rf"$\rm q_{{fk}}={reportDict['LoadFront']:.0f}$ $\rm kPa$", fontsize=8, va='bottom'
        )
        ax.text(
            sum(grnextent_back) / 2, grnlevel_back[0],
            rf"$\rm q_{{bk}}={reportDict['LoadBack']:.0f}$ $\rm kPa$", fontsize=8, va='bottom'
        )

        # Results box ---
        if reportDict['AnchorLevel'] is not None:
            AnchorAxial = reportDict['AnchorForce'] / np.cos(np.radians(reportDict['AnchorInclination']))
            net_force = reportDict['SumTanForce'] - WeightWallTotal - AnchorAxial * np.sin(np.radians(reportDict['AnchorInclination']))
            result_text = (
                rf"$\rm |M_{{Ed,max}}|={abs(reportDict['MaxMoment']):.0f}$ kNm/m\n"
                rf"$\rm Toe_{{level}}={ToeLevel:.1f}$ m\n"
                rf"$\rm A_d={reportDict['AnchorForce']:.0f}$ kN/m\n"
                rf"$\rm \Sigma F↑={net_force:.0f}$ kN/m"
            )
        else:
            net_force = reportDict['SumTanForce'] - WeightWallTotal
            result_text = (
                rf"$\rm |M_{{Ed,max}}|={abs(reportDict['MaxMoment']):.0f}$ kNm/m\n"
                rf"$\rm Toe_{{level}}={ToeLevel:.1f}$ m\n"
                rf"$\rm \Sigma F↑={net_force:.0f}$ kN/m"
            )

        ax.text(
            xmin, ymax - 0.017 * (ymax - ymin),
            result_text, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='grey', alpha=0.1)
        )

        # Logo ---
        ax.text(xmax, ymin, 'COWI', fontsize=20, fontname='Century Schoolbook', color='orangered', ha='right', va='bottom')

        # Save figure ---
        temp_path = os.path.join(utils.TemporaryWorkingDirectory(), 'ReportFront.pdf')
        plt.savefig(temp_path, dpi='figure', facecolor='w', edgecolor='w',
                    orientation='portrait', format='pdf', transparent=False,
                    bbox_inches=None, pad_inches=0.05)
        plt.close()

        return temp_path
