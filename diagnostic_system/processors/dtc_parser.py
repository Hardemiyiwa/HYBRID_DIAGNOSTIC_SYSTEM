"""
DTC Parser - Parses and classifies diagnostic trouble codes

This module handles:
- DTC structure parsing (P0XXX, C0XXX, etc.)
- Domain classification (Powertrain, Chassis, Body, Network)
- Severity determination
- Subsystem identification
"""


class ParsedDTC:
    """
    Represents a parsed Diagnostic Trouble Code with all its metadata.
    
    Attributes:
        code: The DTC code (e.g., 'P0420')
        description: Human-readable description
        domain: Powertrain, Chassis, Body, or Network
        code_type: Generic or Manufacturer-specific
        severity: Low, Medium, or Critical
        subsystem: Affected subsystem (e.g., 'Catalyst', 'Hybrid Battery')
        safety_critical: Whether this is a safety-critical fault
        hybrid_related: Whether this affects hybrid systems
    """
    
    def __init__(self, code, description=""):
        """
        Initialize a ParsedDTC object.
        
        Args:
            code: DTC code string (e.g., 'P0420')
            description: Optional description from vehicle
        """
        self.code = code.upper()  # Ensure uppercase
        self.description = description
        
        # Parse the code structure
        self.domain = self._parse_domain()
        self.code_type = self._parse_type()
        self.subsystem = self._identify_subsystem()
        
        # Determine severity and safety criticality
        self.severity = self._determine_severity()
        self.safety_critical = self._is_safety_critical()
        self.hybrid_related = self._is_hybrid_related()
    
    def _parse_domain(self):
        """
        Parse the domain from the first character.
        
        Returns:
            str: Domain name
        """
        if not self.code:
            return "Unknown"
        
        domain_map = {
            'P': 'Powertrain',
            'C': 'Chassis',
            'B': 'Body',
            'U': 'Network'
        }
        
        first_char = self.code[0]
        return domain_map.get(first_char, 'Unknown')
    
    def _parse_type(self):
        """
        Parse the code type from the second character.
        
        Returns:
            str: 'Generic' or 'Manufacturer-specific'
        """
        if len(self.code) < 2:
            return "Unknown"
        
        second_char = self.code[1]
        
        if second_char in ['0', '2']:
            return "Generic (SAE)"
        elif second_char in ['1', '3']:
            return "Manufacturer-specific"
        else:
            return "Unknown"
    
    def _identify_subsystem(self):
        """
        Identify the affected subsystem based on code patterns.
        
        This uses code ranges to classify subsystems.
        
        Returns:
            str: Subsystem name
        """
        # For Powertrain codes (P)
        if self.code.startswith('P'):
            code_num = self.code[1:]  # Get everything after 'P'
            
            # Hybrid-specific codes (P0Axx, P1Axx, P3xxx in some cases)
            if code_num.startswith('0A') or code_num.startswith('1A'):
                return "Hybrid/Electric System"
            
            # Engine codes
            if code_num.startswith('01') or code_num.startswith('02'):
                return "Fuel/Air Metering and Auxiliary Emissions"
            
            if code_num.startswith('03'):
                return "Ignition System"
            
            if code_num.startswith('04'):
                return "Emissions Control"
            
            if code_num.startswith('05') or code_num.startswith('06'):
                return "Vehicle Speed & Idle Control"
            
            if code_num.startswith('07') or code_num.startswith('08'):
                return "Transmission"
            
            # Default for powertrain
            return "Powertrain (General)"
        
        # For Chassis codes (C)
        elif self.code.startswith('C'):
            return "Chassis System"
        
        # For Body codes (B)
        elif self.code.startswith('B'):
            return "Body System"
        
        # For Network codes (U)
        elif self.code.startswith('U'):
            return "Network Communication"
        
        return "Unknown"
    
    def _determine_severity(self):
        """
        Determine severity level of the fault.
        
        Severity levels:
        - Low: Minor issue, vehicle drivable
        - Medium: Significant issue, should be addressed soon
        - Critical: Safety risk or major system failure
        
        Returns:
            str: Severity level
        """
        code = self.code
        
        # Critical severity codes
        critical_patterns = [
            'P0A',  # Hybrid system faults
            'P06',  # Computer/output circuit
            'C0',   # Chassis (brakes, stability control)
        ]
        
        # Specific critical codes
        critical_codes = [
            'P0601',  # ECU Memory error
            'P0602',  # ECU Programming error
            'P0606',  # ECU Processor fault
        ]
        
        # Check if it's critical
        if code in critical_codes:
            return "Critical"
        
        for pattern in critical_patterns:
            if code.startswith(pattern):
                return "Critical"
        
        # Medium severity - emissions, transmission
        medium_patterns = [
            'P04',  # Emissions
            'P07',  # Transmission
            'P08',  # Transmission
        ]
        
        for pattern in medium_patterns:
            if code.startswith(pattern):
                return "Medium"
        
        # Default to low for others
        return "Low"
    
    def _is_safety_critical(self):
        """
        Determine if this code represents a safety-critical fault.
        
        Safety-critical faults require immediate attention and may
        make the vehicle unsafe to drive.
        
        Returns:
            bool: True if safety-critical
        """
        # Hybrid high-voltage system faults are safety-critical
        if self.code.startswith('P0A'):
            return True
        
        # Chassis codes (brakes, stability) are safety-critical
        if self.code.startswith('C'):
            return True
        
        # Specific safety-critical codes
        safety_codes = [
            'P0601', 'P0602', 'P0606',  # ECU faults
            'P0562',  # System voltage low
        ]
        
        if self.code in safety_codes:
            return True
        
        return False
    
    def _is_hybrid_related(self):
        """
        Determine if this code is related to hybrid systems.
        
        Returns:
            bool: True if hybrid-related
        """
        # P0Axx codes are hybrid/electric
        if self.code.startswith('P0A') or self.code.startswith('P1A'):
            return True
        
        # Specific hybrid-related codes
        hybrid_codes = [
            'P3000',  # Battery voltage high
            'P3001',  # Battery voltage low
        ]
        
        if self.code in hybrid_codes:
            return True
        
        return False
    
    def to_dict(self):
        """
        Convert the parsed DTC to a dictionary.
        
        This is useful for JSON export.
        
        Returns:
            dict: Dictionary representation of the DTC
        """
        return {
            'code': self.code,
            'description': self.description,
            'domain': self.domain,
            'code_type': self.code_type,
            'subsystem': self.subsystem,
            'severity': self.severity,
            'safety_critical': self.safety_critical,
            'hybrid_related': self.hybrid_related
        }
    
    def __str__(self):
        """String representation of the DTC"""
        return f"{self.code}: {self.description} [{self.severity}]"
    
    def __repr__(self):
        """Developer representation"""
        return f"ParsedDTC(code='{self.code}', severity='{self.severity}', domain='{self.domain}')"


def parse_dtcs(dtc_list):
    """
    Parse a list of DTCs from the vehicle.
    
    This is the main function your code will call to process DTCs.
    
    Args:
        dtc_list: List of (code, description) tuples from OBD interface
                  Example: [('P0420', 'Catalyst System Efficiency Below Threshold')]
    
    Returns:
        list: List of ParsedDTC objects
    """
    parsed_dtcs = []
    
    for code, description in dtc_list:
        parsed_dtc = ParsedDTC(code, description)
        parsed_dtcs.append(parsed_dtc)
    
    return parsed_dtcs


def parse_dtcs_to_dict(dtc_list):
    """
    Parse DTCs and return as a list of dictionaries.
    
    This is convenient for JSON export.
    
    Args:
        dtc_list: List of (code, description) tuples
    
    Returns:
        list: List of dictionaries
    """
    parsed_dtcs = parse_dtcs(dtc_list)
    return [dtc.to_dict() for dtc in parsed_dtcs]


def classify_dtcs_by_severity(parsed_dtcs):
    """
    Group DTCs by severity level.
    
    Args:
        parsed_dtcs: List of ParsedDTC objects
    
    Returns:
        dict: DTCs grouped by severity
              {'Critical': [...], 'Medium': [...], 'Low': [...]}
    """
    classified = {
        'Critical': [],
        'Medium': [],
        'Low': []
    }
    
    for dtc in parsed_dtcs:
        classified[dtc.severity].append(dtc)
    
    return classified


def get_safety_critical_dtcs(parsed_dtcs):
    """
    Filter out only safety-critical DTCs.
    
    Args:
        parsed_dtcs: List of ParsedDTC objects
    
    Returns:
        list: Only safety-critical DTCs
    """
    return [dtc for dtc in parsed_dtcs if dtc.safety_critical]


def get_hybrid_related_dtcs(parsed_dtcs):
    """
    Filter out only hybrid-related DTCs.
    
    Args:
        parsed_dtcs: List of ParsedDTC objects
    
    Returns:
        list: Only hybrid-related DTCs
    """
    return [dtc for dtc in parsed_dtcs if dtc.hybrid_related]
