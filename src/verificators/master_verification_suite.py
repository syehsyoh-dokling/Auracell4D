"""
AuraCell 4D - Master Ground-Truth Verification Suite
Executes 15 benchmark validation cases across all 5 core themes:
1. Acoustic & Micro-Pressure Multi-Frequency (3 cases)
2. Fluid Dynamics & CFD Navier-Stokes (3 cases)
3. Biomechanical & OpenSees/FEBio Nonlinear Mechanics (3 cases)
4. Cellular Kinematics & Mitosis CTC (3 cases)
5. 16-Band Hyperspectral & Redox SpectrumaX (3 cases)
"""

import sys
import json
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from src.verificators.acoustic_verificator import AcousticGTVerificator
from src.verificators.fluid_cfd_verificator import FluidCFDGTVerificator
from src.verificators.opensees_biomech_verificator import OpenSeesBiomechGTVerificator
from src.verificators.cellular_kinematics_verificator import CellularKinematicsGTVerificator
from src.verificators.spectral_redox_verificator import SpectralRedoxGTVerificator

def run_all_benchmarks():
    print("=" * 80)
    print("[AURACELL 4D] MULTI-PHYSICS MASTER GROUND-TRUTH VERIFICATION SUITE")
    print("=" * 80)
    print("15 internal consistency checks (formula vs reference constant) across 5 physical/bio themes.")
    print("NOTE: these are unit tests of the solvers, NOT validations against literature data.\n")

    results = []

    # THEME 1: Acoustic Multi-Frequency
    print(">>> THEME 1: ACOUSTIC & INFRASOUND/ULTRASOUND MULTI-FREQUENCY VERIFICATOR")
    ac_ver = AcousticGTVerificator()
    r1 = ac_ver.case_1_rayleigh_plesset_bubble_resonance(bubble_radius_um=30.0)
    r2 = ac_ver.case_2_cardiomyocyte_infrasound_beating(beat_rate_bpm=72.0)
    r3 = ac_ver.case_3_shear_induced_acoustic_whistle(channel_width_um=100.0, flow_rate_ul_min=20.0)
    for r in [r1, r2, r3]:
        print(f"  [{r['status']}] {r['case_id']} - {r['name']}")
        print(f"         Regime: {r.get('auditory_regime', 'N/A')}")
        print(f"         Residual Error: {r['residual_error'] * 100:.3f}%\n")
        results.append(r)

    # THEME 2: Fluid Dynamics & CFD
    print(">>> THEME 2: FLUID DYNAMICS & CFD NAVIER-STOKES VERIFICATOR")
    fl_ver = FluidCFDGTVerificator()
    r4 = fl_ver.case_1_endothelial_wall_shear_stress(flow_rate_ul_min=10.0, width_um=1000.0, height_um=100.0)
    r5 = fl_ver.case_2_pressure_drop_channel_clogging(channel_len_mm=20.0, width_um=100.0, height_um=50.0)
    r6 = fl_ver.case_3_womersley_pulsatile_number(height_um=100.0, pulse_freq_hz=1.2)
    for r in [r4, r5, r6]:
        print(f"  [{r['status']}] {r['case_id']} - {r['name']}")
        print(f"         Residual Error: {r['residual_error'] * 100:.3f}%\n")
        results.append(r)

    # THEME 3: Biomechanical & Structural Nonlinear Mechanics
    print(">>> THEME 3: BIOMECHANICAL & OPENSEES/FEBIO STRUCTURAL VERIFICATOR")
    bm_ver = OpenSeesBiomechGTVerificator()
    r7 = bm_ver.case_1_pdms_membrane_deflection(pressure_kpa=10.0, membrane_span_um=1000.0)
    r8 = bm_ver.case_2_hertzian_cell_indentation(indentation_nm=500.0, tip_radius_nm=2000.0)
    r9 = bm_ver.case_3_hydrogel_ecm_shear_modulus(e_kpa=10.0, poisson=0.49)
    for r in [r7, r8, r9]:
        print(f"  [{r['status']}] {r['case_id']} - {r['name']}")
        print(f"         Residual Error: {r['residual_error'] * 100:.3f}%\n")
        results.append(r)

    # THEME 4: Cellular Kinematics & Mitosis
    print(">>> THEME 4: CELLULAR KINEMATICS & MITOSIS CTC VERIFICATOR")
    ck_ver = CellularKinematicsGTVerificator()
    r10 = ck_ver.case_1_eukaryotic_mitosis_kinetics(measured_m_phase_min=52.0, daughter_separation_dist_um=12.0)
    r11 = ck_ver.case_2_oxygen_diffusion_limit_spheroid(d_o2_m2_s=2.0e-9, c0_mol_m3=0.20)
    r12 = ck_ver.case_3_contact_inhibition_packing_density(cell_diameter_um=20.0, measured_cells_per_mm2=2150.0)
    for r in [r10, r11, r12]:
        print(f"  [{r['status']}] {r['case_id']} - {r['name']}")
        print(f"         Residual Error: {r['residual_error'] * 100:.3f}%\n")
        results.append(r)

    # THEME 5: 16-Band Hyperspectral & Redox
    print(">>> THEME 5: 16-BAND HYPERSPECTRAL & METABOLIC REDOX VERIFICATOR")
    sp_ver = SpectralRedoxGTVerificator()
    r13 = sp_ver.case_1_optical_redox_ratio_toxicity(nadh_intensity=0.72, fad_intensity=0.34)
    r14 = sp_ver.case_2_lipid_droplet_nir_absorption(absorption_930nm=0.48, reference_850nm=0.12)
    r15 = sp_ver.case_3_hemoglobin_oxygen_saturation(a_577nm=0.85, a_542nm=0.72)
    for r in [r13, r14, r15]:
        print(f"  [{r['status']}] {r['case_id']} - {r['name']}")
        print(f"         Residual Error: {r['residual_error'] * 100:.3f}%\n")
        results.append(r)

    # Summary Statistics
    total = len(results)
    passed = len([r for r in results if r['status'] == 'PASS'])
    max_residual = max(r['residual_error'] for r in results)

    print("=" * 80)
    print(f"SUMMARY: {passed}/{total} internal consistency checks passed")
    print(f"MAXIMUM RESIDUAL vs reference constant: {max_residual * 100:.4f}% (reference constants are self-defined)")
    print("STATUS: internal consistency checks complete (no performance claim implied)")
    print("=" * 80)

    # Export report JSON to benchmarks folder
    benchmarks_dir = root_dir / "benchmarks"
    benchmarks_dir.mkdir(parents=True, exist_ok=True)
    report_file = benchmarks_dir / "ground_truth_verification_results.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f">> Exported calibration results to: {report_file}")

    return results

if __name__ == "__main__":
    run_all_benchmarks()
