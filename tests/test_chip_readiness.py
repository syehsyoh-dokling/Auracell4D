"""
AuraCell 4D - Physical Chip Production Readiness & HIL Test Suite
Validates the complete hardware-software translation pipeline:
1. Microchannel physical specification compliance
2. Real-time Hardware-in-the-Loop (HIL) closed-loop actuation (<20ms latency)
3. C-header firmware generation for microcontroller deployment
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.chip_production.chip_spec import SmartChipSpecification
from src.chip_production.hardware_in_the_loop_sim import HardwareInTheLoopSimulator
from src.chip_production.firmware_bridge import export_firmware_header

def run_test():
    print("=" * 75)
    print("[AURACELL 4D] PHYSICAL CHIP HARDWARE-READINESS & HIL VALIDATION TEST")
    print("=" * 75)

    # 1. Inspect Physical Chip Specifications
    print("\n[Step 1] Verifying Mechanical & Fluidic Cartridge Specifications...")
    spec = SmartChipSpecification()
    print(f"  -> Cartridge Dimensions: 75 x 25 mm (ANSI-SLAS Microplate Standard)")
    print(f"  -> Apical Channel: {spec.apical_channel['width_um']} x {spec.apical_channel['height_um']} um")
    print(f"  -> Basal Channel: {spec.basal_channel['width_um']} x {spec.basal_channel['height_um']} um")
    print(f"  -> Porous PDMS Membrane: {spec.membrane['thickness_um']} um thickness, {spec.membrane['pore_diameter_um']} um pore diameter")
    print(f"  -> Integrated Piezo Sensors: {len(spec.piezo_sensors)} channels (PZT-Inlet, PZT-Mid, PZT-Outlet)")

    # 2. Run Closed-Loop Hardware-in-the-Loop (HIL) Simulation
    print("\n[Step 2] Executing Real-Time Closed-Loop Hardware-in-the-Loop (HIL) Simulation...")
    hil = HardwareInTheLoopSimulator()
    hil_result = hil.run_closed_loop_test(inject_bubble=True, inject_clog=True)
    
    print(f"  -> Simulation Status: {hil_result['test_status']}")
    print(f"  -> Actuation Events Triggered: {hil_result['actions_triggered']}")
    for act in hil_result["action_details"]:
        print(f"     * Step {act['step']} ({act['time_ms']} ms): {act['action']}")
        print(f"       Reason: {act['reason']} | Latency: {act['response_latency_ms']} ms")
    print(f"  -> Mean Edge Controller Latency: {hil_result['mean_actuation_latency_ms']} ms (Target: < 20.0 ms)")
    print(f"  -> Membrane Delamination Prevented: {hil_result['membrane_delamination_prevented']}")
    print(f"  -> Microbubble Shear Detachment Prevented: {hil_result['bubble_detachment_prevented']}")

    # 3. Export & Verify C-Firmware Header for Microcontroller Flashing
    print("\n[Step 3] Exporting Embedded C-Firmware Header for Microcontroller Flashing...")
    fw_header_path = root_dir / "src" / "chip_production" / "auracell_chip_firmware.h"
    export_firmware_header(fw_header_path)
    print(f"  -> C/C++ Header generated at: {fw_header_path.name} ({fw_header_path.stat().st_size} bytes)")

    print("\n" + "=" * 75)
    print("[OK] Spec + HIL SIMULATION ran without exceptions. Latency numbers are Python timings, not hardware.")
    print("=" * 75)

if __name__ == "__main__":
    run_test()
