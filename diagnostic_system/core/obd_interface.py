"""
OBD Interface - Connects to vehicle and retrieves diagnostic data

This module handles:
- Connection to OBD-II adapter
- DTC retrieval
- Sensor data collection
- Connection management
"""

import sys
import os
import logging

# Add diagnostic_system to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import obd  # python-OBD library (installed via pip)
from datetime import datetime

# Import our modules
try:
    from config import settings
except ImportError:
    # Fallback if running from different location
    import importlib.util
    spec = importlib.util.spec_from_file_location("settings", os.path.join(parent_dir, "config", "settings.py"))
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

# Simple logger setup (inline to avoid import issues)
def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


class OBDInterface:
    """
    Interface for connecting to vehicle and retrieving diagnostic data.
    
    This class handles all communication with the OBD-II adapter.
    It can work with both real vehicles and obdsim for testing.
    """
    
    def __init__(self, port=None, baudrate=None, protocol=None, timeout=None):
        """
        Initialize the OBD interface.
        
        Args:
            port: Serial port (e.g., 'COM3' or '/dev/pts/2'). 
                  If None, uses settings.OBD_PORT
            baudrate: Connection speed. If None, auto-detects
            protocol: OBD protocol. If None, auto-detects
            timeout: Connection timeout in seconds
        """
        # Set up logger
        self.logger = setup_logger(__name__)
        
        # Store connection parameters (use settings as defaults)
        self.port = port or settings.OBD_PORT
        self.baudrate = baudrate or settings.OBD_BAUDRATE
        self.protocol = protocol or settings.OBD_PROTOCOL
        self.timeout = timeout or settings.OBD_TIMEOUT
        
        # Connection object (will be created when we connect)
        self.connection = None
        
        # Track connection status
        self.is_connected = False
        
        self.logger.info("OBD Interface initialized")
        self.logger.info(f"Port: {self.port}")
        self.logger.info(f"Timeout: {self.timeout}s")
    
    def connect(self):
        """
        Connect to the OBD-II adapter.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        self.logger.info("Attempting to connect to vehicle...")
        
        try:
            # Create OBD connection
            # portstr: which port to use
            # baudrate, protocol: let python-OBD auto-detect if None
            # fast: whether to skip initialization checks
            # timeout: how long to wait for responses
            
            self.connection = obd.OBD(
                portstr=self.port,
                baudrate=self.baudrate,
                protocol=self.protocol,
                fast=settings.OBD_FAST,
                timeout=self.timeout
            )
            
            # Check if connection was successful
            if self.connection.status() == obd.OBDStatus.CAR_CONNECTED:
                self.is_connected = True
                self.logger.info("✓ Successfully connected to vehicle")
                self.logger.info(f"Protocol: {self.connection.protocol_name()}")
                self.logger.info(f"Supported commands: {len(self.connection.supported_commands)}")
                return True
            else:
                self.is_connected = False
                self.logger.error(f"✗ Connection failed. Status: {self.connection.status()}")
                return False
                
        except Exception as e:
            self.is_connected = False
            self.logger.error(f"✗ Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """
        Disconnect from the OBD-II adapter.
        
        Always call this when you're done to properly close the connection.
        """
        if self.connection:
            try:
                self.connection.close()
                self.is_connected = False
                self.logger.info("Disconnected from vehicle")
            except Exception as e:
                self.logger.error(f"Error during disconnect: {str(e)}")
        else:
            self.logger.warning("No active connection to disconnect")
    
    def get_dtcs(self):
        """
        Retrieve Diagnostic Trouble Codes (DTCs) from the vehicle.
        
        DTCs are fault codes that indicate problems with the vehicle.
        
        Returns:
            list: List of tuples (code, description)
                  Example: [('P0420', 'Catalyst System Efficiency Below Threshold')]
                  Returns empty list if no codes or connection failed
        """
        if not self.is_connected:
            self.logger.error("Not connected to vehicle. Call connect() first.")
            return []
        
        try:
            self.logger.info("Retrieving DTCs...")
            
            # Query the vehicle for DTCs
            response = self.connection.query(obd.commands.GET_DTC)
            
            # Check if we got a valid response
            if response.is_null():
                self.logger.warning("No DTC data available")
                return []
            
            # response.value is a list of (code, description) tuples
            dtcs = response.value
            
            if dtcs:
                self.logger.info(f"Found {len(dtcs)} DTC(s)")
                for code, desc in dtcs:
                    self.logger.info(f"  - {code}: {desc}")
            else:
                self.logger.info("No DTCs found (vehicle is clear)")
            
            return dtcs
            
        except Exception as e:
            self.logger.error(f"Error retrieving DTCs: {str(e)}")
            return []
    
    def get_sensor_data(self, sensor_list=None):
        """
        Retrieve sensor data from the vehicle.
        
        Args:
            sensor_list: List of sensor names to query (e.g., ['SPEED', 'RPM'])
                        If None, uses sensors from settings.SENSOR_PIDS
        
        Returns:
            dict: Dictionary of sensor readings
                  Example: {'SPEED': 65, 'RPM': 2500, 'COOLANT_TEMP': 85}
                  Sensors that fail return None
        """
        if not self.is_connected:
            self.logger.error("Not connected to vehicle. Call connect() first.")
            return {}
        
        # Use provided sensor list or default from settings
        sensors_to_query = sensor_list or settings.SENSOR_PIDS
        
        sensor_data = {}
        
        self.logger.info(f"Collecting data from {len(sensors_to_query)} sensor(s)...")
        
        for sensor_name in sensors_to_query:
            try:
                # Get the OBD command for this sensor
                # obd.commands is a dictionary: obd.commands['SPEED'], obd.commands['RPM'], etc.
                if hasattr(obd.commands, sensor_name):
                    command = getattr(obd.commands, sensor_name)
                else:
                    self.logger.warning(f"Unknown sensor: {sensor_name}")
                    sensor_data[sensor_name] = None
                    continue
                
                # Query the sensor
                response = self.connection.query(command)
                
                # Check if we got valid data
                if response.is_null():
                    self.logger.debug(f"{sensor_name}: No data available")
                    sensor_data[sensor_name] = None
                else:
                    # Extract the value
                    # response.value includes units (e.g., "65 kph")
                    # We'll store the full value for now
                    sensor_data[sensor_name] = response.value
                    self.logger.debug(f"{sensor_name}: {response.value}")
                    
            except Exception as e:
                self.logger.warning(f"Error reading {sensor_name}: {str(e)}")
                sensor_data[sensor_name] = None
        
        # Count successful readings
        successful = sum(1 for v in sensor_data.values() if v is not None)
        self.logger.info(f"Successfully collected {successful}/{len(sensors_to_query)} sensor readings")
        
        return sensor_data
    
    def get_all_data(self):
        """
        Retrieve all diagnostic data (DTCs + sensors) in one call.
        
        This is a convenience method that combines get_dtcs() and get_sensor_data().
        
        Returns:
            dict: Complete diagnostic data
                  {
                      'timestamp': '2026-02-04T15:30:00',
                      'dtcs': [('P0420', 'Catalyst problem')],
                      'sensors': {'SPEED': 65, 'RPM': 2500, ...},
                      'connection_info': {
                          'port': 'COM3',
                          'protocol': 'ISO 15765-4 CAN',
                          'status': 'connected'
                      }
                  }
        """
        if not self.is_connected:
            self.logger.error("Not connected to vehicle. Call connect() first.")
            return None
        
        self.logger.info("Collecting complete diagnostic data...")
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Collect DTCs
        dtcs = self.get_dtcs()
        
        # Collect sensor data
        sensors = self.get_sensor_data()
        
        # Build complete data structure
        data = {
            'timestamp': timestamp,
            'dtcs': dtcs,
            'sensors': sensors,
            'connection_info': {
                'port': self.port,
                'protocol': self.connection.protocol_name() if self.connection else 'Unknown',
                'status': 'connected' if self.is_connected else 'disconnected',
                'supported_commands': len(self.connection.supported_commands) if self.connection else 0
            }
        }
        
        self.logger.info("Data collection complete")
        
        return data
