"""
Simulation Package

Modular components for the TULIAN disaster simulation engine.
"""

from .disaster_impact import (
    calculate_enhanced_impact,
    get_magnitude_multiplier,
    calculate_temporal_impact,
    calculate_severity_score,
    calculate_physical_destruction_prob,
)

from .humanitarian import (
    calculate_assistance_probability,
    check_displacement,
    check_health_impact,
    calculate_economic_shock,
)

__all__ = [
    # Disaster impact
    'calculate_enhanced_impact',
    'get_magnitude_multiplier',
    'calculate_temporal_impact',
    'calculate_severity_score',
    'calculate_physical_destruction_prob',
    # Humanitarian
    'calculate_assistance_probability',
    'check_displacement',
    'check_health_impact',
    'calculate_economic_shock',
]
