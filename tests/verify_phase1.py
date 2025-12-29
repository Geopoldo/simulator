#!/usr/bin/env python3
"""
Verification script for Phase 1 implementation:
- Disaster Subtype usage
- Temporal dynamics (recency, duration)
- Magnitude-based severity
"""

import json
import sys
import os

# Determine project root (tests/ is one level down)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'backend'))

def verify_phase1():
    print("=" * 80)
    print("PHASE 1 VERIFICATION: Temporal Dynamics & Disaster Specificity")
    print("=" * 80)
    
    # Load simulated data
    with open(os.path.join(PROJECT_ROOT, "backend/simulated_data_massive.json"), "r") as f:
        data = json.load(f)
    
    print(f"\n✓ Loaded {len(data)} simulated records")
    
    # Load context to check what disasters are available
    from context_loader import ContextLoader
    loader = ContextLoader(os.path.join(PROJECT_ROOT, "context/public_emdat_custom_request_2025-12-04.xlsx"))
    events = loader.get_events_by_country("Colombia")
    
    print(f"✓ Loaded {len(events)} disaster events for Colombia")
    
    # Check for disaster subtypes
    print("\n" + "=" * 80)
    print("1. DISASTER SUBTYPE SPECIFICITY")
    print("=" * 80)
    
    subtypes_in_context = set()
    magnitudes = []
    durations = []
    
    for event in events:
        subtype = event.get('disaster_subtype')
        if subtype:
            subtypes_in_context.add(subtype)
        
        mag = event.get('magnitude')
        if mag:
            magnitudes.append((mag, event.get('magnitude_scale')))
        
        duration = event.get('duration_days')
        if duration:
            durations.append(duration)
    
    print(f"Disaster Subtypes in Context: {len(subtypes_in_context)}")
    print(f"Sample Subtypes: {list(subtypes_in_context)[:5]}")
    
    # Check temporal data
    print("\n" + "=" * 80)
    print("2. TEMPORAL DATA EXTRACTION")
    print("=" * 80)
    
    events_with_dates = sum(1 for e in events if e.get('start_date') and e.get('end_date'))
    events_with_duration = sum(1 for e in events if e.get('duration_days') is not None)
    
    print(f"Events with Start/End Dates: {events_with_dates}/{len(events)} ({events_with_dates/len(events)*100:.1f}%)")
    print(f"Events with Duration Calculated: {events_with_duration}/{len(events)} ({events_with_duration/len(events)*100:.1f}%)")
    
    if durations:
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        print(f"Average Duration: {avg_duration:.0f} days")
        print(f"Max Duration: {max_duration} days (prolonged disaster)")
    
    # Check magnitude data
    print("\n" + "=" * 80)
    print("3. MAGNITUDE & SCALE DATA")
    print("=" * 80)
    
    events_with_magnitude = sum(1 for e in events if e.get('magnitude'))
    print(f"Events with Magnitude: {events_with_magnitude}/{len(events)} ({events_with_magnitude/len(events)*100:.1f}%)")
    
    if magnitudes:
        print(f"\nSample Magnitudes:")
        for mag, scale in magnitudes[:5]:
            print(f"  - {mag} {scale}")
    
    # Check impact variation
    print("\n" + "=" * 80)
    print("4. IMPACT CALCULATION VERIFICATION")
    print("=" * 80)
    
    # Sample a few records and check FCS variation
    fcs_values = [r.get('FCSStap', 0) for r in data]
    fcs_avg = sum(fcs_values) / len(fcs_values)
    fcs_std = (sum((x - fcs_avg)**2 for x in fcs_values) / len(fcs_values)) ** 0.5
    
    print(f"FCS Staples - Mean: {fcs_avg:.2f}, Std Dev: {fcs_std:.2f}")
    print(f"FCS Range: {min(fcs_values)} - {max(fcs_values)}")
    
    # Success criteria
    print("\n" + "=" * 80)
    print("SUCCESS CRITERIA")
    print("=" * 80)
    
    criteria = {
        "Disaster Subtypes Extracted": len(subtypes_in_context) > 0,
        "Temporal Data (>90%)": events_with_dates / len(events) > 0.9,
        "Duration Calculated": events_with_duration > 0,
        "Magnitude Data (>30%)": events_with_magnitude / len(events) > 0.3,
        "FCS Variation (Std > 1.5)": fcs_std > 1.5
    }
    
    for criterion, passed in criteria.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {criterion}")
    
    all_passed = all(criteria.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 PHASE 1 VERIFICATION: ALL TESTS PASSED")
    else:
        print("⚠️  PHASE 1 VERIFICATION: SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = verify_phase1()
    sys.exit(0 if success else 1)
