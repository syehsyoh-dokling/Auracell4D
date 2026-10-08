"""
AuraCell 4D - End-to-End Architecture Verification Test
Tests all layers: Acoustic, 4D Vision, 16-Band Spectral, and Multi-Physics Evidence Gating.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.utils.synthetic_data import (
    generate_synthetic_acoustic_stream,
    generate_synthetic_4d_cells,
    generate_synthetic_hyperspectral_cube
)
from src.acoustic.processor import AcousticProcessor
from src.vision_4d.mitosis_ilp import MitosisILPSolver
from src.spectral.redox_classifier import HyperspectralRedoxClassifier
from src.evidence_gate.gate_orchestrator import MasterEvidenceGate
from src.agent.dossier_generator import RegulatoryDossierGenerator

def run_test():
    print("=" * 65)
    print("[START] AURACELL 4D: END-TO-END PIPELINE VERIFICATION TEST")
    print("=" * 65)

    # 1. Acoustic Micro-Sensing Test
    print("\n[Layer 1A] Testing Acoustic Engine (AURASENSAI Core)...")
    acoustic_data = generate_synthetic_acoustic_stream(duration_sec=2.0, num_events=3)
    processor = AcousticProcessor(sample_rate=acoustic_data["sample_rate"])
    detected_audio_events = processor.detect_transient_events(acoustic_data["signal"])
    print(f"  -> Audio Duration: 2.0s | Detected Transients: {len(detected_audio_events)}")
    for ev in detected_audio_events:
        print(f"     * Transient @ {ev['timestamp_sec']}s (SNR: {ev['snr_db']} dB)")

    # 2. 4D Volumetric Vision & Mitosis Test
    print("\n[Layer 1B] Testing 4D Volumetric Vision (Velocell Core)...")
    cell_timepoints = generate_synthetic_4d_cells(num_initial_cells=6, num_timepoints=5)
    tracker = MitosisILPSolver(max_distance=15.0)
    lineage_results = tracker.track_lineage(cell_timepoints)
    print(f"  -> Tracked Timepoints: {len(cell_timepoints)} | Mitosis Events: {lineage_results['total_mitosis_events']}")
    for m in lineage_results["detected_divisions"]:
        print(f"     * Mitosis: Cell {m['parent_id']} -> Daughters ({m['daughter_1_id']}, {m['daughter_2_id']}) [Conf: {m['mitosis_confidence']}]")

    # 3. Hyperspectral Viability & Redox Ratio Test
    print("\n[Layer 1C] Testing 16-Band Hyperspectral Classifier (SpectrumaX Core)...")
    hyper_cube = generate_synthetic_hyperspectral_cube(height=32, width=32, num_bands=16)
    classifier = HyperspectralRedoxClassifier()
    viability_report = classifier.classify_viability(hyper_cube)
    print(f"  -> Mean Optical Redox Ratio (ORR): {viability_report['mean_orr']}")
    print(f"  -> Viable Fraction: {viability_report['viable_fraction'] * 100:.1f}% | Status: {viability_report['status']}")

    # 4. The Multi-Physics Evidence Gate Test (SeismoForge Paradigm)
    print("\n[Layer 2 & 3] Testing Multi-Physics Evidence Gate...")
    gate = MasterEvidenceGate()

    # Test Case A: Physically Valid Mitosis
    valid_claim = {
        "claim_type": "mitosis_division",
        "parent": {"x": 50.0, "y": 50.0, "z": 20.0},
        "daughter_1": {"x": 55.0, "y": 50.0, "z": 20.0},
        "daughter_2": {"x": 45.0, "y": 50.0, "z": 20.0},
        "duration_min": 60.0
    }
    cert_valid = gate.certify_claim(valid_claim)
    print(f"  -> Valid Mitosis Claim: {cert_valid['verdict']} (Spacing: {cert_valid.get('daughter_spacing_um')} um)")

    # Test Case B: Unphysical Mitosis (Hallucinated 5-minute division)
    hallucinated_claim = {
        "claim_type": "mitosis_division",
        "parent": {"x": 50.0, "y": 50.0, "z": 20.0},
        "daughter_1": {"x": 50.5, "y": 50.0, "z": 20.0},
        "daughter_2": {"x": 50.0, "y": 50.0, "z": 20.0},
        "duration_min": 5.0  # Impossible for mammalian cells!
    }
    cert_hallucinated = gate.certify_claim(hallucinated_claim)
    print(f"  -> Hallucinated Mitosis Claim: {cert_hallucinated['verdict']} (Reason: {cert_hallucinated['reason']})")

    # 5. Regulatory Dossier Generation
    print("\n[Layer 4] Generating FDA-Ready Regulatory Dossier (Verity Engine)...")
    dossier_gen = RegulatoryDossierGenerator()
    dossier = dossier_gen.generate_dossier(
        certified_events=[cert_valid],
        spectral_summary=viability_report,
        acoustic_summary=detected_audio_events
    )
    print(f"  -> Regulatory Framework: {dossier['regulatory_framework']}")
    print(f"  -> Evidence-Gating Status: {dossier['evidence_gating_status']}")
    print(f"  -> Total Certified Citations: {len(dossier['scientific_citations'])}")

    print("\n" + "=" * 65)
    print("[OK] Smoke test on SYNTHETIC data finished without exceptions (no performance claim).")
    print("=" * 65)

if __name__ == "__main__":
    run_test()
