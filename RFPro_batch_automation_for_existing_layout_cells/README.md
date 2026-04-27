Jaehyuk Kim
Aug. 28. 2025
ADS Python API of RFPro Batch for Exisiting(Pre-designed) layout cells

# Notice
This is a personal project files of Jaehyuk Kim.
Not provided official purpose. Will not support for the any trouble shooting. You can edit and modify and use it.

# Assumptions and Preconditions

- "The Python scripts are intended to be executed in Visual Studio Code, with the interpreter set to the python.exe found in the ADS
installation path.“
- "In this example, existing layout cell names are distinguished and collected within libraries, and rfproviews are created for each
library's cells, followed by sequential RFPro EM simulations.
- "This example assumes that the layout is designed based on a 2-port configuration, where p1 and p2 are the input and output ports,
and p3 and p4 are the corresponding ground ports.
It also considers a scenario in which multiple circuit cells and layout cells are mixed across within multiple libraries.“
- " Existing Layout means the user designed layout cells into workspace of ADS already, and the user want to run EM simulation
automatically like a batch simulation with layout cells.”
- "If the three Python files mentioned above are handled by a single wrapper, errors may occur due to timing issues between each
process."


# How to run this example
- VS code is used to run py files using python scripts
- To run this example, follo the below steps

1. Run 1_get_lib_cell_name.py to collect library and layout cell names
Set the ADS directory, Set the HOME directory, Set the workspace name, then Run
2. Run 2_Top_rfpro_from_json_2.py to generate rfproview, EM setup and to run simulation
Set the ADS directory, Set the HOME directory, Set the workspace name, then Run
3. Run 3_plot.py to generate pdf for the RFPro results
Set the HOME directory, Set the workspace name, then Run


## Flow chart of python files
1_get_lib_cell_name.py :  To collect library and Layout cell names from the workspace
2_Top_rfpro_from_json  :  To open workspace with information of lib and cell names, To create rfproview for each of layout cells, To set EM setup for each rfproview
3_plot.py : To PDF creation with rfpro simulation results


## Summary
- This example can be applied when a customer has pre-created layout cells for various reasons.To run this example, follo the below
steps
- Python script, it is possible to identify the names of layout cells among the available cells and automatically generate an EM
simulation batch.
- Batch generation is also possible even when multiple libraries and multiple cells are mixed.
- A possible next task could involve generating batches based on data, depending on how cells differ in port count and configuration.

