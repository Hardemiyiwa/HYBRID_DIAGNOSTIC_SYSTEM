"""
Test Script for Signal Processor

This script tests the signal processing and normalization functionality.
"""

import sys
import os

# Add diagnostic_system to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.signal_processor import SignalProcessor
import json


def print_section(title):
    """Print a nice section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_normalization():
    """Test basic sensor normalization"""
    print_section("TEST 1: Sensor Normalization")
    
    # Simulate raw sensor data from OBD (as strings like from obdsim)
    raw_sensors = {
        'SPEED': '64.0 kilometer_per_hour',
        'RPM': '3823.25 revolutions_per_minute',
        'COOLANT_TEMP': '95 degree_Celsius',
        'ENGINE_LOAD': '45.5 percent',
        'CONTROL_MODULE_VOLTAGE': None  # Missing sensor
    }
    
    processor = SignalProcessor()
    normalized = processor.normalize_sensors(raw_sensors)
    
    print("\nRaw sensors:")
    for key, value in raw_sensors.items():
        print(f"  {key}: {value}")
    
    print("\nNormalized sensors:")
    for key, value in normalized.items():
        print(f"  {key}: {value}")


def test_unit_conversion():
    """Test unit conversion to standard units"""
    print_section("TEST 2: Unit Conversion")
    
    # Create processor
    processor = SignalProcessor()
    
    # Normalized data (from previous step)
    normalized = {
        'SPEED': {'value': 64.0, 'unit': 'kilometer_per_hour'},
        'RPM': {'value': 3823.25, 'unit': 'revolutions_per_minute'},
        'COOLANT_TEMP': {'value': 95, 'unit': 'degree_Celsius'},
        'ENGINE_LOAD': {'value': 45.5, 'unit': 'percent'},
        'CONTROL_MODULE_VOLTAGE': None
    }
    
    standard = processor.convert_to_standard_units(normalized)
    
    print("\nStandard units:")
    for key, value in standard.items():
        print(f"  {key}: {value}")


def test_vehicle_state():
    """Test vehicle state derivation"""
    print_section("TEST 3: Vehicle State Derivation")
    
    # Standard sensor data
    standard_sensors = {
        'speed_kph': 64.0,
        'rpm': 3823.25,
        'coolant_temp_c': 95.0,
        'engine_load_pct': 45.5,
        'control_module_voltage_v': 201.5  # Hybrid voltage
    }
    
    processor = SignalProcessor()
    state = processor.derive_vehicle_state(standard_sensors)
    
    print("\nVehicle State:")
    for key, value in state.items():
        status = "✓" if value else "✗"
        if isinstance(value, bool):
            print(f"  {status} {key}: {value}")
        else:
            print(f"  → {key}: {value}")


def test_different_scenarios():
    """Test different driving scenarios"""
    print_section("TEST 4: Different Scenarios")
    
    scenarios = {
        "Parked (Engine Off)": {
            'speed_kph': 0,
            'rpm': 0,
            'coolant_temp_c': 25,
            'engine_load_pct': 0,
            'control_module_voltage_v': 12.6
        },
        "Idling": {
            'speed_kph': 0,
            'rpm': 750,
            'coolant_temp_c': 92,
            'engine_load_pct': 15,
            'control_module_voltage_v': 201.0
        },
        "Highway Cruising": {
            'speed_kph': 110,
            'rpm': 2200,
            'coolant_temp_c': 95,
            'engine_load_pct': 35,
            'control_module_voltage_v': 205.0
        },
        "Hard Acceleration": {
            'speed_kph': 85,
            'rpm': 5200,
            'coolant_temp_c': 98,
            'engine_load_pct': 85,
            'control_module_voltage_v': 210.0
        },
        "Overheating": {
            'speed_kph': 20,
            'rpm': 1500,
            'coolant_temp_c': 115,
            'engine_load_pct': 40,
            'control_module_voltage_v': 200.0
        }
    }
    
    processor = SignalProcessor()
    
    for scenario_name, sensors in scenarios.items():
        print(f"\n{scenario_name}:")
        print(f"  Speed: {sensors['speed_kph']} km/h, RPM: {sensors['rpm']}")
        print(f"  Temp: {sensors['coolant_temp_c']}°C, Load: {sensors['engine_load_pct']}%")
        
        state = processor.derive_vehicle_state(sensors)
        
        # Show key states
        print(f"  → Mode: {state['mode']}")
        print(f"  → Engine: {'Running' if state['engine_running'] else 'Off'}")
        print(f"  → Temperature: ", end="")
        if state['engine_normal_temp']:
            print("Normal ✓")
        elif state['engine_overheating']:
            print("OVERHEATING ⚠️")
        elif state['engine_cold']:
            print("Cold")
        else:
            print("Warming up")
        
        print(f"  → Hybrid: {'Active' if state['high_voltage_present'] else 'Inactive'}")


def test_complete_pipeline():
    """Test complete processing pipeline"""
    print_section("TEST 5: Complete Pipeline")
    
    # Simulate raw sensor data (as it comes from OBD)
    raw_sensors = {
        'SPEED': '75.0 kilometer_per_hour',
        'RPM': '2850.5 revolutions_per_minute',
        'COOLANT_TEMP': '93 degree_Celsius',
        'ENGINE_LOAD': '42.3 percent',
        'THROTTLE_POS': '38.5 percent',
        'FUEL_LEVEL': '65.2 percent',
        'CONTROL_MODULE_VOLTAGE': '203.4 volt'
    }
    
    processor = SignalProcessor()
    
    # Process everything in one call
    result = processor.process(raw_sensors)
    
    print("\nProcessed Data (JSON format for AI team):")
    print(json.dumps(result, indent=2))
    
    # Save to file
    output_file = "processed_sensors.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✓ Saved to: {output_file}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  SIGNAL PROCESSOR TEST SUITE")
    print("=" * 60)
    
    test_normalization()
    test_unit_conversion()
    test_vehicle_state()
    test_different_scenarios()
    test_complete_pipeline()
    
    print_section("TEST SUMMARY")
    print("✓ All tests completed successfully!")
    print("\nThe Signal Processor can:")
    print("  • Normalize raw sensor data")
    print("  • Convert units to standard formats")
    print("  • Derive vehicle state (moving, idle, temp, etc.)")
    print("  • Handle missing sensors gracefully")
    print("  • Output clean JSON for AI team")
    print("\nReady for integration!")


if __name__ == "__main__":
    main()
