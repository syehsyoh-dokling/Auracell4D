"""
AuraCell 4D - Embedded Firmware & Microcontroller Bridge
Generates C/C++ header files and hardware register definitions for
direct flashing onto onboard microcontrollers (ARM Cortex-M4/M7, ESP32-S3, STM32).
"""

C_HEADER_TEMPLATE = """/**
 * ============================================================================
 * @file    auracell_chip_firmware.h
 * @brief   AuraCell 4D - On-Chip Hardware-Firmware Interface Definitions
 * @target  ARM Cortex-M4/M7, STM32H7, ESP32-S3 (CellShells Bio-Cartridge Interface)
 * @author  Saifuddin & AuraCell 4D Team
 * ============================================================================
 */

#ifndef AURACELL_CHIP_FIRMWARE_H
#define AURACELL_CHIP_FIRMWARE_H

#include <stdint.h>
#include <stdbool.h>

/* --- SENSOR PINOUTS & ADC CHANNELS --- */
#define PIN_PZT_INLET_ADC         0   /* Fast ADC: Cavitation burst detection (500 kSps) */
#define PIN_PZT_MID_BIOAMP        1   /* Bio-Amp ADC: Cardiomyocyte MCG (1 kSps) */
#define PIN_PZT_OUTLET_ADC        2   /* Bandpass ADC: Clogging whistle (50 kSps) */

/* --- ACTUATOR OUTPUT CHANNELS --- */
#define PIN_VALVE_BYPASS_PWM      12  /* High-speed piezo micro-valve */
#define PIN_PUMP_FLOW_CONTROL     14  /* Perfusion pump PWM / DAC flow throttle */

/* --- BIOPHYSICAL SAFETY THRESHOLDS --- */
#define CAVITATION_BURST_FREQ_HZ  108000.0f  /* 108 kHz Minnaert bubble resonance */
#define MAX_ALLOWABLE_SHEAR_DYN   15.0f      /* Endothelial safety limit: 15 dyn/cm^2 */
#define CRITICAL_PRESSURE_DROP_PA 500.0f     /* Anti-delamination pressure ceiling */
#define ACTUATION_DEADLINE_MS     20.0f      /* Real-time loop deadline */

/* --- SYSTEM TELEMETRY PACKET STRUCT --- */
typedef struct __attribute__((packed)) {
    uint32_t timestamp_ms;
    float    flow_rate_ul_min;
    float    wall_shear_stress_dyn;
    float    inlet_peak_khz;
    float    pressure_drop_pa;
    uint8_t  valve_state;       /* 0: NORMAL, 1: BYPASS_VENTING */
    uint8_t  alarm_flags;       /* Bit 0: Cavitation, Bit 1: Clog, Bit 2: Arrhythmia */
} AuraCell_Telemetry_t;

/* --- EXPORTED FIRMWARE FUNCTIONS --- */
void AuraCell_InitHardware(void);
void AuraCell_ProcessAcousticFrame(const int16_t* pzt_samples, uint16_t len);
void AuraCell_EmergencyThrottlePump(float safe_flow_rate_ul_min);
void AuraCell_ActuateVentingValve(bool open_valve);

#endif /* AURACELL_CHIP_FIRMWARE_H */
"""

def export_firmware_header(target_path):
    with open(target_path, "w") as f:
        f.write(C_HEADER_TEMPLATE)
    return target_path
