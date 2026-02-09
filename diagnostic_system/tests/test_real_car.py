"""
Real Car Connection Test

Simple test to verify connection to a real vehicle.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.obd_interface import OBDInterface


def test_real_car():
    """Test connection to real vehicle"""
    print("\n" + "=" * 60)
    print("  REAL VEHICLE CONNECTION TEST")
    print("=" * 60)
    
    print("\nBefore starting:")
    print("  ✓ Adapter plugged into car's OBD-II port")
    print("  ✓ Ignition ON or engine running")
    print("  ✓ config/settings.py updated with correct port")
    
    input("\nPress Enter when ready...")
    
    print("\nAttempting connection...")
    
    interface = OBDInterface()
    
    if interface.connect():
        print("\n✓✓✓ CONNECTION SUCCESSFUL! ✓✓✓")
        print(f"\nVehicle Information:")
        print(f"  Protocol: {interface.connection.protocol_name()}")
        print(f"  Supported Commands: {len(interface.connection.supported_commands)}")
        
        # Try to get basic info
        print("\nTrying to read basic data...")
        
        # Get DTCs
        dtcs = interface.get_dtcs()
        print(f"  DTCs: {len(dtcs)} found")
        if dtcs:
            for code, desc in dtcs:
                print(f"    • {code}: {desc}")
        
        # Get a few basic sensors
        basic_sensors = interface.get_sensor_data(['SPEED', 'RPM', 'COOLANT_TEMP'])
        print(f"\n  Basic Sensors:")
        for sensor, value in basic_sensors.items():
            print(f"    {sensor}: {value}")
        
        interface.disconnect()
        print("\n✓ Test complete - Your system works with real cars!")
        
    else:
        print("\n✗ CONNECTION FAILED")
        print("\nTroubleshooting:")
        print("  1. Check port in settings.py matches Device Manager/system")
        print("  2. Make sure car ignition is ON")
        print("  3. Try unplugging and replugging adapter")
        print("  4. Check adapter LED (should be blinking)")
        print("  5. For Bluetooth: Make sure it's paired properly")


if __name__ == "__main__":
    test_real_car()
