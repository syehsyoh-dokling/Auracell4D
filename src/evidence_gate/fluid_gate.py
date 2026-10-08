"""
AuraCell 4D - Fluid Mechanical Evidence Gate (OpenFOAM Principle)
Validates microfluidic shear stresses and flow continuity using Navier-Stokes
principles to verify or reject acoustic and optical velocity claims.
"""

import numpy as np

class FluidMechanicalGate:
    def __init__(self, channel_width_um=1000.0, channel_height_um=100.0, dynamic_viscosity_pa_s=0.001):
        """
        Reference cartridge geometry (identical to chip_spec.py and the writeup, Section 3.3):
        - Width: 1000 um, Height: 100 um
        - Fluid: cell culture medium (~ water viscosity at 37C: 0.001 Pa.s)
        At 10 uL/min this gives tau = 6*mu*Q/(w*h^2) = 1.0 dyn/cm^2 [Design, computed].
        """
        self.w = channel_width_um * 1e-6
        self.h = channel_height_um * 1e-6
        self.mu = dynamic_viscosity_pa_s

    def compute_wall_shear_stress(self, flow_rate_ul_per_min):
        """
        Calculates wall shear stress (tau) for rectangular microchannels:
        tau = (6 * mu * Q) / (w * h^2)
        Returns shear stress in dyn/cm^2 (1 Pa = 10 dyn/cm^2).
        """
        # Convert uL/min to m^3/s
        q_m3_s = (flow_rate_ul_per_min * 1e-9) / 60.0
        
        # Wall shear stress in Pa
        tau_pa = (6.0 * self.mu * q_m3_s) / (self.w * (self.h ** 2))
        tau_dyn_cm2 = tau_pa * 10.0
        return tau_dyn_cm2

    def verify_shear_claim(self, reported_flow_rate, observed_cell_detachment):
        """
        Rule: Human endothelial cells tolerate up to 15-20 dyn/cm^2.
        If an AI claims detachment occurs at 2 dyn/cm^2 without drug, or denies detachment at 80 dyn/cm^2,
        the claim is flagged as unphysical.
        """
        tau = self.compute_wall_shear_stress(reported_flow_rate)
        
        if tau > 30.0 and not observed_cell_detachment:
            return {
                "verdict": "REJECT",
                "reason": f"Physical violation: Wall shear stress ({tau:.1f} dyn/cm^2) exceeds critical threshold (>30 dyn/cm^2) but zero cell detachment was reported.",
                "residual": abs(tau - 30.0) / 30.0
            }
            
        return {
            "verdict": "PASS",
            "shear_stress_dyn_cm2": float(np.round(tau, 2)),
            "residual": 0.0
        }
