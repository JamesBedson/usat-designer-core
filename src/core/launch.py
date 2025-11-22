# ===========================================================
# USAT Designer Core Entry Point
# ===========================================================

# Miscellaneous imports
import xml.etree.ElementTree as ET
import gc
import sys
import threading
import matplotlib

# USAT Designer Common imports
from usat_designer_common.constants.opt import *
from usat_designer_common.constants.data import *
from usat_designer_common.common.optimize import optimize_for_usat_designer

# USAT Designer Core imports
from utils.parse import parse_encoding_settings
from utils.plot import generate_base64_plots

# ===========================================================

def threaded_plot_worker(optimisation_data, output_container):
    plots = generate_base64_plots(optimisation_data, return_base_64=True)
    output_container.update(plots)


def start_decoding(xml_string: str,
                   progress_callback=None,
                   status_callback=None) -> tuple:
    
    matplotlib.use("Agg")

    total_steps = 4
    
    if progress_callback:
        progress_callback(1.0 / total_steps)
    
    if status_callback:
        status_callback("Processing USAT parameters")

    usat_state_parameters_xml   = ET.fromstring(xml_string)
    optimization_dict           = parse_encoding_settings(usat_state_parameters_xml)

    optimization_dict[OPT_PD_SHOW_RESULTS]       = False
    optimization_dict[OPT_PD_SAVE_RESULTS]       = False
    optimization_dict[OPT_PD_RESULTS_FILE_NAME]  = None
    
    if progress_callback:
        progress_callback(2.0 / total_steps)

    if status_callback:
        status_callback("Optimizing")
    optimisation_data   = optimize_for_usat_designer(optimization_dict)
    T_optimised         = optimisation_data[DSN_OUT_TRANSCODING_MATRIX].T.tolist()

    if progress_callback:
        progress_callback(3.0 / total_steps)

    if status_callback:
        status_callback("Generating Plots")

    plot_data_container = {}
    plot_thread = threading.Thread(target=threaded_plot_worker, args=(optimisation_data, plot_data_container))
    plot_thread.start()
    plot_thread.join()
    
    if progress_callback:
        progress_callback(4.0 / total_steps)

    if status_callback:
        status_callback("Finishing")

    energy_base_64                  = plot_data_container[DSN_PLT_ENERGY]
    pressure_base_64                = plot_data_container[DSN_PLT_PRESSURE]
    radial_intensity_base_64        = plot_data_container[DSN_PLT_RADIAL_INTENSITY]
    transverse_intensity_base_64    = plot_data_container[DSN_PLT_TRANSVERSE_INTENSITY]
    angular_error_base_64           = plot_data_container[DSN_PLT_ANGULAR_ERROR]
    source_width_base_64            = plot_data_container[DSN_PLT_SOURCE_WIDTH]
    
    return (
        T_optimised,
        energy_base_64,
        pressure_base_64,
        radial_intensity_base_64,
        transverse_intensity_base_64,
        angular_error_base_64,
        source_width_base_64
    )


#################################################################################
def main():

    if len(sys.argv) != 2:
        print("Usage: python script.py <your_argument>")

    else:
        gain_matrix = start_decoding(sys.argv[1])

    return gain_matrix
#################################################################################

if __name__ == "__main__":
    main()
    sys.modules.clear()
    gc.collect()