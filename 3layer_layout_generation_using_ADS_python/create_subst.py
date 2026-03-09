# Copyright Keysight Technologies 2024 - 2024 ////Create Substrate///
from keysight.ads import de
from keysight.ads import subst as substrate
from keysight.ads.de import db_uu
from keysight.ads.de.db import LayerId
import os
import time


def create_substrate(wrk_name, lib, HOME, Er, H_um, tanD, metal_T) -> None:
    wrk_space_path = os.path.join(HOME, wrk_name)
    wrk = de.open_workspace(wrk_space_path)
    lib_path = de.get_path_to_open_library(lib)
    library = wrk.open_library(lib, lib_path, mode=de.LibraryMode.SHARED)
    #library = de.Library.get(lib)

    new_er = str(Er)
    new_tanD = str(tanD)

    # Define the materials.matdb file content
    xml_content = f"""<!DOCTYPE Materials>
    <Materials>
        <Conductors>
            <Conductor name="Copper" tnom="" real="5.8e7 Siemens/m" electron_path="" parmtype="1" mur_real="1" thermal_conductivity="401" imag="" tc1="" mur_imag="" thermal_conductivity_in_z="" heat_capacity="2.49E+06" tc2=""/>
            <Conductor name="Gold" tnom="" real="4.1e7 Siemens/m" electron_path="" parmtype="1" mur_real="1" thermal_conductivity="318" imag="" tc1="" mur_imag="" thermal_conductivity_in_z="" heat_capacity="2.49E+06" tc2=""/>
        </Conductors>
        <Dielectrics>
            <Dielectric name="Air" er_loss="" electron_path="" er_real="1.0" loss_type="1" mur_real="1" thermal_conductivity="0.027" mur_imag="" valuefreq="1 GHz" thermal_conductivity_in_z="" heat_capacity="1.18E+03" highfreq="1 THz" lowfreq="1 KHz" er_imag=""/>
            <Dielectric name="Alumina" er_loss="" electron_path="" er_real="9.6" loss_type="1" mur_real="1" thermal_conductivity="25.25" mur_imag="" valuefreq="1 GHz" thermal_conductivity_in_z="" heat_capacity="1.73E+063" highfreq="1 THz" lowfreq="1 KHz" er_imag=""/>
            <Dielectric name="em_Sub" er_loss="{new_tanD}" electron_path="" er_real="{new_er}" loss_type="1" mur_real="1" thermal_conductivity="" mur_imag="" valuefreq="1 GHz" thermal_conductivity_in_z="" heat_capacity="" highfreq="1 THz" lowfreq="1 KHz" er_imag=""/>
        </Dielectrics>
    </Materials>
    """
    file_path = os.path.join(wrk_space_path, lib, "materials.matdb")

    # Write the XML content to the new file
    with open(file_path, "w") as file:
        file.write(xml_content)
        # print(f"Data written to {file_path}")



#///////////////////////////////////////////////////////////////////////////
    #assert not library.is_read_only
    # Create the substrate definition from Python
    subst_name = "demo_substrate"

    # Start by creating an "empty" substrate.
    subst = substrate.create_substrate(library, subst_name) #library, subst_name
    assert substrate.substrate_exists(library, subst_name) #library, subst_name
    assert not subst.is_read_only
    assert subst.is_writable

    # See what materials are available
    if False:
        names = substrate.get_conductor_names(library)
        assert len(names) != 0
        names = substrate.get_semiconductor_names(library)
        names = substrate.get_superconductor_names(library)
        names = substrate.get_dielectric_names(library)
        names = substrate.get_roughness_names(library)

    # If you need to specify a list of purposes to ignore, use this
    if True:
        subst.purposes_to_exclude = ["Dummy"]
        assert not subst.purposes_to_include
    else:
        subst.purposes_to_include = ["Drawing"]
        assert not subst.purposes_to_exclude
        
    # This substrate will have two infinite materials and three interfaces
    assert len(subst.materials) == 2 #2
    assert len(subst.interfaces) == 3 #3
    assert subst.materials[0].is_infinite_material
    top_material_index = subst.top_material_index
    assert subst.materials[top_material_index].is_infinite_material
    assert not subst.has_top_cover
    interface0 = subst.interfaces[0]
    assert not interface0.is_cover
    assert interface0.is_non_cover_placeholder    
    ####////////////여기까지 에러 없음. 
    
     # Convert the bottom interface to a cover
    if False:
        # The hard way
        interface0.purpose = substrate.InterfaceItem.Purpose.COVER
        interface0.material_name = "Gold" #PERFECT_CONDUCTOR
    else:
        interface0.convert_to_cover()
    interface0.thickness_expr = "0.123"  # just so we can identify this interface
    interface0.thickness_unit = substrate.Unit.MICRON
    interface0.material_name = "Gold"
    assert interface0.is_cover
    assert not interface0.is_non_cover_placeholder
    assert subst.has_bottom_cover
    
    material0 = subst.materials[0] #<-- 0은 lowest material의 위치 
    # Since the bottom interface is now a cover, material0 won't be infinite
    #assert not material0.is_infinite_material
    material0.thickness_expr = str(H_um)
    material0.thickness_unit = substrate.Unit.MICRON #MILLIMETER
    material0.material_name = "em_Sub"
    #from help code/////////////////////////////
    
    interface1 = subst.interfaces[1] #--> [1] no error
    if True:
        # You can specify interface by index
        layer1 = subst.insert_layer(1, de.ProcessRole.CONDUCTOR) #--> 0 lowest interface, 1 2nd, 2-3rd interface, 2 4th-error with interface[1]
    else:
        # You can can also pass interfaces
        layer = subst.insert_layer(interface1, de.ProcessRole.CONDUCTOR)
    layer1.layer_number = 16 # metal layer number : 0-cond 1-cond2 16-pc1 
    layer1.material_name = "Copper"
    layer1.thickness_expr = str(metal_T)
    layer1.thickness_unit = substrate.Unit.MICRON #MILLIMETER
    # The layer item can represent a sheet that neither expands nor intrudes into the material.
    #assert layer1.sheet is False --> error line
    layer1.sheet = False
    layer1.expand = True  # Otherwise we intrude
    # Note that setting is_above to False sets the thickness negative
    layer1.is_above = False   #False - so it expands the material above the interface / True -QE 
    #assert layer.thickness_expr == "-0.01"
    #subst.save_substrate()
    #/////////////
    #if True:
        # This will leave the bottom material and layer alone
    subst.insert_material_and_interface_above(1) #<-- 0Bottom Air , 1midd Air, 2upper Air material정의 없으므로 Air
    
    material1 = subst.materials[1] #<-- material1 location 0 bottom material, 1 midd material,2 upper  
    material1.thickness_expr = "200"
    material1.thickness_unit = substrate.Unit.MICRON #MILLIMETER
    material1.material_name = "Alumina"
    subst.save_substrate()
    #///////////////
    
    # If we set the thickness of the top material, it won't
    # be relevant because there is no top cover so the material is infinite.
    material2 = subst.materials[2]
    material2.thickness_expr = str(H_um)
    material2.thickness_unit = substrate.Unit.MICRON
    material2.material_name = "em_Sub"
    #assert material2.is_infinite_material
    subst.save_substrate()

    # If we add one more material and interface, material2 won't be infinite.
    subst.insert_material_and_interface_below(3)
    assert not material2.is_infinite_material
    assert material2.thickness == 138

    interface2 = subst.interfaces[2] #--> [1] no error
    if True:
        # You can specify interface by index
        layer2 = subst.insert_layer(2, de.ProcessRole.CONDUCTOR) #--> 0 lowest interface, 1 2nd, 2-3rd interface, 2 4th-error with interface[1]
    else:
        # You can can also pass interfaces
        layer = subst.insert_layer(interface1, de.ProcessRole.CONDUCTOR)
    layer2.layer_number = 2 # <-- 1 -QE
    layer2.material_name = "Copper"
    layer2.thickness_expr = str(metal_T)
    layer2.thickness_unit = substrate.Unit.MICRON #MILLIMETER
    # The layer item can represent a sheet that neither expands nor intrudes into the material.
    #assert layer1.sheet is False --> error line
    layer2.sheet = True
    layer2.expand = False  # Otherwise we intrude

    interface3 = subst.interfaces[3] #--> [1] no error
    if True:
        # You can specify interface by index
        layer3 = subst.insert_layer(3, de.ProcessRole.CONDUCTOR) #--> 0 lowest interface, 1 2nd, 2-3rd interface, 2 4th-error with interface[1]
    else:
        # You can can also pass interfaces
        layer = subst.insert_layer(interface1, de.ProcessRole.CONDUCTOR)
    layer3.layer_number = 1 # <-- 1 -QE
    layer3.material_name = "Copper"
    layer3.thickness_expr = str(metal_T)
    layer3.thickness_unit = substrate.Unit.MICRON #MILLIMETER
    # The layer item can represent a sheet that neither expands nor intrudes into the material.
    #assert layer1.sheet is False --> error line
    layer3.sheet = True
    layer3.expand = False  # Otherwise we intrude
    subst.save_substrate()
    
    
    """via layer
    if False:
        # The basic function...
        via = subst.insert_via(1, 2, de.ProcessRole.CONDUCTOR_VIA)
    elif False:
        # You can specify interface by index
        via = subst.insert_conductor_via(1, 2)
    else:
        # You can can also pass interfaces
        interface2 = subst.interfaces[2]
        via = subst.insert_conductor_via(interface1, interface2)"""
    
    """
    via.layer_number = 3  # cond2
    via.material_name = "Gold"
    assert via.process_role == de.ProcessRole.CONDUCTOR_VIA
    via.is_plating_enabled = True
    via.plating_dielectric_material_name = "em_Sub"
    via.plating_thickness = 0.1
    via.plating_thickness_unit = substrate.Unit.MICRON #MILLIMETER"""
    subst.save_substrate() 
    """
    ### nested 
    nested_subst = subst.insert_substrate(interface2)
    nested_subst.set_library_and_substrate_names(library.name, "empty")
    assert nested_subst.library_name == library.name
    assert nested_subst.substrate_name == "empty"

    # There are three choices for alignment
    if False:
        nested_subst.align_type = substrate.SubstrateItem.AlignType.BOTTOM
    elif False:
        nested_subst.align_type = substrate.SubstrateItem.AlignType.TOP
    else:
        nested_subst.align_type = substrate.SubstrateItem.AlignType.LAYER
    # When aligning with a layer, we have to specify which part of the layer aligns
    nested_subst.alignment_position = substrate.SubstrateItem.AlignPosition.TOP_OF_LAYER
    nested_subst.align_layer_name = "cond2"
    subst.save_substrate()

    # If you don't need it any more, you can delete it
    if False:
        substrate.delete_substrate(library, subst_name)
    """
    
    
    
