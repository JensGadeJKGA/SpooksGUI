########################################################################################################################
########################################################################################################################
#
#     SSS  TTTTTT EEEE EEEE L         SSS  H  H EEEE EEEE TTTTTT     PPPP  III L    EEEE     W     W  AA  L    L
#    S       TT   E    E    L        S     H  H E    E      TT       P   P  I  L    E        W     W A  A L    L
#     SSS    TT   EEE  EEE  L         SSS  HHHH EEE  EEE    TT       PPPP   I  L    EEE      W  W  W AAAA L    L
#        S   TT   E    E    L            S H  H E    E      TT       P      I  L    E         W W W  A  A L    L
#    SSSS    TT   EEEE EEEE LLLL     SSSS  H  H EEEE EEEE   TT       P     III LLLL EEEE       W W   A  A LLLL LLLL
#
########################################################################################################################
########################################################################################################################
#
#    Calculations in accordance with DS/EN 1993-5 and DK NA.                                  CCC  OOO  W     W III
#    This calculation verifies the cross-sectional and member load carrying capacity         C    O   O W     W  I
#    of steel sheet pile walls respecting plastic rotations, diff. water and                 C    O   O W  W  W  I
#    occurrence of corrosion.                                                                C    O   O  W W W   I
#                                                                                             CCC  OOO    W W   III
#
########################################################################################################################
########################################################################################################################
#
#   Rev:        Date:               Inits:              Comment:
#   0.1         25.07.2022          CHHJ                First version
#
########################################################################################################################
########################################################################################################################


# KAGB: Jeg vil anbefale at tilføje scriptet til et virtuelt miljø og lave en requirements fil. Umiddelbart kræves kun pandas og numpy som main deps

#   IMPORT PACKAGES 
import numpy as np
import pandas as pd


#   Sheet pile data from Database
sheet_db_filename = r'O:\Organisation\DK_1551\Konstruktioner\INIT\CHHJ\Geotekniske beregningsdokumenter\3. Under udvikling\Database_Spunsvægge.xlsx'
sheet_db = pd.read_excel(sheet_db_filename, sheet_name=0, skiprows=[1, 2], index_col=0)
sheetpile = sheet_db.index  # section names

########################################################################################################################
#   INPUT VARIABLES
########################################################################################################################



# w_dif = 0.5  # Diff. water pressure [m]
# L = 18  # Length, anchor level - pile tip level [m]

# # Rotational Capacity
# failure_mode = '1FC'  # Failure mode: 0FC, 1FC, 2FC
# soil_comp = 'Dense'  # Deposition of soil: Dense, Loose
# anchor_level = -1.0  # Anchor level [level - m]
# maxm_level = -10.5  # Level of max moment [level - m]
# pl_level = -18  # Level of pile tip for 1FC. Equal to 2nd max moment for 2FC
# m_ind_level = 0  # Level of 2nd max moment for 2FC. Variable can be set to anything for 1FC.
# exca_level = -14.5  # Excavation level [level - m]
# mob_vp = 'Yes'  # Mobilization of passive earth pressure below water table: Yes(if terrain in front is below water), No
# w_1clc = None  # Calculated displacement, if None not used.
# w_2clc = None  # Calculated displacement, if None not used.
# w_3clc = None  # Calculated displacement, if None not used.

########################################################################################################################
#   CALCULATION
########################################################################################################################

def sheet_pile_add_on(profile, max_util, LS_calc, Ctl_cl, K_FI_cl, fyk, e_modul, 
                      beta_B, beta_D, t_cor_input_list, t_cor_lvl_input_list, MEd_list, VEd_list, NEd_list,
                      lvl_list, w_dif, L, failure_mode, soil_comp, pl_level, maxm_level, anchor_level,
                      m_ind_level, exca_level, mob_vp, w_1clc, w_2clc, w_3clc, sheet_db, sheetpile):
    
    
    
    
    
    #### Added by EMBT 17.10.2023 (forces are converted to absolute values)
    # M_Ed_MaxM = abs(M_Ed_MaxM)
    # V_Ed_MaxM = abs(V_Ed_MaxM)
    # N_Ed_MaxM = abs(N_Ed_MaxM)
    # for item in [M_Ed_anchor, V_Ed_anchor, N_Ed_anchor]:
        
    #     try:
    #         item = abs(item)
            
    #     except:
            
    #         pass
        
    M_list = [abs(ele) for ele in MEd_list]
    V_list = [abs(ele) for ele in VEd_list]
    N_list = [abs(ele) for ele in NEd_list]
    ###############################################################
    
    #NEW!!!!!!!!!!!!!!!!!!!
    # t_cor_input_list = [3.75, 0, 1.2]
    # t_cor_lvl_input_list = [2, -1, -4]
    t_cor = [t_cor_lvl_input_list, t_cor_input_list]


    # #NEW!!!!!!!!!!!!!!!!!!!
    # M_list = [1000, 900, 800, 700, 600, 500]
    # V_list = [50, 200, 400, 50, 50, 50]
    # N_list = [10, 0, 100, 1, 1, 1]
    # lvl_list = [2, 1, 0, -3, -4, -6]
    t_cor_list = [0] * len(lvl_list)
    for i in range(len(lvl_list)):
        j=0
        if lvl_list[i] == t_cor_lvl_input_list[0]:
            t_cor_list[i] = t_cor_input_list[0]
        elif lvl_list[i] in t_cor_lvl_input_list:
            value_index = t_cor_lvl_input_list.index(lvl_list[i])
            t_cor_list[i] = max(t_cor_input_list[value_index], t_cor_input_list[value_index-1])
        elif lvl_list[i] < t_cor_lvl_input_list[j]:
            while lvl_list[i] < t_cor_lvl_input_list[j]:
                if j == len(t_cor_lvl_input_list)-1:
                    break
                else:
                    j=j+1
            if j == len(t_cor_lvl_input_list) - 1:
                t_cor_list[i] = t_cor_input_list[j]
            else:
                t_cor_list[i] = t_cor_input_list[j - 1]
        elif lvl_list[i] > t_cor_lvl_input_list[j]:
            t_cor_list[i] = t_cor_input_list[j-1]


    loads_df = pd.DataFrame({
        "Level": lvl_list,
        "Moment": M_list,
        "Shear": V_list,
        "Axial_force": N_list,
        "Corrosion":    t_cor_list
    })
    
    
    
    if 'Optimize' not in profile:
        drop_list = sheetpile.drop(profile)
        sheet_db = sheet_db.drop(index=drop_list)
        sheetpile = profile
        
    d_w = sheet_db['b']  # Distance between locks [mm]
    h = sheet_db['h']  # Height of flange [mm]
    t_f_init = sheet_db['t']  # Thickness of flange [mm]
    t_w_init = sheet_db['s']  # Thickness of web [mm]
    a_init = sheet_db['A']  # Cross-section area [cm2/m]
    i_y_init = sheet_db['Iy']  # Moment of inertia [cm4/m]
    w_ely_init = sheet_db['Wel,y']  # Elastic sectional modulus [cm3/m]
    w_ply_init = sheet_db['Wpl,y']  # Plastic sectional modulus [cm3/m]
    angle_init = sheet_db['angle']  # Angle between web and CL [deg]
    b = sheet_db['breddeflange']  # Width of flange [mm]
    type_profile = sheet_db['profiltype']  # Profile type [-]
    type_profile_2 = sheet_db["profiltype_2"]  # Profile type 2 [-]
    
    num_sheetpiles = len(sheet_db)
    
    
    def main(t_c_tot, v_ed, n_ed, m_ed):
        #   PARTIAL SAFETY FACTORS - DS/EN 1993-5 DK NA 5.1.1 (4)
        ls, calc_type = LS_calc.split("-", 1)  # Limit State-Calculation Type
        k_fi = {'CC3': 1.1, 'Disable': 1.0}
        gamma_3 = {'Normal': 1.0, 'Strict': 0.95}
        gamma_m0 = {'ULS': 1.1 * gamma_3[Ctl_cl] * k_fi[K_FI_cl], 'SLS': gamma_3[Ctl_cl], 'ALS': 1.0}
        gamma_m1 = {'ULS': 1.2 * gamma_3[Ctl_cl] * k_fi[K_FI_cl], 'SLS': gamma_3[Ctl_cl], 'ALS': 1.0}
    
        #   GEOMETRICAL PROPERTIES
        #   Apply Corrosion
        t_f = t_f_init - t_c_tot  # Thickness of flange incl. corrosion [mm]
        t_w = t_w_init - t_c_tot  # Thickness of web incl. corrosion [mm]
        w_el = w_ely_init * ((t_f_init - t_c_tot) / t_f_init)  # Elastic section modulus incl. corrosion [cm3/m]
        w_pl = w_ply_init * ((t_f_init - t_c_tot) / t_f_init)  # Elastic section modulus incl. corrosion [cm3/m]
        i_y = i_y_init * ((t_f_init - t_c_tot) / t_f_init)  # Moment of inertia incl. corrosion [cm4/m]
        a_v = (t_w * (h - t_f)) / d_w * 10  # Web area incl. corrosion [cm2/m]
        a = a_init * ((t_f_init - t_c_tot) / t_f_init)  # Cross-sectional area [cm2/m]
        w_y = w_pl if calc_type == 'Plastic' else w_el
    
        # Non-dim. slenderness [-]
        c = (h - t_f) / np.sin(np.radians(angle_init))
        c[type_profile == "U"] /= 2
    
        #   MATERIAL PROPERTIES
        f_yk = np.full(num_sheetpiles, float(fyk))
    
        def eps_func(f_yk_func):  # DS/EN 1993-5 Table 5.1
            return np.sqrt(235 / f_yk_func)
    
        epsilon = eps_func(f_yk)
        l_a = (b / t_f) / epsilon
    
        #   Cross-Section Class
        def csc_func(la, piletype):  # DS/EN 1993-5 Table 5.1
            if (la <= 45 and piletype == 'Z') or (la <= 37 and piletype == 'U'):
                return 1
            elif ((45 < la <= 66) and piletype == 'Z') or ((37 < la <= 49) and piletype == 'U'):
                return 3
            elif (la > 66 and piletype == 'Z') or (la > 49 and piletype == 'U'):
                return 4
            else:
                float("nan")
    
        csc = [csc_func(l_a[i], type_profile[i]) for i in range(num_sheetpiles)]
        csc = np.array(csc)
    
        for i in range(num_sheetpiles):
            if csc[i] == 4:  # Yield strength reduced because of Cross-Section Class 4. Recalc of eps and lambda
                if type_profile[i] == 'Z':
                    f_yk[i] = 235 / ((b[i] / t_f[i]) / 66) ** 2
                elif type_profile[i] == 'U':
                    f_yk[i] = 235 / ((b[i] / t_f[i]) / 49) ** 2
                epsilon[i] = eps_func(f_yk[i])
    
                if (l_a[i] <= 45 and type_profile[i] == 'Z') or (l_a[i] <= 37 and type_profile[i] == 'U'):
                    pass
                elif ((45 < l_a[i] <= 66) and type_profile[i] == 'Z') or ((37 < l_a[i] <= 49) and type_profile[i] == 'U'):
                    pass
                elif (l_a[i] > 66 and type_profile[i] == 'Z') or (l_a[i] > 49 and type_profile[i] == 'U'):
                    l_a[i] = (b[i] / t_f[i]) / epsilon[i]
                else:
                    # KAGB: Jeg er usikker på om den ønskede adfærd er at bryde sammen eller om fejlen skal gemmes til senere. Hvis der indsættes tekst i listen, så bryder koden sammen senere.
                    raise Exception("ERROR in csc cl. 4")
    
        ################################################################################################################
        #   STATIC CALCULATIONS
        ################################################################################################################
        # YIELD STRENGTH REDUCTION FACTORS
        # Reduction due to Non-dimensional Slenderness (DS/EN 1993-5 Table C-1)
        def p_c_func(la, pile_type):  # Reduction factor due to non-dimensional slenderness (DS/EN 1993-5 Table C-1)
            la = np.round(la, 2)
            if (np.round(la,2) <= 45 and pile_type == 'Z') or (la <= 37 and pile_type == 'U'):
                return 1.0
            elif (45 < la <= 50) and pile_type == 'Z':
                return ((0.95 - 1.00) / (50 - 45)) * la + (1.00 - ((0.95 - 1.00) / (50 - 45)) * 45)
            elif (50 < la <= 60) and pile_type == 'Z':
                return ((0.90 - 0.95) / (60 - 50)) * la + (0.95 - ((0.90 - 0.95) / (60 - 50)) * 50)
            elif (60 < la <= 66) and pile_type == 'Z':
                return ((0.85 - 0.90) / (66 - 60)) * la + (0.90 - ((0.85 - 0.90) / (66 - 60)) * 60)
            elif (37 < la <= 40) and pile_type == 'U':
                return ((0.95 - 1.00) / (40 - 37)) * la + (1.00 - ((0.95 - 1.00) / (40 - 37)) * 37)
            elif (40 < la <= 46) and pile_type == 'U':
                return ((0.90 - 0.95) / (46 - 40)) * la + (0.95 - ((0.90 - 0.95) / (46 - 40)) * 40)
            elif (46 < la <= 49) and pile_type == 'U':
                return ((0.85 - 0.90) / (49 - 46)) * la + (0.90 - ((0.85 - 0.90) / (49 - 46)) * 46)
            else:
                raise Exception('ERROR in p_C_func!')
    
        p_c = [p_c_func(l_a[i], type_profile[i]) for i in range(num_sheetpiles)]
        p_c = np.array(p_c)
    
        # Reduction due to Differential Water Pressure (DS/EN 1993-5 Table 5.2)
        b_water = [c[i] / np.sqrt(2) if b[i] <= c[i] / np.sqrt(2) else b[i] for i in range(num_sheetpiles)]
        b_water = np.array(b_water)
    
        l_a_water = (b_water / np.minimum(t_f, t_w)) * epsilon
    
        def p_p_func(z, l_a_w, piletype):
            # KAGB: Måske det her kan faktoriseres på en eller anden måde, men lad os se på det sammen.
            def g20_func(x_func):
                if x_func < 5:
                    return 1.0
                elif 5 <= x_func < 10:
                    return ((0.99 - 1.00) / (10 - 5)) * x_func + (1.00 - ((0.99 - 1.00) / (10 - 5)) * 5)
                elif 10 <= x_func < 15:
                    return ((0.98 - 0.99) / (15 - 10)) * x_func + (0.99 - ((0.99 - 0.98) / (15 - 10)) * 10)
                elif 15 <= x_func <= 20:
                    return 0.98
                else:
                    raise Exception('ERROR in g20_func!')
    
            def g30_func(x_func):
                if x_func < 5:
                    return 1.0
                elif 5 <= x_func < 10:
                    return ((0.97 - 1.00) / (10 - 5)) * x_func + (1.00 - ((0.97 - 1.00) / (10 - 5)) * 5)
                elif 10 <= x_func < 15:
                    return ((0.96 - 0.97) / (15 - 10)) * x_func + (0.97 - ((0.96 - 0.97) / (15 - 10)) * 10)
                elif 15 <= x_func <= 20:
                    return ((0.94 - 0.96) / (20 - 15)) * x_func + (0.96 - ((0.94 - 0.96) / (20 - 15)) * 15)
                else:
                    raise Exception('ERROR in g30_func!')
    
            def g40_func(x_func):
                if x_func < 5:
                    return 1.0
                elif 5 <= x_func < 10:
                    return ((0.95 - 1.00) / (10 - 5)) * x_func + (1.00 - ((0.95 - 1.00) / (10 - 5)) * 5)
                elif 10 <= x_func < 15:
                    return ((0.92 - 0.95) / (15 - 10)) * x_func + (0.95 - ((0.92 - 0.95) / (15 - 10)) * 10)
                elif 15 <= x_func <= 20:
                    return ((0.88 - 0.92) / (20 - 15)) * x_func + (0.92 - ((0.88 - 0.92) / (20 - 15)) * 15)
                else:
                    raise Exception('ERROR in g40_func!')
    
            def g50_func(x_func):
                if x_func < 5:
                    return 1.0
                elif 5 <= x_func < 10:
                    return ((0.87 - 1.00) / (10 - 5)) * x_func + (1.00 - ((0.87 - 1.00) / (10 - 5)) * 5)
                elif 10 <= x_func < 15:
                    return ((0.76 - 0.87) / (15 - 10)) * x_func + (0.87 - ((0.76 - 0.87) / (15 - 10)) * 10)
                elif 15 <= x_func <= 20:
                    return ((0.60 - 0.76) / (20 - 15)) * x_func + (0.76 - ((0.60 - 0.76) / (20 - 15)) * 15)
                else:
                    raise Exception('ERROR in g50_func!')
    
            if piletype == 'Z':
                if l_a_w < 20:
                    return 1.0
                elif 20 <= l_a_w < 30:
                    return g20_func(z) * ((30 - l_a_w) / (30 - 20)) + g30_func(z) * ((l_a_w - 20) / (30 - 20))
                elif 30 <= l_a_w < 40:
                    return g30_func(z) * ((40 - l_a_w) / (40 - 30)) + g40_func(z) * ((l_a_w - 30) / (40 - 30))
                elif 40 <= l_a_w < 50:
                    return g40_func(z) * ((50 - l_a_w) / (50 - 40)) + g50_func(z) * ((l_a_w - 40) / (50 - 40))
                elif 50 <= l_a_w:
                    return g50_func(z)
            elif piletype == 'U':
                return 1.0
            else:
                raise Exception('ERROR in p_p_func!')
    
        p_p = [p_p_func(w_dif, l_a_water[i], type_profile[i]) for i in range(num_sheetpiles)]
        p_p = np.array(p_p)
    
        # Reduction of Yield Strength (DS/EN 1993-5 Section 5.2.4)
        f_yk_red = f_yk * p_c * p_p  # Reduced char. yield strength [MPa]
    
        # CROSS-SECTION ANALYSIS
        # Bending Moment (DS/EN 1993-5 Section 5.2.2)
        m_crd = beta_B * w_y * (f_yk_red / gamma_m0[ls]) / 1000  # Design moment resistance [kN*m/m]
        u_relm = m_ed / m_crd  # Relative utilization ratio [-]
    
        # Shear Force (DS/EN 1993-5 Section 5.2.2)
        v_plrd = a_v * f_yk_red / (np.sqrt(3) * gamma_m0[ls]) / 10  # Design plastic shear resistance [kN/m]
        u_relv = v_ed / v_plrd  # Relative utilization ratio [-]
    
        p_v = ((2 * v_ed) / v_plrd - 1) ** 2
        f_yk_redn = (1 - p_v) * f_yk_red
    
        p_v[u_relv <= 0.5] = 0.0
        f_yk_redn[u_relv <= 0.5] = f_yk_red[u_relv <= 0.5]
    
        # Shear Buckling (DS/EN 1993-5 Section 5.2.2)
        l_w = 0.346 * (c / t_w) * np.sqrt(f_yk_red / e_modul * 10 ** -3)  # Relative web slenderness [-]
    
        def f_bv_func(l_w_func, f_ykred):
            if l_w_func <= 0.83:
                return 0.58 * f_ykred
            elif 0.83 < l_w_func < 1.40:
                return (0.48 * f_ykred) / l_w_func
            elif 1.40 <= l_w_func:
                return (0.67 * f_ykred) / l_w_func ** 2
            else:
                raise Exception('ERROR in f_bv_func!')
    
        f_bv = [f_bv_func(l_w[i], f_yk_red[i]) for i in range(num_sheetpiles)]
        f_bv = np.array(f_bv)
    
        v_brd = ((h - t_f) * t_w * f_bv) / (gamma_m0[ls] * d_w)  # Shear buckling resistance [kN/m]
        u_relvbuck = v_ed / v_brd  # Relative utilization ratio [-]
        u_relvbuck[(c / t_w) / epsilon <= 72] = 0
    
        # Axial Force (DS/EN 1993-5 Section 5.2.3)
        n_plrd = (a * f_yk_red) / gamma_m0[ls] / 10  # Design plastic resistance [kN/m]
        u_reln = n_ed / n_plrd  # Relative utilization ratio [-]
    
        cond_a = (u_reln <= 0.10) & (csc != 3) & (type_profile == 'Z')
        cond_b = (u_reln <= 0.25) & (csc != 3) & (type_profile == 'U')
        cond_c = (u_reln <= 0.10) & (csc == 3)
        axialreduc = np.ones(num_sheetpiles)
        axialreduc[cond_a | cond_b | cond_c] = 0.0
    
        # Member buckling (DS/EN 1993-5 Section 5.2.3)
        l_buck = L  # Buckling length [m]
        n_cr = (e_modul * i_y * beta_D * np.pi ** 2) / l_buck ** 2 / 100  # Elastic critical load [kN/m]
        u_relncr = n_ed / n_cr  # Relative utilization ratio [-]
    
        l_rel_cr = np.sqrt((a * 10 ** (-4) * f_yk_red * 10 ** 3) / n_cr)  # Relative non dimensionsal slenderness [-]
        a_imp = 0.76  # Imperfection factor [-]
        phi = 0.5 * (1.0 + a_imp * (l_rel_cr - 0.2) + l_rel_cr ** 2)
        chi = np.minimum(1.0, 1 / (phi + np.sqrt(phi ** 2 - l_rel_cr ** 2)))
        u_relbuck = n_ed/(chi*n_plrd*(gamma_m0[ls]/gamma_m1[ls]))+1.15*m_ed/(m_crd*(gamma_m0[ls]/gamma_m1[ls]))
        u_relbuck = np.array(u_relbuck)
        u_relbuck[u_relncr < 0.04] = 0
    
        # Combined Bending, Shear and Axial Force (DS/EN 1993-5 Section 5.2.3)
        # Bending moment reduced due to shear force [kN*m/m]
        m_vrd = (beta_B*w_y-(p_v*a_v**2)/(4*t_w*np.sin(np.radians(angle_init)))*10)*(f_yk_red/gamma_m0[ls])/1000
    
        def m_nrd_func(i):
            if csc[i] == 1 or csc[i] == 4:
                if type_profile[i] == 'Z':
                    return 1.11 * beta_B * w_y[i] * f_yk_redn[i] / gamma_m0[ls] * (1 - u_reln[i]) / 1000
                else:
                    return 1.33 * beta_B * w_y[i] * f_yk_redn[i] / gamma_m0[ls] * (1 - u_reln[i]) / 1000
            else:
                return beta_B * w_y[i] * f_yk_redn[i] / gamma_m0[ls] * (1 - u_reln[i]) / 1000
    
        m_nrd = [m_nrd_func(i) for i in range(num_sheetpiles)]
        m_nrd = np.array(m_nrd)
    
        m_cvrd = np.minimum(m_crd, m_vrd)
        m_cnrd = np.minimum(m_crd, m_nrd)
        m_cvnrd = np.minimum(m_cvrd, m_cnrd)
    
        cond_1 = u_relv <= 0.5
        cond_2 = axialreduc == 0
        cond_v = ~cond_1 & cond_2
        cond_n = cond_1 & ~cond_2
        cond_vn = ~cond_1 & ~cond_2
        
        m_rd = np.copy(m_crd)
        m_rd[cond_v] = m_cvrd[cond_v]
        m_rd[cond_n] = m_cnrd[cond_n]
        m_rd[cond_vn] = m_cvnrd[cond_vn]
    
        u_relcomb = m_ed / m_rd  # Relative utilization ratio [-]
    
        # ROTATIONAL CAPACITY (DS/EN 1993-5 Annex C and DS/EN 1997-1/AC:2010 Annex C.3)
        if not (failure_mode == '1FC' or failure_mode == '2FC'):
            control_rot = ['Rot. Cap. not checked. Not 1FC or 2FC.'] * len(sheetpile)
        else:
    
            l_1 = anchor_level - maxm_level
            if failure_mode == '1FC':
                l_2 = maxm_level - pl_level
            else:
                l_2 = maxm_level - m_ind_level
            l_tot = l_1 + l_2
    
            # Active Earth Pressure
            if failure_mode == '1FC' and soil_comp == 'Loose':
                v_a_min = 0.01
            elif failure_mode == '1FC' and soil_comp == 'Dense':
                v_a_min = 0.005
            elif failure_mode == '2FC' and soil_comp == 'Loose' and 0.01 * l_1 > 0.005 * l_2:
                v_a_min = 0.01
            elif failure_mode == '2FC' and soil_comp == 'Loose' and 0.01 * l_1 <= 0.005 * l_2:
                v_a_min = 0.005
            elif failure_mode == '2FC' and soil_comp == 'Dense' and 0.005 * l_1 > 0.002 * l_2:
                v_a_min = 0.005
            else:
                v_a_min = 0.002
    
            if failure_mode == '1FC' and soil_comp == 'Loose':
                ha = l_1
            elif (failure_mode == '2FC' and v_a_min == 0.002) or (
                    failure_mode == '2FC' and v_a_min == 0.005 and soil_comp == 'Loose'):
                ha = l_2
            else:
                ha = l_1
            v_a = v_a_min * ha  # Active deformation requirements [mm]
    
            # Passive Earth Pressure
            if failure_mode == '1FC' and soil_comp == 'Loose':
                x = 0.015
            elif failure_mode == '1FC' and soil_comp == 'Dense':
                x = 0.01
            elif failure_mode == '2FC' and soil_comp == 'Loose':
                x = 0.04
            elif failure_mode == '2FC' and soil_comp == 'Dense':
                x = 0.02
            else:
                x = 9999
    
            v_p = x * (exca_level - pl_level)
            if mob_vp == 'Yes':
                v_p *= 2
    
            # Determination of Rotational Capacity
    
            w_1 = w_1clc*10**-3 if w_1clc is not None else 0.0
            w_2 = w_2clc*10**-3 if w_2clc is not None else max(v_a, v_p) if failure_mode == "1FC" or failure_mode == "2FC" else 0.0
            w_3 = w_3clc*10**-3 if w_3clc is not None else max(v_a, v_p) if failure_mode == "1FC" else 0.0
            # KAGB: Hvis w_3clc er udefineret og fm ikke er 1FC eller 2FC, så kommer der None ud, er det meningen? Er det muligt?
    
            phi_roted = (w_2 - w_1) / l_1 + (w_2 - w_3) / l_2  # Design rotation angle
            phi_pled = 5 / 12 * (m_rd * l_tot) / (beta_D * e_modul * i_y) * 100  # Design elastic rotation angle
            phi_ed = phi_roted - phi_pled  # Maximum design rotation angle
    
            # Design plastic rotation angle
    
            # def phi_cd_func(pile_type, pc, l_a_func):
            def f100_func(la):
                return (0 - 0.11) / (45 - 25) * la + (0.11 - (0 - 0.11) / (45 - 25) * 25)
    
            def f95_func(la):
                return (0 - 0.12) / (50 - 25) * la + (0.12 - (0 - 0.12) / (50 - 25) * 25)
    
            def f90_func(la):
                return (0 - 0.13) / (60 - 25) * la + (0.13 - (0 - 0.13) / (60 - 25) * 25)
    
            def f85_func(la):
                return (0 - 0.14) / (66 - 25) * la + (0.14 - (0 - 0.14) / (66 - 25) * 25)
    
            def g100_func(la):
                return (0 - 0.16) / (37 - 20) * la + (0.16 - (0 - 0.16) / (37 - 20) * 20)
    
            def g95_func(la):
                return (0 - 0.17) / (40 - 20) * la + (0.17 - (0 - 0.17) / (40 - 20) * 20)
    
            def g90_func(la):
                return (0 - 0.18) / (46 - 20) * la + (0.18 - (0 - 0.18) / (46 - 20) * 20)
    
            def g85_func(la):
                return (0 - 0.19) / (49 - 20) * la + (0.19 - (0 - 0.19) / (49 - 20) * 20)
    
            phi_cd = np.zeros(num_sheetpiles)
            control_rot = np.empty(num_sheetpiles, dtype=object)
            for i in range(num_sheetpiles):
                phi_ = None
                if type_profile[i] == "Z":
                    if p_c[i] == 1.0:
                        phi_ = f100_func(l_a[i])
                    elif 0.95 < p_c[i] < 1.0:
                        phi_ = f95_func(l_a[i]) + (f100_func(l_a[i]) - f95_func(l_a[i])) * ((p_c[i] - 0.95) / (1.0 - 0.95))
                    elif 0.90 < p_c[i] <= 0.95:
                        phi_ = f90_func(l_a[i]) + (f95_func(l_a[i]) - f90_func(l_a[i])) * ((p_c[i] - 0.90) / (0.95 - 0.90))
                    elif 0.85 < p_c[i] <= 0.90:
                        phi_ = f85_func(l_a[i]) + (f90_func(l_a[i]) - f85_func(l_a[i])) * ((p_c[i] - 0.85) / (0.90 - 0.85))
                    elif p_c[i] <= 0.85:
                        phi_ = f85_func(l_a[i])
                elif type_profile[i] == "U":
                    if p_c[i] == 1.0:
                        phi_ = g100_func(l_a[i])
                    elif 0.95 < p_c[i] < 1.0:
                        phi_ = g95_func(l_a[i]) + (g100_func(l_a[i]) - g95_func(l_a[i])) * ((p_c[i] - 0.95) / (1.0 - 0.95))
                    elif 0.90 < p_c[i] <= 0.95:
                        phi_ = g90_func(l_a[i]) + (g95_func(l_a[i]) - g90_func(l_a[i])) * ((p_c[i] - 0.90) / (0.95 - 0.90))
                    elif 0.85 < p_c[i] <= 0.90:
                        phi_ = g85_func(l_a[i]) + (g90_func(l_a[i]) - g85_func(l_a[i])) * ((p_c[i] - 0.85) / (0.90 - 0.85))
                    elif p_c[i] <= 0.85:
                        phi_ = g85_func(l_a[i])
    
                if phi_ is None:
                    raise Exception("ERROR in phi_cd_func!")
    
                phi_cd[i] = phi_
    
                control_rot[i] = 'OK!' if phi_cd[i] > phi_ed[i] else 'NOT OK!'
    
        return {
            "control_rot": control_rot,
            "u_relvbuck": u_relvbuck,
            "u_relbuck": u_relbuck,
            "u_relcomb": u_relcomb,
            "u_relm": u_relm,
            "u_relv": u_relv,
            "u_relncr": u_relncr,
            "u_reln": u_reln
        }
    
    # NEW!!!!!!!!!!!!
    #Calculations
    results_df = pd.DataFrame(columns=[sheetpile])
    results_rot_cap = pd.DataFrame(columns=[sheetpile])
    
    for index, row in loads_df.iterrows():
        results = main(row["Corrosion"], row["Shear"], row["Axial_force"], row["Moment"])
        u_reloptimize = np.maximum.reduce([results["u_relm"], results["u_relv"], results["u_relncr"], results["u_reln"],
                                                  results["u_relvbuck"], results["u_relbuck"], results["u_relcomb"]])
        results_df.loc[len(results_df)] = u_reloptimize
        results_df_red = results_df.max().to_numpy()
    
        results_rot_cap.loc[len(results_rot_cap)]=results["control_rot"]
    
    def check_column(column):
        if 'NOT OK!' in column.values:
            return 'NOT OK!'
        else:
            return 'OK!'
    
    results_rot_cap_red = results_rot_cap.apply(check_column).to_numpy()
    
    
    # MRCH if skrevet lidt mere explicit.
    if profile == 'Optimize-700':
        section_match = type_profile_2 == "Z-700"
    elif profile == 'Optimize-750':
        section_match = type_profile_2 == "Z-750"
    elif profile == 'Optimize-770':
        section_match = type_profile_2 == "Z-770"
    elif profile == 'Optimize-800':
        section_match = type_profile_2 == "Z-800"
    elif profile == 'Optimize-Z':
        section_match = type_profile == "Z"
    elif profile == 'Optimize-U':
        section_match = type_profile == "U"
    else:
        section_match = np.full(num_sheetpiles, True)
    
    # Print results
    print('')
    print('## RESULTS ######################')
    result = None
    if 'Optimize' not in profile:
        result = 0
        if results_df_red[result] > max_util:
            print("")
            print("WARNING: Overutilization ("+str(round(results_df_red[result], 2))+">"+"{:.2f}".format(max_util)+")")
            print("")
    else:
        match = np.where(section_match & (results_df_red <= max_util) & (results_rot_cap_red != "NOT OK!"))
    
        if len(match) == 0 or min(u_reloptimize) > max_util:
            print('No sheet pile could be found!')
        else:
            max_ = max(results_df_red[match])                # max utilization still below max_util (optimal solution)
            result, = np.where(results_df_red == max_)  # index of optimal solution
            result = result[0]
    
    if result is not None:
        
        
        u_rel = round(results_df_red[result], 2)
        control_Rot = results_rot_cap_red[result]
        Sheetpile = sheet_db.index[result]
        results_df_as_array = results_df.to_numpy()
        u_rel_lvl = pd.DataFrame(results_df_as_array[:,result], columns=["u_rel"], index=lvl_list)
        # MRCH: Det afrundede antal decimaler og din format ("{:.2f}") bør være samme tal. Ved afrund til 3 cifre, men kun 2 viste tal bliver f.eks. 0.175 til 0.17 istedet for 0.18
        print('Sheet Pile Profile:                   ' + Sheetpile)
        print('Relative utilization ratio:           ', "{:.2f}".format(u_rel))
        print('Rotational Capacity:                  ' + control_Rot)
        print('relative utilization ratio per data point:')
        print(u_rel_lvl)
        print('#################################')
        
        
        
        Results = {'SheetPileProfile': Sheetpile,
                   'RUR': u_rel,
                   'RURLevel': u_rel_lvl,
                   'RURLevel_max': u_rel_lvl.idxmax()['u_rel'],
                   'RotCap': control_Rot}
        
    else:
        
        Results = {'SheetPileProfile': 'N/A',
                   'RUR': 'N/A',
                   'RURLevel': 'N/A',
                   'RotCap': 'N/A'}
        
        
        
    print(loads_df)

        
    return Results
        

################### Added by EMBT 30.11.2023 #################################



def failure_detector(iA, iB, iC):
    
    if abs(iA) - 1 < 0.001 and 1 - iC < 0.001:
        
        failure_mode = '2FC'
    
    elif iA == 0 and 1 - iC < 0.001:
        
        failure_mode = '1FC'
        
    else:
        
        failure_mode = '0FC'
        
    
    return failure_mode
        

# def find_closest_val_tuples_list(tuples_list, target):
#     return min(tuples_list, key=lambda x: abs(x[0] - target))


def steel_sheet_pile_implementer(GetResultsOutput):
    
    Analysis = GetResultsOutput.get('Analysis')
    SheetPileAddOnInput = Analysis.get('SheetPileAddOnInput')
    Results = GetResultsOutput.get('Results')
    PlotResults = GetResultsOutput.get('PlotResults')    
    AxialWallLoad = Analysis.get('AxialWallLoad')
    
    ## Steel sheet pile wall add on
    profile =  SheetPileAddOnInput.get('Optimize')  # Choose profile or optimization.
    max_util = SheetPileAddOnInput.get('MaxUtilization')  # Max utilization ratio allowed
    LS_calc = SheetPileAddOnInput.get('LimitState')  # Choose limit state and calculation Type: XXX-YYYYYYY.
    Ctl_cl = SheetPileAddOnInput.get('ControlClass')  # Control Class: normal, strict
    K_FI_cl = SheetPileAddOnInput.get('KFI') # Consequence Class: CC3, Disable
    fyk = SheetPileAddOnInput.get('fyk')  # Char. Yield Strength [MPa]
    e_modul = 210  # Elastic Modulus [GPa]
    beta_B = SheetPileAddOnInput.get('BetaB')  # 1.0 for Z-piles. For U-piles see DS/EN 1993-5 DK NA)
    beta_D = SheetPileAddOnInput.get('BetaD')  # 1.0 for Z-piles. For U-piles see DS/EN 1993-5 DK NA)
    t_cor_input_list = SheetPileAddOnInput.get('tCor')
    t_cor_lvl_input_list = SheetPileAddOnInput.get('tCorLevel')
    soil_comp = SheetPileAddOnInput.get('SoilDeposit')
    exca_level = Analysis.get('SoilLayersFront')[0].get('TopLayer')
    WaterLevelFront = Analysis.get('WaterLevelFront')
    w_dif = Analysis.get('WDiff')
    zT = Analysis.get('zT')
    iA = Analysis.get('iA')
    iB = Analysis.get('iB')
    iC = Analysis.get('iC')
    failure_mode = failure_detector(iA, iB, iC)
    
    
    w_1clc = None  # Calculated displacement, if None not used.
    w_2clc = None  # Calculated displacement, if None not used.
    w_3clc = None  # Calculated displacement, if None not used.
    

    try: 
        AnchorLevel = GetResultsOutput.get('Analysis').get('AnchorLevel')
        AnchorInclination = GetResultsOutput.get('Analysis').get('AnchorInclination')
        AnchorForce = GetResultsOutput.get('Results').get('AnchorForce')
        AnchorAxial = AnchorForce/np.cos(np.radians(AnchorInclination))

    except:
        AnchorLevel = 'N/A'
        AnchorInclination = 'N/A'
        AnchorForce = 'N/A'
        AnchorAxial = 'N/A'
    ToeLevel = GetResultsOutput.get('Results').get('ToeLevel')
    WallMass = GetResultsOutput.get('Analysis').get('WallMass')
    WallSpecificWeight = WallMass * 9.82 / 1000
    WeightWallTotal = WallSpecificWeight * (zT - ToeLevel)
    
    
    if AnchorLevel != 'N/A':
        
        N_Ed = AnchorAxial*np.sin(np.radians(float(AnchorInclination))) + WeightWallTotal + AxialWallLoad
    else:
        N_Ed =  WeightWallTotal + AxialWallLoad
        
    print('Ned '+str(N_Ed))
    
    
    #### Spooks results
    
    pl_level = Results.get('ToeLevel')
    maxm_level = PlotResults.get('LevelMaxMoment')
    MEd_list = PlotResults.get('Moment')
    VEd_list = PlotResults.get('ShearForce')
    lvl_list = PlotResults.get('PlotLevels')
    NEd_list = []
    for i in range(len(lvl_list)):
        NEd_list.append(N_Ed)
    m_ind_level = 0  # Level of 2nd max moment for 2FC. Variable can be set to anything for 1FC.
    
    ### Mobilized passive earth pressure below water level
    if pl_level <= WaterLevelFront:
        
        mob_vp = 'Yes'
        
    else:
        
        mob_vp = 'No'
    
    
    
    if Analysis.get('AnchorLevel') != None:
        anchor_level = Analysis.get('AnchorLevel')

        L = abs(anchor_level - pl_level)
        
    else:
        
        anchor_level = None

        L = abs(zT - pl_level)
    

    Results = sheet_pile_add_on(profile, max_util, LS_calc, Ctl_cl, K_FI_cl, fyk, e_modul, 
                          beta_B, beta_D, t_cor_input_list, t_cor_lvl_input_list, MEd_list, VEd_list, NEd_list,
                          lvl_list, w_dif, L, failure_mode, soil_comp, pl_level, maxm_level, anchor_level,
                          m_ind_level, exca_level, mob_vp, w_1clc, w_2clc, w_3clc, sheet_db, sheetpile)

    
    
    return Results

