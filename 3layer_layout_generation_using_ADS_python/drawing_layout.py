# Copyright Keysight Technologies 2024 - 2024
from keysight.ads import de
from keysight.ads import subst as subst
from keysight.ads.de import db_uu
from keysight.ads.de.db import LayerId
import numpy as np
import time 
import  os
import shutil
import random
import keysight.edatoolbox.multi_python as multi_python


def design_sample_layout(Er, H_um, wrk_name, lib, cell, HOME):  
    start_time = time.time()  # Start time for code execution
    wrk_space_path = os.path.join(HOME, wrk_name)
    if os.path.exists(wrk_space_path):
        shutil.rmtree(wrk_space_path)
    de.create_workspace(wrk_space_path)
    wrk_space = de.open_workspace(wrk_space_path)
    library = de.create_new_library(lib, os.path.join(wrk_space_path, lib))
    library.setup_schematic_tech()
    library.create_layout_tech_std_ads("micron", 10000, False) #ads("millimeter", 10000, False)
    wrk_space.add_library(
        lib, os.path.join(wrk_space_path, lib), mode=de.LibraryMode.SHARED
    )

    

        
    design = db_uu.create_layout(lib + ":" + cell + ":" + "layout")
    layer_id = design.create_layer_id("cond") #cond
    #//////////////////////////////////////
    # Add a 300x100 rectangle on the left on layer "cond:drawing"
    cond = layer_id.create_layer_id_from_library(library, "cond", "drawing")
    design.add_rectangle(cond, (0, 0), (160, 500))
        
    # Add a 200x100 rectangle overlapping first rectangle on the right on layer "cond2:drawing"
    cond2 = layer_id.create_layer_id_from_library(library, "cond2", "drawing")
    design.add_rectangle(cond2, (62, 0), (98, 500))
    
    # Add a 300x100 rectangle on the left on layer "cond:drawing"
    pc1 = layer_id.create_layer_id_from_library(library, "pc1", "drawing")
    design.add_rectangle(pc1, (0, 0), (160, 500))
    """
        # Add a radius 30 circle in the overlapping portion of the two rectangles on layer "hole:drawing"
        hole = layer_id.create_layer_id_from_library(library, "hole", "drawing")
        design.add_circle(hole, (250, 50), 30) """

        # Add a pin on the ground net on the left side of the cond layer's rectangle
                
    pin1_pinfig = design.add_dot(cond2, (80, 0))
    net = design.find_or_add_net("P1")
    term_1 = design.add_term(net, "P1")
    design.add_pin(term_1, pin1_pinfig, angle=270.0)

        # Add a pin on the ground net on the right side of the cond2 layer's rectangle
    pin2_pinfig = design.add_dot(cond2, (80, 500))
    net = design.find_or_add_net("P2")
    term_2 = design.add_term(net, "P2")
    design.add_pin(term_2, pin2_pinfig, angle=90.0)
        
        # Add a pin on the ground net on the left side of the cond layer's rectangle
    pin3_pinfig = design.add_dot(cond, (80, 0))
    gnd_net = design.find_or_add_net("gnd!")
    gnd_3 = design.add_term(gnd_net, "P3")
    design.add_pin(gnd_3, pin3_pinfig, angle=270.0)

        # Add a pin on the ground net on the right side of the cond2 layer's rectangle
    pin4_pinfig = design.add_dot(cond, (80, 500))
    gnd_4 = design.add_term(gnd_net, "P4")
    design.add_pin(gnd_4, pin4_pinfig, angle=90.0)
        
        # Add a pin on the ground net on the left side of the cond layer's rectangle
    pin5_pinfig = design.add_dot(pc1, (80, 0))
    gnd_net = design.find_or_add_net("gnd!")
    gnd_5 = design.add_term(gnd_net, "P5")
    design.add_pin(gnd_5, pin5_pinfig, angle=270.0)

        # Add a pin on the ground net on the right side of the cond2 layer's rectangle
    pin6_pinfig = design.add_dot(pc1, (80, 500))
    gnd_6 = design.add_term(gnd_net, "P6")
    design.add_pin(gnd_6, pin6_pinfig, angle=90.0)
    # Save changes to the layout file
    design.save_design()

        #return design --> Disable to avoid 'workspace already open error'///////////////////////////
                          
    design.save_design()
    end_time = time.time()  # End time for code execution
    print("Layout created in ", round(end_time - start_time, 2), " seconds")
    
    print(f"Layout Created Successfully")
    de.close_workspace()
