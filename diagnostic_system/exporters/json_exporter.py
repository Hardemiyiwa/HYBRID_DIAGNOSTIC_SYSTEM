"""
JSON Exporter - Exports diagnostic data to JSON format

This module handles:
- Data formatting for AI team
- JSON serialization
- Pretty printing
- File output
"""

import json
import os
from datetime import datetime


class JSONExporter:
    """
    Exports diagnostic data to JSON format for AI team.
    
    This class combines data from:
    - OBD Interface (connection info)
    - DTC Parser (fault codes)
    - Signal Processor (sensor data and vehicle state)
    
    And creates a complete diagnostic output.
    """
    
    def __init__(self, output_dir="output", pretty_print=True):
        """
        Initialize the JSON Exporter.
        
        Args:
            output_dir: Directory to save output files
            pretty_print: Whether to format JSON nicely (True = readable)
        """
        self.output_dir = output_dir
        self.pretty_print = pretty_print
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def create_diagnostic_output(self, obd_data, parsed_dtcs, processed_sensors):
        """
        Create complete diagnostic output combining all data sources.
        
        Args:
            obd_data: Raw data from OBD Interface (get_all_data())
            parsed_dtcs: List of ParsedDTC objects from DTC Parser
            processed_sensors: Processed data from Signal Processor
        
        Returns:
            dict: Complete diagnostic data structure
        """
        # Get timestamp
        timestamp = datetime.now().isoformat()
        
        # Convert parsed DTCs to dictionaries
        dtcs_list = [dtc.to_dict() for dtc in parsed_dtcs] if parsed_dtcs else []
        
        # Build complete structure
        diagnostic_data = {
            "metadata": {
                "timestamp": timestamp,
                "version": "1.0",
                "system": "Hybrid Vehicle Diagnostic Intelligence System"
            },
            
            "connection": {
                "port": obd_data.get('connection_info', {}).get('port', 'Unknown'),
                "protocol": obd_data.get('connection_info', {}).get('protocol', 'Unknown'),
                "status": obd_data.get('connection_info', {}).get('status', 'Unknown'),
                "supported_commands": obd_data.get('connection_info', {}).get('supported_commands', 0)
            },
            
            "dtcs": {
                "count": len(dtcs_list),
                "codes": dtcs_list,
                "summary": self._create_dtc_summary(parsed_dtcs)
            },
            
            "sensors": processed_sensors.get('sensors', {}),
            
            "vehicle_state": processed_sensors.get('vehicle_state', {}),
            
            "analysis": self._create_analysis(parsed_dtcs, processed_sensors)
        }
        
        return diagnostic_data
    
    def _create_dtc_summary(self, parsed_dtcs):
        """
        Create a summary of DTCs by severity and type.
        
        Args:
            parsed_dtcs: List of ParsedDTC objects
        
        Returns:
            dict: Summary statistics
        """
        if not parsed_dtcs:
            return {
                "total": 0,
                "critical": 0,
                "medium": 0,
                "low": 0,
                "safety_critical": 0,
                "hybrid_related": 0
            }
        
        summary = {
            "total": len(parsed_dtcs),
            "critical": sum(1 for dtc in parsed_dtcs if dtc.severity == "Critical"),
            "medium": sum(1 for dtc in parsed_dtcs if dtc.severity == "Medium"),
            "low": sum(1 for dtc in parsed_dtcs if dtc.severity == "Low"),
            "safety_critical": sum(1 for dtc in parsed_dtcs if dtc.safety_critical),
            "hybrid_related": sum(1 for dtc in parsed_dtcs if dtc.hybrid_related)
        }
        
        return summary
    
    def _create_analysis(self, parsed_dtcs, processed_sensors):
        """
        Create high-level analysis for AI reasoning.
        
        This provides quick insights for the AI team.
        
        Args:
            parsed_dtcs: List of ParsedDTC objects
            processed_sensors: Processed sensor data
        
        Returns:
            dict: Analysis summary
        """
        vehicle_state = processed_sensors.get('vehicle_state', {})
        
        # Determine overall health status
        health_status = "HEALTHY"
        warnings = []
        
        # Check DTCs
        if parsed_dtcs:
            critical_count = sum(1 for dtc in parsed_dtcs if dtc.severity == "Critical")
            safety_critical_count = sum(1 for dtc in parsed_dtcs if dtc.safety_critical)
            
            if safety_critical_count > 0:
                health_status = "CRITICAL"
                warnings.append(f"{safety_critical_count} safety-critical fault(s) detected")
            elif critical_count > 0:
                health_status = "WARNING"
                warnings.append(f"{critical_count} critical fault(s) detected")
            elif len(parsed_dtcs) > 0:
                health_status = "ATTENTION"
                warnings.append(f"{len(parsed_dtcs)} fault code(s) present")
        
        # Check vehicle state
        if vehicle_state.get('engine_overheating', False):
            health_status = "CRITICAL"
            warnings.append("Engine overheating detected")
        
        if vehicle_state.get('engine_high_rpm', False):
            warnings.append("Engine running at high RPM")
        
        # Build analysis
        analysis = {
            "health_status": health_status,
            "warnings": warnings,
            "drivable": health_status != "CRITICAL",
            "immediate_action_required": health_status == "CRITICAL",
            "recommendation": self._get_recommendation(health_status, parsed_dtcs, vehicle_state)
        }
        
        return analysis
    
    def _get_recommendation(self, health_status, parsed_dtcs, vehicle_state):
        """
        Generate recommendation based on diagnostic data.
        
        Args:
            health_status: Overall health status
            parsed_dtcs: List of ParsedDTC objects
            vehicle_state: Vehicle state dictionary
        
        Returns:
            str: Recommendation text
        """
        if health_status == "CRITICAL":
            if vehicle_state.get('engine_overheating', False):
                return "STOP IMMEDIATELY: Engine overheating. Do not continue driving. Seek immediate service."
            
            safety_critical = [dtc for dtc in parsed_dtcs if dtc.safety_critical]
            if safety_critical:
                return f"STOP IMMEDIATELY: Safety-critical fault detected ({safety_critical[0].code}). Do not drive. Contact qualified technician."
            
            return "CRITICAL: Stop driving and seek immediate professional diagnosis."
        
        elif health_status == "WARNING":
            return "Schedule service soon. Critical fault codes detected. Avoid extended driving."
        
        elif health_status == "ATTENTION":
            return "Minor faults detected. Schedule service at your convenience."
        
        else:
            return "Vehicle operating normally. No immediate action required."
    
    def export_to_json(self, diagnostic_data, filename=None):
        """
        Export diagnostic data to JSON file.
        
        Args:
            diagnostic_data: Complete diagnostic dictionary
            filename: Optional custom filename. If None, auto-generates with timestamp
        
        Returns:
            str: Path to saved file
        """
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnostic_{timestamp}.json"
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Full path
        filepath = os.path.join(self.output_dir, filename)
        
        # Write to file
        with open(filepath, 'w') as f:
            if self.pretty_print:
                json.dump(diagnostic_data, f, indent=2)
            else:
                json.dump(diagnostic_data, f)
        
        return filepath
    
    def export_to_string(self, diagnostic_data):
        """
        Export diagnostic data to JSON string.
        
        Useful for sending over network or API.
        
        Args:
            diagnostic_data: Complete diagnostic dictionary
        
        Returns:
            str: JSON string
        """
        if self.pretty_print:
            return json.dumps(diagnostic_data, indent=2)
        else:
            return json.dumps(diagnostic_data)
    
    def validate_structure(self, diagnostic_data):
        """
        Validate that diagnostic data has all required fields.
        
        Args:
            diagnostic_data: Diagnostic dictionary to validate
        
        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ['metadata', 'connection', 'dtcs', 'sensors', 'vehicle_state', 'analysis']
        
        for field in required_fields:
            if field not in diagnostic_data:
                return False, f"Missing required field: {field}"
        
        # Validate metadata
        if 'timestamp' not in diagnostic_data['metadata']:
            return False, "Missing timestamp in metadata"
        
        return True, "Valid"
