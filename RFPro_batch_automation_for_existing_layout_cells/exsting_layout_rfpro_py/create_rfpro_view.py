import os
import time
import keysight.edatoolbox.multi_python as multi_python
from keysight.ads import de
from keysight.ads import emtools  
from keysight.ads.de import ael



def create_rfpro_view(wrk_name, lib, cell, HOME):

    start = time.time()

    wrk = os.path.join(HOME, wrk_name)
    de.Library.open(lib, os.path.join(wrk, lib), mode=de.LibraryMode.SHARED)
    
    emtools.create_empro_view(
        (lib, cell, "rfprosetup"),
        "rfpro",
        (lib, cell, "layout"),
        (lib, "tech.subst"),
    )

    extraInputDir = os.path.join(wrk, "simulation", lib, cell, "rfprosetup", "extra", "0")
    os.makedirs(extraInputDir, exist_ok=True)
    ael.emIfcApply_generateOaExtraInput(
        extraInputDir, lib, cell, "layout", lib, "tech.subst"
    )
    
    stop = time.time()
    print("RFPro view created in ", round(stop - start, 2), " seconds")
