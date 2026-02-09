"""
Signal Processor - Processes and normalizes sensor data

This module handles:
- Sensor data normalization
- Vehicle state derivation
- Unit conversions
- Data validation
"""


class SignalProcessor:
    """
    Processes raw OBD sensor data into normalized, usable format.
    
    This class:
    - Extracts numeric values from Pint quantities
    - Converts units to standard formats
    - Handles missing/None values
    - Derives vehicle state from sensor readings
    """
    
    def __init__(self):
        """Initialize the signal processor"""
        pass
    
    def normalize_sensors(self, raw_sensors):
        """
        Normalize raw sensor data from OBD interface.
        
        Converts Pint quantities (e.g., "64.0 kilometer_per_hour") 
        to clean numeric values.
        
        Args:
            raw_sensors: Dictionary of sensor readings from OBD interface
                        Example: {'SPEED': <Quantity(64.0, 'kph')>, ...}
        
        Returns:
            dict: Normalized sensor data with numeric values
        """
        normalized = {}
        
        for sensor_name, value in raw_sensors.items():
            # Handle None values
            if value is None:
                normalized[sensor_name] = None
                continue
            
            # Handle string "None"
            if str(value) == "None":
                normalized[sensor_name] = None
                continue
            
            # Extract numeric value and unit from Pint quantity
            try:
                # Convert to string to parse
                value_str = str(value)
                
                # Split into number and unit
                # Example: "64.0 kilometer_per_hour" -> ["64.0", "kilometer_per_hour"]
                parts = value_str.split(maxsplit=1)
                
                if len(parts) > 0:
                    numeric_value = float(parts[0])
                    unit = parts[1] if len(parts) > 1 else ""
                    
                    # Store both value and unit
                    normalized[sensor_name] = {
                        'value': numeric_value,
                        'unit': unit
                    }
                else:
                    normalized[sensor_name] = None
                    
            except (ValueError, AttributeError):
                # If conversion fails, store as None
                normalized[sensor_name] = None
        
        return normalized
    
    def convert_to_standard_units(self, normalized_sensors):
        """
        Convert sensor values to standard units.
        
        Standard units:
        - Speed: km/h
        - Temperature: Celsius
        - Pressure: kPa
        - Voltage: Volts
        - Percentage: %
        
        Args:
            normalized_sensors: Dictionary from normalize_sensors()
        
        Returns:
            dict: Sensors in standard units with clean keys
        """
        standard = {}
        
        for sensor_name, sensor_data in normalized_sensors.items():
            if sensor_data is None:
                # Keep None values as-is
                standard_key = self._get_standard_key(sensor_name)
                standard[standard_key] = None
                continue
            
            value = sensor_data['value']
            unit = sensor_data.get('unit', '')
            
            # Convert based on sensor type
            if sensor_name == 'SPEED':
                # Speed: ensure km/h
                if 'mile' in unit.lower():
                    value = value * 1.60934  # mph to km/h
                standard['speed_kph'] = round(value, 2)
            
            elif sensor_name == 'RPM':
                standard['rpm'] = round(value, 2)
            
            elif 'TEMP' in sensor_name:
                # Temperature: ensure Celsius
                if 'fahrenheit' in unit.lower():
                    value = (value - 32) * 5/9
                temp_key = sensor_name.lower().replace('_temp', '_temp_c')
                standard[temp_key] = round(value, 1)
            
            elif 'PRESSURE' in sensor_name:
                # Pressure: ensure kPa
                if 'psi' in unit.lower():
                    value = value * 6.89476  # psi to kPa
                pressure_key = sensor_name.lower() + '_kpa'
                standard[pressure_key] = round(value, 1)
            
            elif 'VOLTAGE' in sensor_name:
                voltage_key = sensor_name.lower() + '_v'
                standard[voltage_key] = round(value, 2)
            
            elif 'LOAD' in sensor_name or 'LEVEL' in sensor_name or 'POS' in sensor_name:
                # Percentages
                percent_key = sensor_name.lower() + '_pct'
                standard[percent_key] = round(value, 1)
            
            else:
                # Default: just clean the key name
                clean_key = sensor_name.lower()
                standard[clean_key] = round(value, 2)
        
        return standard
    
    def _get_standard_key(self, sensor_name):
        """Get standardized key name for a sensor"""
        key_map = {
            'SPEED': 'speed_kph',
            'RPM': 'rpm',
            'COOLANT_TEMP': 'coolant_temp_c',
            'ENGINE_LOAD': 'engine_load_pct',
            'THROTTLE_POS': 'throttle_pos_pct',
            'FUEL_LEVEL': 'fuel_level_pct',
            'FUEL_PRESSURE': 'fuel_pressure_kpa',
            'CONTROL_MODULE_VOLTAGE': 'control_module_voltage_v',
        }
        
        return key_map.get(sensor_name, sensor_name.lower())
    
    def derive_vehicle_state(self, standard_sensors):
        """
        Derive high-level vehicle state from sensor readings.
        
        This creates a semantic understanding of what the vehicle is doing.
        
        Args:
            standard_sensors: Dictionary from convert_to_standard_units()
        
        Returns:
            dict: Vehicle state information
        """
        state = {}
        
        # Get sensor values (with safe defaults)
        speed = standard_sensors.get('speed_kph', 0) or 0
        rpm = standard_sensors.get('rpm', 0) or 0
        engine_load = standard_sensors.get('engine_load_pct', 0) or 0
        coolant_temp = standard_sensors.get('coolant_temp_c', 0) or 0
        voltage = standard_sensors.get('control_module_voltage_v', 0) or 0
        
        # Basic movement states
        state['vehicle_moving'] = speed > 5  # Moving if > 5 km/h
        state['vehicle_stopped'] = speed < 1  # Stopped if < 1 km/h
        
        # Engine states
        state['engine_running'] = rpm > 300  # Engine on if RPM > 300
        state['engine_off'] = rpm < 100  # Engine off if RPM < 100
        state['engine_idle'] = 500 < rpm < 1000 and speed < 5  # Idling
        state['engine_high_rpm'] = rpm > 4000  # High RPM
        
        # Temperature states
        state['engine_cold'] = coolant_temp < 60  # Cold if < 60°C
        state['engine_warm'] = 60 <= coolant_temp < 90  # Warming up
        state['engine_normal_temp'] = 90 <= coolant_temp <= 110  # Normal operating
        state['engine_overheating'] = coolant_temp > 110  # Overheating if > 110°C
        
        # Load states
        state['low_load'] = engine_load < 30
        state['moderate_load'] = 30 <= engine_load < 70
        state['high_load'] = engine_load >= 70
        
        # Hybrid-specific states (if voltage data available)
        if voltage > 0:
            state['high_voltage_present'] = voltage > 100  # Hybrid battery active
            state['low_voltage_system'] = voltage < 20  # 12V system only
        else:
            state['high_voltage_present'] = False
            state['low_voltage_system'] = True
        
        # Driving modes (inferred)
        if state['vehicle_stopped'] and state['engine_running']:
            state['mode'] = 'idle'
        elif state['vehicle_moving'] and state['low_load']:
            state['mode'] = 'cruising'
        elif state['vehicle_moving'] and state['high_load']:
            state['mode'] = 'accelerating'
        elif speed < 1 and rpm < 100:
            state['mode'] = 'off'
        else:
            state['mode'] = 'normal'
        
        return state
    
    def process(self, raw_sensors):
        """
        Process raw sensor data through complete pipeline.
        
        This is the main method to call. It:
        1. Normalizes raw sensor data
        2. Converts to standard units
        3. Derives vehicle state
        
        Args:
            raw_sensors: Raw sensor dictionary from OBD interface
        
        Returns:
            dict: Complete processed data
                  {
                      'sensors': {...},  # Normalized sensor values
                      'vehicle_state': {...}  # Derived state
                  }
        """
        # Step 1: Normalize (extract numbers from Pint quantities)
        normalized = self.normalize_sensors(raw_sensors)
        
        # Step 2: Convert to standard units
        standard = self.convert_to_standard_units(normalized)
        
        # Step 3: Derive vehicle state
        state = self.derive_vehicle_state(standard)
        
        # Return complete processed data
        return {
            'sensors': standard,
            'vehicle_state': state
        }
