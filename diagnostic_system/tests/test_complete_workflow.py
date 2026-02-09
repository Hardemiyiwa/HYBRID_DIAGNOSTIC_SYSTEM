"""
Complete Integration Test

This test demonstrates the complete diagnostic workflow:
1. Connect to vehicle (OBD Interface)
2. Get DTCs and sensors
3. Parse DTCs (DTC Parser)
4. Process sensors (Signal Processor)
5. Export complete diagnostic (JSON Exporter)

This shows how all components work together!
"""

import sys
import os

# Add diagnostic_system to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.obd_interface import OBDInterface
from processors.dtc_parser import parse_dtcs
from processors.signal_processor import SignalProcessor
from exporters.json_exporter import JSONExporter
import json


def print_section(title):
    """Print a nice section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_complete_workflow():
    """
    Test the complete diagnostic workflow end-to-end.
    
    This simulates what your main application will do.
    """
    print("\n" + "=" * 70)
    print("  COMPLETE DIAGNOSTIC WORKFLOW")
    print("  (Integration Test - All Components)")
    print("=" * 70)
    
    # ========================================================================
    # STEP 1: Connect to Vehicle
    # ========================================================================
    print_section("STEP 1: Connect to Vehicle (OBD Interface)")
    
    interface = OBDInterface()
    
    if not interface.connect():
        print("✗ Failed to connect to vehicle")
        print("\nMake sure:")
        print("  1. obdsim is running")
        print("  2. Port is correct in config/settings.py")
        return
    
    print("✓ Connected successfully")
    print(f"  Protocol: {interface.connection.protocol_name()}")
    
    # ========================================================================
    # STEP 2: Collect Raw Data
    # ========================================================================
    print_section("STEP 2: Collect Data from Vehicle")
    
    obd_data = interface.get_all_data()
    
    print(f"✓ DTCs: {len(obd_data['dtcs'])} found")
    print(f"✓ Sensors: {sum(1 for v in obd_data['sensors'].values() if v is not None)} collected")
    
    # ========================================================================
    # STEP 3: Parse DTCs
    # ========================================================================
    print_section("STEP 3: Parse and Classify DTCs")
    
    parsed_dtcs = parse_dtcs(obd_data['dtcs'])
    
    if parsed_dtcs:
        print(f"\nFound {len(parsed_dtcs)} fault code(s):\n")
        for dtc in parsed_dtcs:
            status = "⚠️ CRITICAL" if dtc.safety_critical else "  "
            hybrid = "🔋" if dtc.hybrid_related else "  "
            print(f"{status} {hybrid} {dtc.code}: {dtc.description}")
            print(f"      Domain: {dtc.domain}, Severity: {dtc.severity}")
    else:
        print("✓ No fault codes detected")
    
    # ========================================================================
    # STEP 4: Process Sensors
    # ========================================================================
    print_section("STEP 4: Process Sensor Data")
    
    processor = SignalProcessor()
    processed = processor.process(obd_data['sensors'])
    
    print("\nNormalized Sensors:")
    for key, value in list(processed['sensors'].items())[:5]:  # Show first 5
        if value is not None:
            print(f"  {key}: {value}")
    
    print("\nVehicle State:")
    print(f"  → Mode: {processed['vehicle_state']['mode']}")
    print(f"  → Engine: {'Running' if processed['vehicle_state']['engine_running'] else 'Off'}")
    print(f"  → Moving: {'Yes' if processed['vehicle_state']['vehicle_moving'] else 'No'}")
    print(f"  → Hybrid: {'Active' if processed['vehicle_state']['high_voltage_present'] else 'Inactive'}")
    
    # ========================================================================
    # STEP 5: Create Complete Diagnostic Output
    # ========================================================================
    print_section("STEP 5: Generate Complete Diagnostic Output")
    
    exporter = JSONExporter()
    
    diagnostic_output = exporter.create_diagnostic_output(
        obd_data=obd_data,
        parsed_dtcs=parsed_dtcs,
        processed_sensors=processed
    )
    
    # Validate structure
    is_valid, message = exporter.validate_structure(diagnostic_output)
    
    if is_valid:
        print("✓ Diagnostic output structure valid")
    else:
        print(f"✗ Validation failed: {message}")
        return
    
    # Show analysis
    analysis = diagnostic_output['analysis']
    print(f"\nHealth Status: {analysis['health_status']}")
    
    if analysis['warnings']:
        print("\nWarnings:")
        for warning in analysis['warnings']:
            print(f"  ⚠️  {warning}")
    
    print(f"\nRecommendation:")
    print(f"  {analysis['recommendation']}")
    
    # ========================================================================
    # STEP 6: Export to File
    # ========================================================================
    print_section("STEP 6: Export to JSON File")
    
    filepath = exporter.export_to_json(diagnostic_output)
    print(f"✓ Saved to: {filepath}")
    
    # Also save a pretty-printed version for viewing
    with open("complete_diagnostic.json", 'w') as f:
        json.dump(diagnostic_output, f, indent=2)
    
    print("✓ Human-readable version: complete_diagnostic.json")
    
    # ========================================================================
    # STEP 7: Show Final Structure
    # ========================================================================
    print_section("STEP 7: Final Diagnostic Structure")
    
    print("\nTop-level fields:")
    for key in diagnostic_output.keys():
        print(f"  • {key}")
    
    print(f"\nDTC Summary:")
    summary = diagnostic_output['dtcs']['summary']
    print(f"  Total: {summary['total']}")
    print(f"  Critical: {summary['critical']}")
    print(f"  Safety-Critical: {summary['safety_critical']}")
    print(f"  Hybrid-Related: {summary['hybrid_related']}")
    
    print(f"\nSensor Count: {len(diagnostic_output['sensors'])}")
    print(f"Vehicle State Flags: {len(diagnostic_output['vehicle_state'])}")
    
    # ========================================================================
    # Cleanup
    # ========================================================================
    interface.disconnect()
    
    print_section("WORKFLOW COMPLETE")
    print("✓ All components working together successfully!")
    print("\nYour diagnostic system is ready for:")
    print("  • Real vehicle testing")
    print("  • AI team integration")
    print("  • Production deployment")
    print("\nOutput files created:")
    print(f"  • {filepath}")
    print("  • complete_diagnostic.json")


def main():
    """Run the complete workflow test"""
    test_complete_workflow()


if __name__ == "__main__":
    main()
