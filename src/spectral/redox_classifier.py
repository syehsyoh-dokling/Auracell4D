"""
AuraCell 4D - Hyperspectral Viability Classifier (SpectrumaX Core)
Computes label-free Optical Redox Ratio (ORR = FAD / (NADH + FAD)) from 16-band
snapshot cubes to discriminate viable from apoptotic/necrotic cells without toxic stains.
"""

import numpy as np

class HyperspectralRedoxClassifier:
    def __init__(self, nadh_band_idx=2, fad_band_idx=6):
        """
        Default band mappings in the 16-band snapshot nanocube:
        - Band 2: NADH emission channel (~450 nm)
        - Band 6: FAD emission channel (~525 nm)
        """
        self.nadh_idx = nadh_band_idx
        self.fad_idx = fad_band_idx

    def compute_optical_redox_ratio(self, hyper_cube):
        """
        Calculates ORR map = FAD / (NADH + FAD + eps).
        - High NADH / Low FAD -> Low ORR (0.15 - 0.35) -> Highly viable, active glycolysis.
        - Low NADH / High FAD -> High ORR (>0.60) -> Oxidative stress, apoptosis/toxicity.
        """
        nadh = hyper_cube[:, :, self.nadh_idx]
        fad = hyper_cube[:, :, self.fad_idx]
        
        orr_map = fad / (nadh + fad + 1e-7)
        return orr_map

    def classify_viability(self, hyper_cube, viability_threshold=0.55):
        """Classifies pixels/clusters into Viable vs Apoptotic."""
        orr_map = self.compute_optical_redox_ratio(hyper_cube)
        viable_mask = orr_map < viability_threshold
        apoptotic_mask = orr_map >= viability_threshold
        
        viable_fraction = float(np.mean(viable_mask))
        apoptotic_fraction = float(np.mean(apoptotic_mask))
        
        return {
            "mean_orr": float(np.round(np.mean(orr_map), 4)),
            "viable_fraction": float(np.round(viable_fraction, 4)),
            "apoptotic_fraction": float(np.round(apoptotic_fraction, 4)),
            "status": "Healthy / Viable" if viable_fraction > 0.70 else "Cellular Toxicity Detected"
        }
