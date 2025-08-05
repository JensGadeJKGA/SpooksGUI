import numpy as np
from Steel_Sheet_Pile_Wall import steel_sheet_pile_implementer

class exportHelper:
    def __init__(self):
        pass

    def get_sheet_pile_addon_results(result):
        try:
            return steel_sheet_pile_implementer(result)
        except Exception as e:
            print(f"Error processing sheet pile results: {e}")
            return {
                'SheetPileProfile': 'N/A',
                'RUR': 'N/A',
                'RURLevel': 'N/A',
                'RURLevel_max': 'N/A',
                'RotCap': 'N/A'
            }

    def get_toe_level(result):
        toe = result['Results'].get('ToeLevel')
        if toe != "N/A":
            return toe
        soil_layers = result['Analysis'].get('SoilLayersFront', [])
        levels = [layer.get('TopLayer', 0) for layer in soil_layers]
        ground_level = max(levels) if levels else 0
        return ground_level - 0.1

    def get_anchor_data(result):
        try:
            level = result['Analysis'].get('AnchorLevel')
            incl = float(result['Analysis'].get('AnchorInclination', 0))
            force = result['Results'].get('AnchorForce')
            axial = force / np.cos(np.radians(incl)) if force is not None else 'N/A'
            moment = result['Results'].get('MomentAtAnchor')
            return level, incl, force, axial, moment
        except:
            return 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
    
    def compute_wall_weight(result, toe_level):
        zT = result['Analysis'].get('zT', 0)
        wall_mass = result['Analysis'].get('WallMass', 0)
        specific_weight = wall_mass * 9.82 / 1000
        return specific_weight * (zT - toe_level)

    def compute_sum_vertical_forces(anchor_axial, anchor_incl, weight_wall, axial_load, tan_force, anchor_level):
        if anchor_level != 'N/A':
            return tan_force - anchor_axial * np.sin(np.radians(anchor_incl)) - weight_wall - axial_load
        else:
            return tan_force - weight_wall - axial_load
