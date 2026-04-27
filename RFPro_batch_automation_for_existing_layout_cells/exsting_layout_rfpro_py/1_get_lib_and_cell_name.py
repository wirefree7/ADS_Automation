import json
import os


def get_layout_and_lib_names():
    import os      # For interacting with the operating system
    #import sys     # For accessing system-specific parameters and functions
    import time    # For measuring execution time
    
    os.environ["QT_LOGGING_RULES"] = r"*.debug=false"  # Disable Qt debug logging
    os.environ["HPEESOF_DIR"] = r"C:\Keysight\ADS2026"  # Set ADS installation directory
    from keysight.ads import de
    HOME = r"C:\Engineering\Script\Read_Cell_name\Existing_layout_EM"  # Home directory for workspaces
    wrk_name = "Read_Cell_Name_wrk"  # Workspace name
    wrk_path = os.path.join(HOME, f"{wrk_name}")
    wrk = de.open_workspace(wrk_path)

    workspace = de.active_workspace()
    libraries = workspace.writable_libraries

    results = []
    
    for lib in libraries:
        cells = lib.cells
        lib_name = lib.name

        print(f"\n {lib_name}   ")
        layout_count = 0
        
        for cell in cells:
            
            cell_name = cell.name

            if "layout" not in cell.views:
                print(f"Schematic Cell Library: {lib}, Cell: {cell_name}")
                
                
            else:
                layout_count += 1
                print(f"--> Layout Cell Library: {lib}, Cell: {cell_name}")
                results.append({
                    "layout_count": layout_count,
                    "lib_name": lib_name,
                    "cell_name": cell_name
                })
    json_file_path = os.path.join(HOME, "result.json")
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


    print("waiting...for 5 seconds to complete process") # Sleep for 5 seconds to ensure environment is set up
    time.sleep(5)
    print("Completed.")
    print(f"Library and cell names saved to {json_file_path}.")
    print("\n")
if __name__ == "__main__":
    get_layout_and_lib_names()
