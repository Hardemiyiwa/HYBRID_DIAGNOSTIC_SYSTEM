"""
Configuration settings for Diagnostic System

This file contains all configuration parameters:
- OBD connection settings
- Timeout values
- Port configuration
- Feature flags
"""

import platform

# Testing mode
TESTING_MODE = True # True = obdsim testing, False = real vehicle

# OBD-II Connection settings

if TESTING_MODE:
    # OBDSIM SETTINGS
    OBD_PORT = "/dev/pts/1"
    OBD_BAUDRATE = None
    OBD_PROTOCOL = None
    OBD_TIMEOUT = 5
    OBD_FAST = False

else:
    # REAL VEHICLE SETTINGS
    # Detect operating system and set appropriate defaults
    system = platform.system()

    if system == "Windows":
        OBD_PORT = "COM3"
        
    elif system == "Linux":
        # Linux - USB adapter
        OBD_PORT = "/dev/ttyUSB0"

    elif system == "Darwin":
        # macOS
        OBD_PORT = "/dev/tty.usbserial"

    else:
        OBD_PORT = None # will attempt auto-detection

    # Real vehicle connection settings
    OBD_BAUDRATE = None
    OBD_PROTOCOL = None
    OBD_TIMEOUT = 30
    OBD_FAST = False

# Data Collection Settings
COLLECT_DTCS = True
COLLECT_FREEZE_FRAME = True
COLLECT_SENSORS = True

# Sensor PIDs to Collect
SENSOR_PIDS = [
    # Basic engine parameters
    'SPEED',
    'RPM',
    'ENGINE_LOAD',
    'COOLANT_TEMP',
    'THROTTLE_POS',

    # Fuel system
    'FUEL_LEVEL',
    'FUEL_PRESSURE',

    # Hybrid-specific (may not be available on all vehicles)
    'HYBRID_BATTERY_REMAINING',
    'CONTROL_MODULE_VOLTAGE',

    # Add more as needed for specific vehicle
]

# Hybrid Vehicle Speceific Settings
HYBRID_MODE = True

# Export Settings
EXPORT_FORMAT = "json"
EXPORT_PRETTY = True
EXPORT_DIRECTORY = "output"
EXPORT_TIMESTAMP = True

# Logging Settings
LOG_LEVEL = "INFO"
LOG_TO_FILE = True
LOG_FILE = "diagnostic.log"
LOG_TO_CONSOLE = True

# Safety and Error Handling
RETRY_ON_ERROR = True
MAX_RETRIES = 3
GRACEFUL_DEGRADATION = True