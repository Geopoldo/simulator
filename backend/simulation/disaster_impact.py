"""
Disaster Impact Calculations Module

Extracted from simulator.py for better modularity.
Contains functions for calculating disaster severity, temporal impact, and physical destruction.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import math


def calculate_enhanced_impact(event: Dict[str, Any], survey_date: datetime, config) -> float:
    """
    Calculate enhanced disaster impact using:
    - Base impact from Total Affected (logarithmic)
    - Magnitude multiplier (disaster-specific severity)
    - Temporal factor (recency and duration)
    - Severity score (official indicators)
    - Sectorial penalties
    
    Args:
        event: Disaster event data from EM-DAT
        survey_date: Date of the survey
        config: SimulationConfig instance
    
    Returns:
        Combined impact factor (0.0+)
    """
    # Base impact from Total Affected
    affected = event.get('Total Affected')
    if affected and affected > 0:
        base_impact = math.log10(affected) * 0.5
    else:
        base_impact = 0.5  # Minimal impact if no data
    
    # Magnitude multiplier
    magnitude_mult = get_magnitude_multiplier(event, config)
    
    # Temporal factor
    temporal_mult = calculate_temporal_impact(event, survey_date)
    
    # Severity score (official indicators)
    severity_score = calculate_severity_score(event)
    severity_mult = 1.0 + (0.25 * severity_score)  # +25% per indicator (max +75%)
    
    # Combined impact
    total_impact = base_impact * magnitude_mult * temporal_mult * severity_mult
    
    # Sectorial Penalty: Check for specific shortages
    shortages = event.get('associated_shortages', [])
    if "Food shortage" in shortages:
        total_impact *= 1.25  # 25% extra impact on food security
    
    return total_impact


def get_magnitude_multiplier(event: Dict[str, Any], config) -> float:
    """
    Calculate severity multiplier based on disaster magnitude and scale.
    Thresholds loaded from config/simulation_params.yaml
    
    Args:
        event: Disaster event data
        config: SimulationConfig instance
    
    Returns:
        Multiplier (1.0-2.0)
    """
    mag = event.get('magnitude')
    scale = event.get('magnitude_scale')
    
    if not mag or not scale:
        return 1.0
    
    try:
        mag = float(mag)
    except (TypeError, ValueError):
        return 1.0
    
    return config.get_disaster_multiplier(mag, scale)


def calculate_temporal_impact(event: Dict[str, Any], survey_date: datetime) -> float:
    """
    Calculate temporal impact factor based on:
    - Recency (disasters decay over 12 months)
    - Duration (longer disasters have more impact)
    
    Args:
        event: Disaster event data
        survey_date: Date of the survey
    
    Returns:
        Temporal multiplier (0.0-1.5)
    """
    # Get end date
    end_date_str = event.get('end_date')
    if not end_date_str:
        return 1.0  # No temporal data, use baseline
    
    try:
        end_date = datetime.fromisoformat(end_date_str)
    except (TypeError, ValueError):
        return 1.0
    
    # Recency factor (decay over 12 months)
    days_since = (survey_date - end_date).days
    months_since = days_since / 30.0
    
    if months_since < 0:
        # Future event
        recency_factor = 1.0
    elif months_since <= 3:
        # Very recent (0-3 months): full impact
        recency_factor = 1.0
    elif months_since <= 12:
        # Recent (3-12 months): linear decay with aid modulation
        damage = event.get('total_damage_usd') or 1
        aid = event.get('aid_contribution_usd') or 0
        
        decay_speed = 1.0
        if damage > 0:
            ratio = aid / damage
            if ratio > 0.5:
                decay_speed = 2.0  # Aid > 50% of damage: faster recovery
            elif ratio < 0.1:
                decay_speed = 0.5  # Aid < 10%: slower recovery
        
        progress = (months_since - 3) / 9
        adjusted_progress = min(1.0, progress * decay_speed)
        recency_factor = 1.0 - adjusted_progress
    else:
        # Old (>12 months): minimal impact
        recency_factor = 0.0
    
    # Duration factor
    duration_days = event.get('duration_days') or 30
    if duration_days > 365:
        duration_factor = 1.5  # Multi-year disaster
    elif duration_days > 180:
        duration_factor = 1.3  # Long disaster (6-12 months)
    elif duration_days > 90:
        duration_factor = 1.1  # Medium disaster (3-6 months)
    else:
        duration_factor = 1.0  # Short disaster
    
    return max(0.0, recency_factor * duration_factor)


def calculate_severity_score(event: Dict[str, Any]) -> int:
    """
    Calculate disaster severity score (0-3) based on official indicators:
    - OFDA/BHA Response
    - Appeal
    - Declaration
    
    Args:
        event: Disaster event data
    
    Returns:
        Score 0-3
    """
    score = 0
    
    if event.get('ofda_response') == 'Yes':
        score += 1
    if event.get('appeal') == 'Yes':
        score += 1
    if event.get('declaration') == 'Yes':
        score += 1
    
    return score


def calculate_physical_destruction_prob(events: List[Dict[str, Any]], config) -> float:
    """
    Calculate probability of total physical destruction (house loss).
    
    Args:
        events: List of disaster events
        config: SimulationConfig instance
    
    Returns:
        Destruction probability (0.0-0.6)
    """
    prob = 0.0
    
    for event in events:
        mag = event.get('magnitude')
        scale = event.get('magnitude_scale')
        
        if not mag:
            continue
        
        try:
            mag = float(mag)
            destruction_prob = config.get_destruction_probability(mag, scale)
            prob = max(prob, destruction_prob)
        except (TypeError, ValueError):
            pass
    
    return prob
