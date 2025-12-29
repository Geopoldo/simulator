"""
Humanitarian Response Module

Extracted from simulator.py for better modularity.
Contains functions for calculating humanitarian assistance, displacement, and health impact.
"""

from typing import Dict, Any, List


def calculate_assistance_probability(
    events: List[Dict[str, Any]], 
    config
) -> float:
    """
    Calculate probability of receiving humanitarian assistance based on:
    - OFDA/BHA Response presence
    - International appeals
    - Government declarations
    
    Args:
        events: List of filtered disaster events
        config: SimulationConfig instance
    
    Returns:
        Probability (0.15-0.85)
    """
    has_ofda = any(e.get('ofda_response') == 'Yes' for e in events)
    has_appeal = any(e.get('appeal') == 'Yes' for e in events)
    has_declaration = any(e.get('declaration') == 'Yes' for e in events)
    
    return config.calculate_assistance_probability(
        has_ofda=has_ofda,
        has_appeal=has_appeal,
        has_declaration=has_declaration
    )


def check_displacement(events: List[Dict[str, Any]], config) -> float:
    """
    Check if household was likely displaced based on homelessness data.
    
    Args:
        events: List of filtered disaster events
        config: SimulationConfig instance
    
    Returns:
        Displacement probability (0.0-0.6)
    """
    total_homeless = sum(e.get('homeless', 0) or 0 for e in events)
    return config.get_displacement_probability(total_homeless)


def check_health_impact(events: List[Dict[str, Any]], config) -> float:
    """
    Check health impact based on injury data.
    
    Args:
        events: List of filtered disaster events
        config: SimulationConfig instance
    
    Returns:
        Health impact probability (0.0-0.5)
    """
    total_injured = sum(e.get('injured', 0) or 0 for e in events)
    return config.get_health_impact_probability(total_injured)


def calculate_economic_shock(events: List[Dict[str, Any]]) -> float:
    """
    Calculate economic shock level based on total damage.
    Uses logarithmic scale.
    
    Args:
        events: List of filtered disaster events
    
    Returns:
        Shock level (0.0-1.0)
    """
    import math
    
    total_damage = sum(e.get('total_damage_usd', 0) or 0 for e in events)
    
    if total_damage <= 0:
        return 0.0
    
    # Logarithmic scale: $1M = 0.2, $10M = 0.4, $100M = 0.6, $1B = 0.8, $10B = 1.0
    return min(1.0, math.log10(total_damage) / 10)
