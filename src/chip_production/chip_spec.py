"""
AuraCell 4D - Physical Organ-on-a-Chip Hardware Specification
Defines the mechanical, fluidic, sensor, and electrical pinout standard for
the CellShells-compatible 'Smart Microfluidic Cartridge'.
"""

class SmartChipSpecification:
    """
    Standard Dual-Channel Microphysiological System (MPS) Geometry:
    Compatible with CellShells Bioscience, Wyss Institute, and Emulate Bio formats.
    """
    def __init__(self):
        # 1. Microchannel Dimensions (SI Units & Micro-scale)
        self.channel_length_mm = 25.0
        self.apical_channel = {
            "name": "Apical Channel (Epithelial/Endothelial Lumen)",
            "width_um": 1000.0,
            "height_um": 100.0,
            "target_cell_type": "Pulmonary Alveolar / Intestinal Caco-2",
            "physiological_flow_rate_ul_min": 10.0,
            "allowable_shear_stress_dyn_cm2": (1.0, 15.0)
        }
        self.basal_channel = {
            "name": "Basal Channel (Vascular Microcapillary Lumen)",
            "width_um": 1000.0,
            "height_um": 100.0,
            "target_cell_type": "Human Umbilical Vein Endothelial Cells (HUVEC)",
            "physiological_flow_rate_ul_min": 10.0,
            "allowable_shear_stress_dyn_cm2": (1.0, 15.0)
        }

        # 2. Porous Flexible PDMS Membrane
        self.membrane = {
            "material": "PDMS (Polydimethylsiloxane, Sylgard 184, 10:1 ratio)",
            "thickness_um": 10.0,
            "pore_diameter_um": 7.0,
            "pore_spacing_um": 30.0,
            "porosity_pct": 12.5,
            "youngs_modulus_mpa": 1.8,
            "max_elastic_deflection_um": 250.0
        }

        # 3. Acoustic Piezo Transducer Hardware Integration (Pinout & Placement)
        self.piezo_sensors = [
            {
                "sensor_id": "PZT-01-INLET",
                "role": "Inlet Bubble Cavitation & Pressure Shock Monitor",
                "location_x_mm": 2.0,
                "frequency_bandwidth_khz": (20.0, 200.0),
                "sampling_rate_ksps": 500.0,
                "interface": "ADC_CHANNEL_0 (0 - 3.3V)"
            },
            {
                "sensor_id": "PZT-02-MID",
                "role": "Membrane Strain & Cardiomyocyte Mechanocardiogram (MCG)",
                "location_x_mm": 12.5,
                "frequency_bandwidth_hz": (0.1, 50.0),
                "sampling_rate_sps": 1000.0,
                "interface": "ADC_CHANNEL_1 (High-Impedance Bio-Amp)"
            },
            {
                "sensor_id": "PZT-03-OUTLET",
                "role": "Clogging Vortex Shedding & Hydraulic Resistance Detector",
                "location_x_mm": 23.0,
                "frequency_bandwidth_khz": (1.0, 10.0),
                "sampling_rate_ksps": 50.0,
                "interface": "ADC_CHANNEL_2 (Bandpass Filtered)"
            }
        ]

        # 4. Optical Inspection Window
        self.optical_window = {
            "glass_coverslip_thickness_um": 170.0,  # Standard #1.5 coverslip
            "working_distance_mm": 0.5,
            "recommended_objective": "20x / 0.8 NA Long Working Distance (LWD)",
            "hyperspectral_bands": 16,
            "spectral_range_nm": (400, 1000)
        }

    def get_hardware_footprint(self):
        """Returns standard ANSI-SLAS microplate compatible footprint."""
        return {
            "standard": "ANSI-SLAS Microplate Footprint Compatible",
            "cartridge_length_mm": 75.0,
            "cartridge_width_mm": 25.0,
            "fluidic_ports": 4,  # Apical In, Apical Out, Basal In, Basal Out
            "vacuum_channels": 2  # Left and right cyclic stretching channels
        }
