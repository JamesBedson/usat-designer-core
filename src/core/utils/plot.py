# ===============================================================
# USAT Designer Core - Plot Utilities
# ===============================================================

# Miscellaneous imports
from typing import Dict
from matplotlib.colors import LinearSegmentedColormap

# USAT Designer Common imports
from usat_designer_common.constants.const_data import *
from usat_designer_common.common.plot import plot_scalar_map

# Universal Transcoder imports
from universal_transcoder.calculations.pressure_velocity import pressure_calculation
from universal_transcoder.calculations.energy_intensity import (
    energy_calculation,
    radial_I_calculation,
    transverse_I_calculation,
    angular_error,
    width_angle
)

# ===============================================================

def generate_base64_plots(optimisation_data: dict,
                          return_base_64 = True) -> dict:
    
    S               = optimisation_data[DSN_OUT_SPEAKER_MATRIX]
    cloud           = optimisation_data[DSN_OUT_CLOUD]
    output_layout   = optimisation_data[DSN_OUT_OUTPUT_LAYOUT]
    
    energy          = energy_calculation(S)
    pressure        = pressure_calculation(S)
    radial_i        = radial_I_calculation(cloud, S, output_layout)
    transverse_i    = transverse_I_calculation(cloud, S, output_layout)
    ae              = angular_error(radial_i, transverse_i)
    source_width    = width_angle(radial_i)

    colors = [
    DSN_PLT_GRADIENT_COOL,
    DSN_PLT_GRANDIENT_NEUTRAL,
    DSN_PLT_GRADIENT_WARM
    ]

    cmap = LinearSegmentedColormap.from_list("custom_coolwarm", colors)
    
    # Energy
    energy_base64           = plot_scalar_map(values=energy,
                                              cloud_points=cloud,
                                              title="Energy",
                                              colorbar_label="Energy",
                                              clim_range=(0, 2),
                                              cmap=cmap,
                                              return_base64=return_base_64)
    
    pressure_base64         = plot_scalar_map(values=pressure,
                                              cloud_points=cloud,
                                              title="Pressure",
                                              colorbar_label="Pressure",
                                              clim_range=(0, 2),
                                              cmap=cmap,
                                              return_base64=return_base_64)
    
    # Radial Itensity
    radial_i_base64         = plot_scalar_map(values=radial_i,
                                              cloud_points=cloud,
                                              title="Radial Intensity",
                                              colorbar_label="Radial Intensity",
                                              clim_range=(0,1),
                                              cmap=cmap,
                                              return_base64=return_base_64)
    # Transverse Intensity
    transverse_i_base64     = plot_scalar_map(values=transverse_i,
                                              cloud_points=cloud,
                                              title="Transverse Intensity",
                                              colorbar_label="Transverse Intensity",
                                              clim_range=(0,1),
                                              cmap=cmap,
                                              return_base64=return_base_64)
    # Angular Error
    angular_error_base64    = plot_scalar_map(values=ae,
                                              cloud_points=cloud,
                                              title="Angular Error",
                                              colorbar_label="Angular Error (Degrees)",
                                              clim_range=(0, 45),
                                              cmap=cmap,
                                              return_base64=return_base_64)
    # Apparent Source Width
    source_width_base64     = plot_scalar_map(values=source_width,
                                              cloud_points=cloud,
                                              title="Source Width",
                                              colorbar_label="Source Width (Degrees)",
                                              clim_range=(0, 45),
                                              cmap=cmap,
                                              return_base64=return_base_64)

    plot_data = {
        DSN_PLT_ENERGY: energy_base64,
        DSN_PLT_PRESSURE: pressure_base64,
        DSN_PLT_RADIAL_INTENSITY: radial_i_base64,
        DSN_PLT_TRANSVERSE_INTENSITY: transverse_i_base64,
        DSN_PLT_ANGULAR_ERROR: angular_error_base64,
        DSN_PLT_SOURCE_WIDTH: source_width_base64
    }

    return plot_data