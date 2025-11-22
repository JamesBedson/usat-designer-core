# ===========================================================
# Universal Transcoder - XML Parse Module
# ===========================================================

# Miscellaneous imports
import xml.etree.ElementTree as ET
from numpy import array as npArray

# Universal Transcoder imports
from universal_transcoder.auxiliars.my_coordinates import MyCoordinates

# USAT Designer Common imports
from usat_designer_common.constants.data import *
from usat_designer_common.constants.opt import *
from usat_designer_common.constants.io import *

# USAT Designer Core imports
from utils.enc_dec import (
    create_encoding_matrix,
    get_ambisonics_output,
    get_ambisonics_decoder_matrix
)
# ===========================================================

def create_speaker_layout(speaker_layout_xml: ET.Element) -> MyCoordinates:
    assert(speaker_layout_xml is not None)
    speakers = []
    for speaker in speaker_layout_xml:
        azimuth     = speaker.get(DSN_SPK_AZIMUTH)
        elevation   = speaker.get(DSN_SPK_ELEVATION)
        distance    = speaker.get(DSN_SPK_DISTANCE)
        isLFE       = speaker.get(DSN_SPK_LFE)

        assert(azimuth is not None)
        assert(elevation is not None)
        assert(distance is not None)
        
        is_lfe = float(isLFE) if isLFE is not None else 0.0

        if bool(is_lfe) == False:
            speakers.append((float(azimuth), float(elevation), float(distance)))

    return MyCoordinates.mult_points(npArray(speakers))


def parse_coefficients(coefficients_xml: ET.Element) -> dict[str, float]:
    coefficients = {}
    
    energy_val = coefficients_xml.get(DSN_COEFF_ENERGY)
    assert(energy_val is not None)

    radial_intensity_val = coefficients_xml.get(DSN_COEFF_RADIAL_INTENSITY)
    assert(radial_intensity_val is not None)

    transverse_intensity_val = coefficients_xml.get(DSN_COEFF_TRANSVERSE_INTENSITY)
    assert(transverse_intensity_val is not None)

    pressure_val = coefficients_xml.get(DSN_COEFF_PRESSURE)
    assert(pressure_val is not None)

    radial_velocity_val = coefficients_xml.get(DSN_COEFF_RADIAL_VELOCITY)
    assert(radial_velocity_val is not None)
    
    transverse_velocity_val = coefficients_xml.get(DSN_COEFF_TRANSVERSE_VELOCITY)
    assert(transverse_velocity_val is not None)
    
    in_phase_quadratic_val = coefficients_xml.get(DSN_COEFF_IN_PHASE_QUADRATIC)
    assert(in_phase_quadratic_val is not None)

    symmetry_quadratic_val = coefficients_xml.get(DSN_COEFF_SYMMETRY_QUADRATIC)
    assert(symmetry_quadratic_val is not None)

    in_phase_linear_val = coefficients_xml.get(DSN_COEFF_IN_PHASE_LINEAR)
    assert(in_phase_linear_val is not None)

    symmetry_linear_val = coefficients_xml.get(DSN_COEFF_SYMMETRY_LINEAR)
    assert(symmetry_linear_val is not None)

    total_gains_linear_val = coefficients_xml.get(DSN_COEFF_TOTAL_GAINS_LINEAR)
    assert(total_gains_linear_val is not None)

    total_gains_quadratic_val = coefficients_xml.get(DSN_COEFF_TOTAL_GAINS_QUADRATIC)
    assert(total_gains_quadratic_val is not None)

    coefficients["energy"] = float(energy_val)
    coefficients["radial_intensity"] = float(radial_intensity_val)
    coefficients["transverse_intensity"] = float(transverse_intensity_val)
    coefficients["pressure"] = float(pressure_val)
    coefficients["radial_velocity"] = float(radial_velocity_val)
    coefficients["transverse_velocity"] = float(transverse_velocity_val)
    coefficients["in_phase_quad"] = float(in_phase_quadratic_val)
    coefficients["symmetry_quad"] = float(symmetry_quadratic_val)
    coefficients["in_phase_lin"] = float(in_phase_linear_val)
    coefficients["symmetry_lin"] = float(symmetry_linear_val)
    coefficients["total_gains_lin"] = float(total_gains_linear_val)
    coefficients["total_gains_quad"] = float(total_gains_quadratic_val)

    return coefficients


def parse_encoding_settings(usat_parameter_settings_xml: ET.Element) -> dict:
    
    # Parse encoding settings
    encoding_settings_xml = usat_parameter_settings_xml.find(DSN_XML_SETTINGS)
    assert(encoding_settings_xml is not None)

    parameter_dict = {}

    input_type  = encoding_settings_xml.get(DSN_XML_INPUT_TYPE)
    output_type = encoding_settings_xml.get(DSN_XML_OUTPUT_TYPE)

    assert(input_type is not None)
    assert(output_type is not None)

    #############################################
    # INPUT

    if input_type == DSN_XML_AMBISONICS:
        input_ambisonics_xml = usat_parameter_settings_xml.find(DSN_XML_INPUT_AMBISONICS)
        assert(input_ambisonics_xml is not None)
        
        order = input_ambisonics_xml.get(DSN_XML_AMBISONICS_ORDER_IN)
        assert(order is not None)

        parameter_dict = create_encoding_matrix(format=input_type, 
                                                parameter_dict=parameter_dict, 
                                                layout_data=int(order))

    elif input_type == DSN_XML_SPEAKER_LAYOUT:
        input_speaker_layout_xml = usat_parameter_settings_xml.find(DSN_XML_INPUT_SPEAKER_LAYOUT)
        assert(input_speaker_layout_xml is not None)

        input_speaker_layout = create_speaker_layout(input_speaker_layout_xml)
        
        parameter_dict = create_encoding_matrix(format=input_type,
                                                parameter_dict=parameter_dict,
                                                layout_data=input_speaker_layout)
        
    else:
        raise AssertionError("Not valid format")
    #############################################

    #############################################
    # OUTPUT
    if output_type == DSN_XML_AMBISONICS:
        output_ambisonics_xml = usat_parameter_settings_xml.find(DSN_XML_OUTPUT_AMBISONICS)
        assert(output_ambisonics_xml is not None)

        order = output_ambisonics_xml.get(DSN_XML_AMBISONICS_ORDER_OUT)        
        assert(order is not None)

        parameter_dict[OPT_PD_OUTPUT_LAYOUT] = get_ambisonics_output(int(order))
        parameter_dict[OPT_PD_DSPK]          = get_ambisonics_decoder_matrix(
            int(order), 
            parameter_dict["output_layout"], 
            "pseudo"
            )

    elif output_type == DSN_XML_SPEAKER_LAYOUT:
        output_speaker_layout_xml = usat_parameter_settings_xml.find(DSN_XML_OUTPUT_SPEAKER_LAYOUT)
        
        assert(output_speaker_layout_xml is not None)
        parameter_dict[OPT_PD_OUTPUT_LAYOUT] = create_speaker_layout(output_speaker_layout_xml)

    else:
        raise AssertionError("Not valid format")
    #############################################

    # COEFFICIENTS
    coefficients_xml = usat_parameter_settings_xml.find(DSN_XML_COEFFICIENTS)
    assert(coefficients_xml is not None)
    
    parameter_dict[OPT_PD_COEFFICIENTS]  = parse_coefficients(coefficients_xml)
    parameter_dict[OPT_PD_SHOW_RESULTS]  = False
    parameter_dict[OPT_PD_SAVE_RESULTS]  = False

    return parameter_dict