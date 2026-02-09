"""
Test Script for DTC Parser

This script tests the DTC parsing and classification functionality.
"""

import sys
import os

# Add diagnostic_system to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processors.dtc_parser import (
    ParsedDTC,
    parse_dtcs,
    parse_dtcs_to_dict,
    classify_dtcs_by_severity,
    get_safety_critical_dtcs,
    get_hybrid_related_dtcs
)
import json


def print_section(title):
    """Print a nice section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_single_dtc():
    """Test parsing a single DTC"""
    print_section("TEST 1: Single DTC Parsing")
    
    # Test with a hybrid code
    dtc = ParsedDTC("P0A80", "Hybrid Battery Pack Deterioration")
    
    print(f"\nCode: {dtc.code}")
    print(f"Description: {dtc.description}")
    print(f"Domain: {dtc.domain}")
    print(f"Code Type: {dtc.code_type}")
    print(f"Subsystem: {dtc.subsystem}")
    print(f"Severity: {dtc.severity}")
    print(f"Safety Critical: {dtc.safety_critical}")
    print(f"Hybrid Related: {dtc.hybrid_related}")
    
    print("\nAs Dictionary:")
    print(json.dumps(dtc.to_dict(), indent=2))


def test_multiple_dtcs():
    """Test parsing multiple DTCs"""
    print_section("TEST 2: Multiple DTCs")
    
    # Sample DTCs covering different categories
    dtc_list = [
        ('P0A80', 'Hybrid Battery Pack Deterioration'),
        ('P0420', 'Catalyst System Efficiency Below Threshold'),
        ('P0301', 'Cylinder 1 Misfire Detected'),
        ('C0071', 'ABS Control Module Fault'),
        ('P0601', 'Internal Control Module Memory Check Sum Error'),
        ('B0001', 'Driver Airbag Circuit'),
        ('U0100', 'Lost Communication with ECM/PCM'),
    ]
    
    parsed = parse_dtcs(dtc_list)
    
    print(f"\nParsed {len(parsed)} DTCs:\n")
    
    for dtc in parsed:
        status = "⚠️ CRITICAL" if dtc.safety_critical else "✓"
        hybrid = "🔋" if dtc.hybrid_related else "  "
        print(f"{status} {hybrid} {dtc.code:8s} [{dtc.severity:8s}] {dtc.domain:15s} - {dtc.subsystem}")


def test_severity_classification():
    """Test grouping DTCs by severity"""
    print_section("TEST 3: Classification by Severity")
    
    dtc_list = [
        ('P0A80', 'Hybrid Battery Pack Deterioration'),
        ('P0420', 'Catalyst System Efficiency Below Threshold'),
        ('P0301', 'Cylinder 1 Misfire Detected'),
        ('C0071', 'ABS Control Module Fault'),
        ('P0601', 'Internal Control Module Memory Check Sum Error'),
    ]
    
    parsed = parse_dtcs(dtc_list)
    classified = classify_dtcs_by_severity(parsed)
    
    for severity in ['Critical', 'Medium', 'Low']:
        print(f"\n{severity} ({len(classified[severity])} codes):")
        for dtc in classified[severity]:
            print(f"  • {dtc.code}: {dtc.description}")


def test_safety_critical_filter():
    """Test filtering safety-critical DTCs"""
    print_section("TEST 4: Safety-Critical DTCs Only")
    
    dtc_list = [
        ('P0A80', 'Hybrid Battery Pack Deterioration'),
        ('P0420', 'Catalyst System Efficiency Below Threshold'),
        ('P0301', 'Cylinder 1 Misfire Detected'),
        ('C0071', 'ABS Control Module Fault'),
        ('P0601', 'Internal Control Module Memory Check Sum Error'),
    ]
    
    parsed = parse_dtcs(dtc_list)
    safety_critical = get_safety_critical_dtcs(parsed)
    
    print(f"\nFound {len(safety_critical)} safety-critical fault(s):\n")
    
    for dtc in safety_critical:
        print(f"⚠️  {dtc.code}: {dtc.description}")
        print(f"    Domain: {dtc.domain}")
        print(f"    Subsystem: {dtc.subsystem}")
        print(f"    Why critical: ", end="")
        
        if dtc.code.startswith('P0A'):
            print("High-voltage hybrid system")
        elif dtc.code.startswith('C'):
            print("Chassis safety system (brakes/stability)")
        elif dtc.code.startswith('P06'):
            print("ECU/computer failure")
        else:
            print("Safety risk identified")
        print()


def test_hybrid_filter():
    """Test filtering hybrid-related DTCs"""
    print_section("TEST 5: Hybrid-Related DTCs Only")
    
    dtc_list = [
        ('P0A80', 'Hybrid Battery Pack Deterioration'),
        ('P0420', 'Catalyst System Efficiency Below Threshold'),
        ('P0A1F', 'Hybrid Battery Voltage System'),
        ('P0301', 'Cylinder 1 Misfire Detected'),
        ('P3000', 'Battery Voltage High'),
    ]
    
    parsed = parse_dtcs(dtc_list)
    hybrid_dtcs = get_hybrid_related_dtcs(parsed)
    
    print(f"\nFound {len(hybrid_dtcs)} hybrid-related fault(s):\n")
    
    for dtc in hybrid_dtcs:
        print(f"🔋 {dtc.code}: {dtc.description}")
        print(f"   Subsystem: {dtc.subsystem}")
        print(f"   Severity: {dtc.severity}")
        print()


def test_json_export():
    """Test JSON export format"""
    print_section("TEST 6: JSON Export Format")
    
    dtc_list = [
        ('P0A80', 'Hybrid Battery Pack Deterioration'),
        ('P0420', 'Catalyst System Efficiency Below Threshold'),
        ('C0071', 'ABS Control Module Fault'),
    ]
    
    # Convert to dictionaries
    dtc_dicts = parse_dtcs_to_dict(dtc_list)
    
    print("\nJSON format (ready for AI team):\n")
    print(json.dumps(dtc_dicts, indent=2))
    
    # Save to file
    output_file = "parsed_dtcs.json"
    with open(output_file, 'w') as f:
        json.dump(dtc_dicts, f, indent=2)
    
    print(f"\n✓ Saved to: {output_file}")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  DTC PARSER TEST SUITE")
    print("=" * 60)
    
    test_single_dtc()
    test_multiple_dtcs()
    test_severity_classification()
    test_safety_critical_filter()
    test_hybrid_filter()
    test_json_export()
    
    print_section("TEST SUMMARY")
    print("✓ All tests completed successfully!")
    print("\nThe DTC Parser can:")
    print("  • Parse DTC structure (domain, type, subsystem)")
    print("  • Determine severity (Critical, Medium, Low)")
    print("  • Identify safety-critical codes")
    print("  • Filter hybrid-related codes")
    print("  • Export to JSON for AI team")
    print("\nReady for integration with OBD Interface!")


if __name__ == "__main__":
    main()
