"""
Configuration loader for simulation parameters.
Loads YAML config files and provides easy access to simulation parameters.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class SimulationConfig:
    """Centralized configuration manager for simulation parameters."""
    
    def __init__(self, config_dir: str = 'config'):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Path to configuration directory (relative to backend/)
        """
        self.config_dir = Path(__file__).parent / config_dir
        
        # Load all config files
        self.params = self._load_yaml('simulation_params.yaml')
        self.fields = self._load_yaml('field_mappings.yaml')
        
        # Cache frequently accessed values
        self._progression_cache = self.params['progression']
        self._disaster_cache = self.params['disaster_impact']['magnitude_multipliers']
    
    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file."""
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    # ===== Progression Methods =====
    
    def get_progression_value(self, year_index: int) -> float:
        """
        Get progression factor for a given year index.
        
        Args:
            year_index: Number of years since baseline (0, 1, 2, 3+)
        
        Returns:
            Progression factor (0.0 = crisis, 1.0 = sustainability)
        """
        if year_index == 0:
            return self._progression_cache['year_0']
        elif year_index == 1:
            return self._progression_cache['year_1']
        elif year_index == 2:
            return self._progression_cache['year_2']
        else:
            return self._progression_cache['year_3_plus']
    
    # ===== Disaster Impact Methods =====
    
    def get_disaster_multiplier(self, magnitude: float, scale: str) -> float:
        """
        Get impact multiplier based on disaster magnitude and scale.
        
        Args:
            magnitude: Numerical magnitude value
            scale: Scale type ('Richter', 'Km/h', 'Kph', 'Km2', 'mm', 'Mm')
        
        Returns:
            Impact multiplier (1.0 = baseline, higher = more severe)
        """
        # Map scale names to config keys
        scale_map = {
            'Richter': 'richter',
            'Km/h': 'wind_speed',
            'Kph': 'wind_speed',
            'Km2': 'area_affected',
            'mm': 'precipitation',
            'Mm': 'precipitation'
        }
        
        scale_key = scale_map.get(scale)
        if not scale_key:
            return 1.0
        
        # Get thresholds for this scale
        thresholds = self._disaster_cache.get(scale_key, [])
        
        # Find matching threshold (highest threshold that magnitude exceeds)
        for item in thresholds:
            if magnitude >= item['threshold']:
                return item['multiplier']
        
        return 1.0
    
    # ===== Economic Shock Methods =====
    
    def get_shock_threshold(self, level: str) -> float:
        """Get economic shock threshold for a given severity level."""
        return self.params['economic_shock']['thresholds'].get(level, 0.0)
    
    # ===== Assistance Methods =====
    
    def get_assistance_params(self) -> Dict[str, Any]:
        """Get all humanitarian assistance probability parameters."""
        return self.params['assistance_probability']
    
    def calculate_assistance_probability(
        self,
        has_ofda: bool = False,
        has_appeal: bool = False,
        has_declaration: bool = False
    ) -> float:
        """
        Calculate assistance probability based on response indicators.
        
        Args:
            has_ofda: OFDA/BHA response present
            has_appeal: International appeal issued
            has_declaration: Government declaration made
        
        Returns:
            Probability of receiving assistance (0.0-1.0)
        """
        params = self.params['assistance_probability']
        prob = params['base']
        
        if has_ofda:
            prob += params['modifiers']['ofda_response']
        if has_appeal:
            prob += params['modifiers']['appeal']
        if has_declaration:
            prob += params['modifiers']['declaration']
        
        return min(prob, params['max'])
    
    # ===== FCS Methods =====
    
    def get_fcs_boost(self, field_type: str) -> float:
        """Get FCS field-specific boost value."""
        return self.params['fcs_boosts'].get(field_type, 0.0)
    
    def get_fcs_fields(self) -> List[str]:
        """Get list of FCS field names."""
        return self.fields['fcs_fields']
    
    # ===== RCSI Methods =====
    
    def get_rcsi_fields(self) -> List[str]:
        """Get list of RCSI field names."""
        return self.fields['rcsi_fields']
    
    # ===== Health Impact Methods =====
    
    def get_health_impact_probability(self, injured_count: int) -> float:
        """Get health impact probability based on number of injuries."""
        thresholds = self.params['health_impact']['injured_thresholds']
        
        for item in thresholds:
            if injured_count > item['count']:
                return item['probability']
        
        return self.params['health_impact']['baseline']
    
    # ===== Displacement Methods =====
    
    def get_displacement_probability(self, homeless_count: int) -> float:
        """Get displacement probability based on number of homeless."""
        thresholds = self.params['displacement']['homeless_thresholds']
        
        for item in thresholds:
            if homeless_count > item['count']:
                return item['probability']
        
        return self.params['displacement']['baseline']
    
    # ===== Physical Destruction Methods =====
    
    def get_destruction_probability(self, magnitude: float, scale: str) -> float:
        """
        Get probability of total physical destruction (house loss).
        
        Args:
            magnitude: Disaster magnitude
            scale: Scale type
        
        Returns:
            Probability of total house destruction (0.0-1.0)
        """
        params = self.params['physical_destruction']
        
        if scale == 'Richter':
            if magnitude >= params['richter']['catastrophic']:
                return params['probabilities']['richter_7_plus']
            elif magnitude >= params['richter']['major']:
                return params['probabilities']['richter_6_plus']
        
        elif scale in ['Km/h', 'Kph']:
            if magnitude >= params['wind_speed']['category_5']:
                return params['probabilities']['wind_200_plus']
            elif magnitude >= params['wind_speed']['category_4']:
                return params['probabilities']['wind_150_plus']
        
        return 0.0
    
    # ===== Geopoint Methods =====
    
    def get_geopoint_variation(self, source: str) -> float:
        """
        Get coordinate variation distance based on source.
        
        Args:
            source: 'disaster_based', 'profile_based', or 'faker_fallback'
        
        Returns:
            Variation in degrees (approximate ±km)
        """
        return self.params['geopoint_variation'].get(source, 0.1)


# Singleton instance
_config_instance: Optional[SimulationConfig] = None


def get_config() -> SimulationConfig:
    """Get singleton config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = SimulationConfig()
    return _config_instance
