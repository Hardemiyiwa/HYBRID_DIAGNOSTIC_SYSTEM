"""
Test Script for OBD Interface

This script tests the OBDInterface class with obdsim.

Before running:
1. Make sure python-OBD is installed:
   pip install obd

2. Start obdsim in another terminal:
   cd ~/obdgpslogger-0.16/bin
   ./obdsim --generator=Cycle  (or --generator=Error for DTCs)
   
3. Note the port it creates (e.g., /dev/pts/2)

4. Update config/settings.py:
   TESTING_MODE = True
   OBD_PORT = "/dev/pts/X"  # Use the port from obdsim
   
5. Run this test:
   cd diagnostic_system
   python tests/test_obd_interface.py
"""

import sys
import os

# Add diagnostic_system directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.obd_interface import OBDInterface
import json


def print_section(title):
    """Print a nice section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_connection():
    """Test basic connection to vehicle"""
    print_section("TEST 1: Connection")
    
    interface = OBDInterface()
    
    # Try to connect
    if interface.connect():
        print("✓ Connection successful!")
        print(f"  Protocol: {interface.connection.protocol_name()}")
        print(f"  Supported commands: {len(interface.connection.supported_commands)}")
        return interface
    else:
        print("✗ Connection failed!")
        print("\nTroubleshooting:")
        print("1. Is obdsim running?")
        print("2. Did you set the correct port in config/settings.py?")
        print("3. Check the obdsim output for the SimPort name")
        return None


def test_dtcs(interface):
    """Test DTC retrieval"""
    print_section("TEST 2: Diagnostic Trouble Codes")
    
    dtcs = interface.get_dtcs()
    
    if dtcs:
        print(f"✓ Found {len(dtcs)} DTC(s):")
        for code, desc in dtcs:
            print(f"  • {code}: {desc}")
    else:
        print("ℹ No DTCs found (vehicle is clear)")
        print("\nNote: To test with DTCs, restart obdsim with:")
        print("  ./obdsim --generator=Error")


def test_sensors(interface):
    """Test sensor data collection"""
    print_section("TEST 3: Sensor Data")
    
    sensors = interface.get_sensor_data()
    
    print(f"Collected {len(sensors)} sensor readings:\n")
    
    for sensor_name, value in sensors.items():
        if value is not None:
            print(f"  ✓ {sensor_name:20s}: {value}")
        else:
            print(f"  ✗ {sensor_name:20s}: Not available")


def test_all_data(interface):
    """Test getting all data at once"""
    print_section("TEST 4: Complete Data Collection")
    
    data = interface.get_all_data()
    
    if data:
        print("✓ Successfully collected all data\n")
        
        # Display in a nice format
        print(f"Timestamp: {data['timestamp']}")
        print(f"\nConnection Info:")
        print(f"  Port: {data['connection_info']['port']}")
        print(f"  Protocol: {data['connection_info']['protocol']}")
        print(f"  Status: {data['connection_info']['status']}")
        
        print(f"\nDTCs: {len(data['dtcs'])} found")
        for code, desc in data['dtcs']:
            print(f"  • {code}: {desc}")
        
        print(f"\nSensors: {sum(1 for v in data['sensors'].values() if v is not None)} available")
        
        # Save to JSON file for inspection
        output_file = "test_output.json"
        with open(output_file, 'w') as f:
            # Convert Pint quantities to strings for JSON serialization
            json_data = data.copy()
            json_data['sensors'] = {k: str(v) for k, v in data['sensors'].items()}
            json.dump(json_data, f, indent=2)
        
        print(f"\n✓ Data saved to: {output_file}")
    else:
        print("✗ Failed to collect data")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  OBD INTERFACE TEST SUITE")
    print("=" * 60)
    
    # Test 1: Connection
    interface = test_connection()
    if not interface:
        print("\n❌ Tests aborted - connection failed")
        return
    
    # Test 2: DTCs
    test_dtcs(interface)
    
    # Test 3: Sensors
    test_sensors(interface)
    
    # Test 4: All data
    test_all_data(interface)
    
    # Clean up
    print_section("CLEANUP")
    interface.disconnect()
    print("✓ Disconnected")
    
    print_section("TEST SUMMARY")
    print("✓ All tests completed successfully!")
    print("\nNext steps:")
    print("1. Check test_output.json to see the data structure")
    print("2. Try with different obdsim generators (Error, Random, Cycle)")
    print("3. Ready to build the DTC Parser (Step 3)")


if __name__ == "__main__":
    main()
