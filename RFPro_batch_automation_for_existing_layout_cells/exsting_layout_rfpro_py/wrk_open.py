# Copyright Keysight Technologies 2024 - 2024
from keysight.ads import de
from keysight.ads import subst as subst
import time 
import  os




def workspace_open(
    Num_layout, wrk_name, lib_name, cell, HOME, 
):  
    

    start_time = time.time()  # Start time for code execution

    
    wrk_space_path = os.path.join(HOME, wrk_name)

    wrk_space = de.open_workspace(wrk_space_path) #Do not delete
    
    
    print(f"Workspace has been opened Successfully")
    #de.close_workspace()
