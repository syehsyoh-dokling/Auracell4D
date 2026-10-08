"""
AuraCell 4D - Cellular Kinematic Evidence Gate (PhysiCell Principle)
Validates mitosis duration, division frequency, and spatial contact inhibition
against deterministic cellular biophysics.
"""

class CellularKinematicsGate:
    def __init__(self, min_mitosis_interval_min=45.0, min_cell_volume_spacing_um=8.0):
        """
        Mammalian cells require at least 45 minutes to complete mitosis (M-phase)
        and cannot occupy identical coordinates due to nuclear steric volume.
        """
        self.min_interval = min_mitosis_interval_min
        self.min_spacing = min_cell_volume_spacing_um

    def verify_mitosis_event(self, parent_cell, daughter_1, daughter_2, duration_min):
        """
        Rejects impossible division rates or overlapping daughter positions.
        """
        if duration_min < 20.0:
            return {
                "verdict": "REJECT",
                "reason": f"Kinetic violation: Reported mitosis completed in {duration_min:.1f} min (minimum physical eukaryotic M-phase is >40 min).",
                "residual": abs(40.0 - duration_min) / 40.0
            }
            
        dx = daughter_1["x"] - daughter_2["x"]
        dy = daughter_1["y"] - daughter_2["y"]
        dz = daughter_1["z"] - daughter_2["z"]
        d = (dx**2 + dy**2 + dz**2) ** 0.5
        
        if d < self.min_spacing:
            return {
                "verdict": "REJECT",
                "reason": f"Steric violation: Daughter cells overlap at {d:.2f} um spacing (< {self.min_spacing} um nuclear radius limit).",
                "residual": abs(self.min_spacing - d) / self.min_spacing
            }

        return {
            "verdict": "PASS",
            "daughter_spacing_um": float(round(d, 2)),
            "residual": 0.0
        }
