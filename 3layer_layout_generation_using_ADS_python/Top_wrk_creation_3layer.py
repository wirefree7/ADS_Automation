"""
1. This code is verified to work with ADS2025 Update 2_1
2. Make sure to specify correct HPEESOF_DIR on line 11
3. Ensure the Python interpreter in VS Code is set to <HPEESOF_DIR>/tools/python/python.exe
4. Set the Home directory to be created workspace in that folder on line 27. 
"""
import shutil
import os
import sys
import time
os.environ["QT_LOGGING_RULES"] = r"*.debug=false"
os.environ["HPEESOF_DIR"] = r"C:\Keysight\ADS2025_Update2_1"

# Multi-Python module was introduced in EDAtoolbox 1.2.2 that ships with ADS2025U1, any version higher that this should work
import keysight.edatoolbox.multi_python as multi_python

# Add current file directory to the system path so that dependent files could be located
current_directory = os.path.dirname(os.path.abspath(__file__))
module_path = current_directory
if module_path not in sys.path:
    sys.path.append(module_path)

# ADS Workspace Details
wrk_name = "demo04_wrk"
lib = "demo04_lib"
cell = "Cell_lay"
HOME = r"c:\Users\jaehyuki\ADS_wrk\Py_Prj\inv_Multi_tech"
# Define sample Design Inputs & Stackup Parameters

Er = 9.6                # Dielectric Constant
H_um = 138            # Substrate Thickness in um
tanD = 0.0023           # Dielectric Loss Tangent
metal_T = 18         # Metal Thickness in um


def wrk_ckt_part(cell):
    import keysight.ads.de as de

    from create_rfpro_view import (
        create_rfpro_view,
        
    )

    from drawing_layout import (
        design_sample_layout
    )
    from create_subst import (
    create_substrate
    )
    cell_name = cell
  
    design_sample_layout(
        Er,
        H_um,
        wrk_name,
        lib,
        cell,
        HOME,
    )
    create_substrate(wrk_name, lib, HOME, Er, H_um, tanD, metal_T)
    
    cell = cell_name
    print("Creating RFPro View for ", cell)
    create_rfpro_view(wrk_name, lib, cell, HOME)
    de.close_workspace()
    print("Workspace and Layout created in ADS\n")

if __name__ == "__main__":
    start = time.time()

    with multi_python.ads_context() as ads_ctx:
        ads_ctx.call(wrk_ckt_part, args=[cell])

    def rfpro_sims():
        from RFPro_EM_Setup_ads2025u2 import rfpro_sim_setup

        with multi_python.xxpro_context() as empro_ctx:
            empro_ctx.call(
                rfpro_sim_setup, args=[wrk_name, lib, cell, HOME]
            )
    rfpro_sims()
    stop = time.time()
    print(
        f"Overall execution time forsimulation: ",
        round(stop - start, 2),
        " seconds",
    )
