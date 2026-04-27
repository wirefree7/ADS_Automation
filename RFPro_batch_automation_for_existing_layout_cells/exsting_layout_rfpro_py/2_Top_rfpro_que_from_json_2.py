# This codes valied with ADS2026 only

import os      # For interacting with the operating system
import sys     # For accessing system-specific parameters and functions
import time    # For measuring execution time
import json
from pprint import pprint

os.environ["QT_LOGGING_RULES"] = r"*.debug=false"  # Disable Qt debug logging
os.environ["HPEESOF_DIR"] = r"C:\Keysight\ADS2026"  #### Set ADS installation directory
import keysight.edatoolbox.multi_python as multi_python

current_directory = os.path.dirname(os.path.abspath(__file__))
module_path = current_directory
if module_path not in sys.path:
    sys.path.append(module_path)

# ADS Workspace Details
wrk_name = "Read_Cell_Name_wrk"  #### Set Workspace name
HOME = r"C:\Engineering\Script\Read_Cell_name\Existing_layout_EM" ### Set Home Directory


from collections import defaultdict

def load_cells_grouped_by_lib():
    with open(os.path.join(HOME, "result.json"), "r", encoding="utf-8") as f:
        json_data = json.load(f)

    lib_cell_map = defaultdict(list)
    for item in json_data:
        lib = item["lib_name"]
        cell = item["cell_name"]
        lib_cell_map[lib].append(cell)

    return lib_cell_map


lib_cell_map = load_cells_grouped_by_lib()
pprint(lib_cell_map)

def wrk_ckt_part(lib_cell_map):
    import keysight.ads.de as de
    from create_rfpro_view import create_rfpro_view
    from wrk_open import workspace_open

    for lib, cells in lib_cell_map.items():
        Num_layout = len(cells)
        workspace_open(Num_layout, wrk_name, lib, cells, HOME)

        for cell in cells:
            print(f"Creating RFPro View for {cell} in {lib}")
            create_rfpro_view(wrk_name, lib, cell, HOME)

        # Workspace close
        try:
            print(f"Closing workspace for {lib}")
            de.close_workspace()  #workspace_close()
        except Exception as e:
            print(f"Error closing workspace: {e}")

    
if __name__ == "__main__":
    lib_cell_map = load_cells_grouped_by_lib()
    start = time.time()  # Start timer

    with multi_python.ads_context() as ads_ctx:  # Start ADS context
        ads_ctx.call(wrk_ckt_part, args=[lib_cell_map])  # Call function to set up workspace and cells
    
    
    def rfpro_sims(lib_cell_map):
        from RFPro_EM_Setup_ads2026 import rfpro_sim_setup
        print("RFPro sim setup...")

        with multi_python.xxpro_context() as empro_ctx:
            for lib, cells in lib_cell_map.items():
                Num_layout = len(cells)
                print(f"Running RFPro simulation for libraries")
                empro_ctx.call(
                    rfpro_sim_setup, args=[Num_layout, wrk_name, lib, cells, HOME]
                )

        print("RFPro simulations completed.")

    rfpro_sims(lib_cell_map)
    print("RFPro simulations completed.")  # Print message indicating completion of RFPro simulations
    stop = time.time()  # Stop timer
    print(
        f"Overall execution time for simulation: ",
        round(stop - start, 2),
        " seconds",
    )


