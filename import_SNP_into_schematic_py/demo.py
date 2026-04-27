# isort: skip_file
"""
An S-parameter automated simulation example for ADS.

This example shows how to instantiate an SnP block, TermGs, and S-param
simulation controller into an ADS schematic.
"""

import os
from pathlib import Path
import re
from typing import List, Literal, Tuple, Union

from keysight import pwdatatools as pwdt
from keysight.edatoolbox import ads as edatoolbox_ads

HPEESOF_DIR = r"C:\Keysight\ADS2025_2_1"
os.environ["HPEESOF_DIR"] = HPEESOF_DIR

from keysight.ads import de as de  # noqa: E402
from keysight.ads.de import db_uu as db_uu # noqa: E402


def add_snp_instance_to_design(
    design: db_uu.Design,
    filepath: Union[str, os.PathLike],
    *,
    origin: Tuple[float, float] = (0, 0),
    name: str = "SnP1",
    portcount: int = -1,
    pin_names: Union[Literal["auto"], List[str]] = "auto",
) -> None:
    """
    Add an SnP instance to an ADS schematic.

    Parameters
    ----------
    design : db_uu.Design
        The design where the SnP instance will be added.
    filepath : Union[str, os.PathLike]
        The path to the SnP file.
    origin : Tuple[float, float], default (0, 0)
        The origin of the SnP instance.
    name : str, default "SnP1"
        The name of the new SnP instance.
    portcount : int, default -1
        The number of ports in the SnP file. If -1, the port count will be extracted
        from the file. If a positive integer, that will be used as the port count.
    pin_names : list of str or "auto", default "auto"
        The names of the SnP symbol's pins. These names are optionally displayed
        on the symbol.  If "auto", port names, if present, are extracted from the file
        and used as the symbol's pin names. If a list of strings is provided, those
        pin names are used as-is. If an empty list, no pin names are shown on the SnP
        symbol.
    """
    snp = design.add_instance(
        db_uu.LCVName("ads_datacmps", "SnP", "symbol"), origin, name=name
    )
    if portcount == -1:
        port_count, portnames_list = get_metadata_from_snp_file(filepath)
        if pin_names != "auto":
            portnames_list = pin_names
    else:
        port_count = portcount
        if pin_names == "auto":
            _, portnames_list = get_metadata_from_snp_file(filepath)
        else:
            portnames_list = pin_names
    port_names_string = make_port_names_string_for_snp_instance(portnames_list)
    with de.db.Transaction(design, "Edit params") as transaction:
        snp.parameters["File"].value = f'"{filepath}"'
        snp.parameters["NumPorts"].value = str(port_count)
        snp.parameters["Type"].value = "TouchstoneType"
        snp.parameters["PinSpacing"].value = "Tight"
        snp.parameters["port_name_list"].value = port_names_string
        snp.invoke_item_parameter_changed_callback(
            ["File", "NumPorts", "Type", "PinSpacing", "port_name_list"]  # type: ignore
        )
        transaction.commit()


def add_s_param_instance_to_design(
    design: db_uu.Design,
    *,
    origin: Tuple[float, float] = (0, 0),
    name: str = "SP1",
    start: float = 1e9,
    stop: float = 10e9,
    step: float = 1e9,
    freq_units: Literal["Hz", "kHz", "MHz", "GHz"] = "GHz",
) -> None:
    """
    Add an S-parameter sweep controller instance to a design.

    Parameters
    ----------
    design : db_uu.Design
        The design where the S-parameter sweep controller will be added.
    origin : Tuple[float, float], default (0, 0)
        The origin of the S-parameter sweep controller instance.
    name : str, default "SP1"
        The name of the new S-parameter sweep controller instance. This is an arbitrary
        decision by the user.
    start : float, default 1e9
        The start frequency of the sweep in Hz.
    stop : float, default 10e9
        The stop frequency of the sweep in Hz.
    step : float, default 1e9
        The frequency step of the sweep in Hz.
    freq_units : Literal["Hz", "kHz", "MHz", "GHz"], default "GHz"
        The frequency units to use in the simulation controller.

    Notes
    -----
    Note that start, stop, and step are *always* provided in Hz. The freq_units
    parameter is used to determine the final frequency units in the simulation
    controller's parameters. The frequency values are divided by the appropriate
    factor based on the freq_units parameter.
    """
    freq_units_upper = freq_units.upper()
    if freq_units_upper not in ("Hz", "KHZ", "MHZ", "GHZ"):
        raise ValueError(
            "Invalid frequency units. Must be 'Hz', 'kHz', 'MHz', or 'GHz'"
        )
    if freq_units_upper == "KHZ":
        freq_unit_final = "kHz"
        divide_by = 1e3
    elif freq_units_upper == "MHZ":
        freq_unit_final = "MHz"
        divide_by = 1e6
    elif freq_units_upper == "GHZ":
        freq_unit_final = "GHz"
        divide_by = 1e9
    else:
        freq_unit_final = "Hz"
        divide_by = 1.0
    start /= divide_by
    stop /= divide_by
    step /= divide_by
    s_param_sweep = design.add_instance(
        ("ads_simulation", "S_Param", "symbol"), origin, name=name
    )
    s_param_sweep.parameters["Start"].value = f"{start} {freq_unit_final}"
    s_param_sweep.parameters["Stop"].value = f"{stop} {freq_unit_final}"
    s_param_sweep.parameters["Step"].value = f"{step} {freq_unit_final}"


def add_termg_instances_to_design(
    design: db_uu.Design,
    *,
    origin: Tuple[float, float] = (0, 0),
    count: int = 1,
    x_offset: float = 2.5,
    y_offset: float = 2.0,
    ncols: int = -1,
    angle: float = -90,
) -> None:
    """
    Add one or more TermG instances to a design.

    The TermG instance names get auto-incremented from "TermG1" to "TermGn".

    Parameters
    ----------
    design : db_uu.Design
        The design where the TermG instances will be added.
    origin : Tuple[float, float], default (0, 0)
        The origin of the first TermG instance.
    count : int, default 1
        The number of TermG instances to add.
    x_offset : float, default 2.5
        The x offset between each TermG instance.
    y_offset : float, default 2.0
        The y offset between each TermG instance.
    ncols : int, default -1
        The number of columns to use when placing the TermG instances.
        This effectively controls the max number of TermG instances per row
        in the schematic. If -1, the number of columns is set to the count.
    angle : float, default -90
        The rotation angle of the TermG instances.
    """
    if ncols == -1:
        ncols = count
    # nrows = (count + ncols - 1) // ncols
    if ncols < 1:
        raise ValueError("ncols must be a positive integer or -1.")
    if count < 0:
        raise ValueError("count must be a non-negative integer")
    for i in range(count):
        name = f"TermG{i + 1}"
        total_x_offset = x_offset * (i % ncols)
        total_y_offset = y_offset * (i // ncols)
        design.add_instance(
            ("ads_simulation", "TermG", "symbol"),
            (origin[0] + total_x_offset, origin[1] - total_y_offset),
            name=name,
            angle=angle,
        )


def add_measeqn_to_design(
    design: db_uu.Design,
    equations: List[str],
    *,
    origin: Tuple[float, float] = (0, 0),
    name: str = "MeasEqn1",
) -> None:
    """
    Add a MeasEqn instance to a design.

    Parameters
    ----------
    design : db_uu.Design
        The design where the MeasEqn instance will be added.
    origin : Tuple[float, float], default (0, 0)
        The origin of the MeasEqn instance.
    name : str, default "MeasEqn1"
        The name of the new MeasEqn instance.
    equations : List[str]
        The equations to add to the MeasEqn instance.

    Notes
    -----
    MeasEqn has a 'SingleTextLine' formset.  You can query as follows:

    >>> measeqn_param = measeqn.parameters["Meas"]
    >>> measeqn_param_definition = measeqn_param.definition
    >>> measeqn_param_formset = measen_param_definition.formset.forms[0]
    >>> measeqn_param_formset_name = measeqn_param_forrmset.name

    To add more than one equation to a single MeasEqn block, you can use the
    `repeats` attribute of the MeasEqn block's `Meas` parameter.  Here is an
    example (where design is a schematic design object):

    >>> measeqn = design.add_instance(
    ...     db_uu.LCVName("ads_simulation", "MeasEqn", "symbol"),
    ...     (0.125, -3.875),
    ...     name="MyEquations",
    ...     angle=270,
    ... )
    >>> measeqn.parameters["Meas"].value = ["x=1"]
    >>> eq2 = de.db.ParamItemString(
    ...     "Meas", "SingleTextLine", "y=42"
    ... )
    >>> eq3 = de.db.ParamItemString(
    ...     "Meas", "SingleTextLine", "z=1e9"
    ... )
    >>> measeqn.parameters["Meas"].repeats.append(eq2)
    >>> measeqn.parameters["Meas"].repeats.append(eq3)
    >>> measeqn.update_item_annotation()
    """
    meas_eqn = design.add_instance(
        ("ads_simulation", "MeasEqn", "symbol"), origin, name=name, angle=-90
    )
    if not equations:
        return
    meas_eqn.parameters["Meas"].value = [equations[0]]
    if len(equations) > 1:
        for eq in equations[1:]:
            meas_eqn.parameters["Meas"].repeats.append(  # type: ignore
                de.db.ParamItemString("Meas", "SingleTextLine", eq)
            )
        meas_eqn.update_item_annotation()


def add_nets_to_instance(instance: db_uu.Instance, *, wire_length: float = 0.5) -> None:
    """
    Add nets to an instance's pins.

    Parameters
    ----------
    instance : db_uu.Instance
        The instance to add nets to.
    wire_length : float, default 0.5
        The length of the wires add to the instance's pins.  Must be greater than 0.
    """
    if wire_length <= 0:
        raise ValueError("wire_length must be greater than 0")
    for inst_pin in instance.inst_pins:
        if len(instance.inst_pins) > 1:
            netname = "Net_" + inst_pin.inst_pin_id.split(".")[1]
        else:
            netname = "Net_" + re.findall(r"\d+", inst_pin.inst_pin_id.split(".")[0])[0]
        point = inst_pin.snap_point
        if point is None:
            continue
        else:
            snap_x = point.x
            snap_y = point.y
            # accounts for rotation
            pin_angle = inst_pin.get_angle_normalized() / 1000.0
            if pin_angle == 0:
                wire = design.add_wire(
                    [(snap_x, snap_y), (snap_x + wire_length, snap_y)]
                )
            elif pin_angle == 90:
                wire = design.add_wire(
                    [(snap_x, snap_y), (snap_x, snap_y + wire_length)]
                )
            elif pin_angle == 180:
                wire = design.add_wire(
                    [(snap_x, snap_y), (snap_x - wire_length, snap_y)]
                )
            else:
                wire = design.add_wire(
                    [(snap_x, snap_y), (snap_x, snap_y - wire_length)]
                )
            wire.add_wire_label(netname)


def get_port_count_from_file_extension(snp_path: Union[str, os.PathLike]) -> int:
    """
    Get the number of ports from the SnP file name.

    Notes
    -----
    This will not work for .ts file extensions, which is a valid
    extension for Touchstone 2.0 files. Also, some tools may use a
    generic .snp extension.  That won't work either.
    """
    _, extension = os.path.splitext(snp_path)
    extension = extension[1:]
    port_count = re.findall(r"\d+", extension)
    if port_count:
        return int(port_count[0])
    else:
        raise ValueError("No port number found from the file name")


def get_metadata_from_snp_file(
    filepath: Union[str, os.PathLike],
) -> Tuple[int, List[str]]:
    """
    Return metadata related to port count and port names from an snp file.

    Parameters
    ----------
    filepath : Union[str, os.PathLike]
        The path to the SnP file.

    Returns
    -------
    Tuple[int, List[str]]
        The number of ports and a list of port names.
    """
    # #TODO once pwdatatools bug is resolved in version 0.11.0, add data=False
    # to file reading function call below to enable metadata-only reading
    group = pwdt.read_file_as_group(filepath)
    # reading as a Group and then selecting just the first Block always
    # works, even for Touchstone files with noise parameters
    block = group.get_member_as_block(0)
    s_param_var = block["S"]
    port_count = s_param_var.shape[-1]
    s_param_highest_dim = s_param_var.dims[-1]
    portname_scale = s_param_highest_dim.get_scale("portname")
    if portname_scale is None:
        portname_list = []
    else:
        index = portname_scale.to_pandas_index()
        assert index.inferred_type == "string"
        portname_list = index.tolist()
    return port_count, portname_list


def make_port_names_string_for_snp_instance(portnames: List[str]) -> str:
    """
    Make portnames string for an SnP block's `port_names_list` parameter.

    If no portnames are shown on the SnP instance, the string is "0".
    Otherwise, it is in the following form:
    "1 <length of largest port name> <list of port names in order>
    """
    if not portnames:
        return "0"
    longest_portname = max(portnames, key=len)
    return f"1 {len(longest_portname)} {' '.join(portnames)}"


SNP_FILES = ("Molex2006_1_T_portnames.s4p", "Molex2006_1_T.s4p")
if "__file__" in globals():
    HERE = Path(__file__).parent  # running as a script
else:
    HERE = Path(os.getcwd()).parent  # running in an interactive session
SNP_PATH = HERE / SNP_FILES[0]
WRK_NAME = "test_wrk"
WRK_PATH = HERE / WRK_NAME
LIB_NAME = "test_library"
LIB_PATH = WRK_PATH / LIB_NAME
CELL_NAME = "test_sch"

if WRK_PATH.exists():
    if de.workspace_is_open():
        workspace = de.active_workspace()
    else:
        workspace = de.open_workspace(WRK_PATH)
else:
    workspace = de.create_workspace(WRK_PATH)
    worksapce = de.open_workspace(WRK_PATH)

if LIB_PATH.exists():
    lib = de.Library.open(LIB_NAME, LIB_PATH, de.LibraryMode.SHARED)
else:
    lib = de.create_new_library(LIB_NAME, LIB_PATH)
    workspace.add_library(LIB_NAME, LIB_PATH, de.LibraryMode.SHARED)

if not lib.cell_exists(CELL_NAME):
    design = db_uu.create_schematic(name=(LIB_NAME, CELL_NAME, "schematic"))
    design.save_design()
design = db_uu.open_design(
    name=(LIB_NAME, CELL_NAME, "schematic"), mode=db_uu.DesignMode.WRITE
)
portcount, portnames = get_metadata_from_snp_file(SNP_PATH)
add_snp_instance_to_design(
    design,
    origin=(0, 0),
    name="SnP1",
    filepath=SNP_PATH,
    portcount=portcount,
    pin_names=portnames,
)
add_s_param_instance_to_design(
    design,
    origin=(0, -1),
    name="SP1",
    start=1e6,
    stop=10e9,
    step=100e6,
    freq_units="GHz",
)
add_termg_instances_to_design(design, origin=(-1, -3.5), count=portcount, ncols=2)
for instance in design.instances:
    add_nets_to_instance(instance, wire_length=0.5)
add_measeqn_to_design(
    design,
    ["x=1", "y=1", "z=1e9"],
    origin=(0, -5),
    name="MeasEqn1",
)
design.save_design()
netlist = design.generate_netlist()
ckt_sim = edatoolbox_ads.CircuitSimulator()
output_path = WRK_PATH / "output" / CELL_NAME
output_path.mkdir(parents=True, exist_ok=True)
ckt_sim.run_netlist(netlist, output_dir=str(output_path))
lib.close()
workspace.close()