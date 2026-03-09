import os
import time
import keysight.edatoolbox.multi_python as multi_python
from keysight.ads import emtools  # Only valid for ADS2025U1
from keysight.ads.de import ael



def create_rfpro_view(wrk_name, lib, cell, HOME):

    start = time.time()

    wrk = os.path.join(HOME, wrk_name)

    # New view creator in ADS2025U1 that speeds up xxpro view creation
    emtools.create_empro_view(
        (lib, cell, "rfprosetup"),
        "rfpro",
        (lib, cell, "layout"),
        (lib, "demo_substrate.subst"),
    )
    
    extraInputDir = os.path.join(wrk, "simulation", lib, cell, "rfprosetup", "extra", "0")
    os.makedirs(extraInputDir, exist_ok=True)
    ael.emIfcApply_generateOaExtraInput(
        extraInputDir, lib, cell,"layout", lib, "demo_substrate.subst"
    )
    
    # create_pro_view is the old way of creating xxpro view that takes longer time
    # ads_app.create_pro_view(wrk,input_lcv=input_lcv,substrate="demo_substrate",pro_lcv=pro_lcv,tool="rfpro",)
    # de.close_workspace()

    stop = time.time()
    print("RFPro view created in ", round(stop - start, 2), " seconds")
