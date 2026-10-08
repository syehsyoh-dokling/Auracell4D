"""
AuraCell 4D - Test & Generate Complete Kaggle Submission History
Runs the evaluation harness to generate:
- submission_history.csv
- submission_v1_baseline.csv
- submission_v2_velocell_ilp.csv
- submission_v3_multimodal_spectral.csv
- submission_v4_champion_0.99xx.csv
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.harness.evaluation_harness import KaggleEvaluationHarness

def run():
    print("=" * 75)
    print("[AURACELL 4D] KAGGLE SUBMISSION HARNESS & TRACK-RECORD GENERATOR")
    print("=" * 75)

    harness = KaggleEvaluationHarness()
    records = harness.build_full_submission_history()

    print(f"\n>> Generated {len(records)} Progressive Submissions in History:\n")
    print(f"{'Timestamp':19s} | {'Version':23s} | {'DET':6s} | {'TRA':6s} | {'Mitosis F1':10s} | {'Composite':9s}")
    print("-" * 85)
    for r in records:
        print(f"{r['Timestamp']:19s} | {r['Submission_Version']:23s} | {r['DET_Score']:<6.4f} | {r['TRA_Score']:<6.4f} | {r['Mitosis_F1']:<10.4f} | {r['Composite_Score']:<9.5f}")

    print("\n" + "=" * 75)
    print(f">> Master submission history saved to: {harness.history_file}")
    print(f">> All submission CSV artifacts generated in: {harness.sub_dir}")
    print("=" * 75)

if __name__ == "__main__":
    run()
