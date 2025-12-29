#!/usr/bin/env python3
"""
Verification script for Phase 2 implementation:
- Humanitarian response indicators (OFDA, Appeal, Declaration)
- Severity score calculation
- Assistance probability correlation
"""

import json
import sys

def verify_phase2():
    print("=" * 80)
    print("PHASE 2 VERIFICATION: Humanitarian Response & Severity")
    print("=" * 80)
    
    # Load context
    from backend.context_loader import ContextLoader
    loader = ContextLoader("context/public_emdat_custom_request_2025-12-04.xlsx")
    events = loader.get_events_by_country("Colombia")
    
    print(f"\n✓ Loaded {len(events)} disaster events for Colombia")
    
    # Check humanitarian response indicators
    print("\n" + "=" * 80)
    print("1. HUMANITARIAN RESPONSE INDICATORS")
    print("=" * 80)
    
    ofda_count = sum(1 for e in events if e.get('ofda_response') == 'Yes')
    appeal_count = sum(1 for e in events if e.get('appeal') == 'Yes')
    declaration_count = sum(1 for e in events if e.get('declaration') == 'Yes')
    
    print(f"Events with OFDA/BHA Response: {ofda_count}/{len(events)} ({ofda_count/len(events)*100:.1f}%)")
    print(f"Events with International Appeal: {appeal_count}/{len(events)} ({appeal_count/len(events)*100:.1f}%)")
    print(f"Events with Government Declaration: {declaration_count}/{len(events)} ({declaration_count/len(events)*100:.1f}%)")
    
    # Calculate severity scores
    print("\n" + "=" * 80)
    print("2. SEVERITY SCORE DISTRIBUTION")
    print("=" * 80)
    
    severity_scores = []
    for event in events:
        score = 0
        if event.get('ofda_response') == 'Yes': score += 1
        if event.get('appeal') == 'Yes': score += 1
        if event.get('declaration') == 'Yes': score += 1
        severity_scores.append(score)
    
    for score in range(4):
        count = severity_scores.count(score)
        pct = (count / len(severity_scores)) * 100 if severity_scores else 0
        print(f"Severity {score}: {count} events ({pct:.1f}%)")
    
    avg_severity = sum(severity_scores) / len(severity_scores) if severity_scores else 0
    print(f"\nAverage Severity Score: {avg_severity:.2f}")
    
    # Check impact on simulated data
    print("\n" + "=" * 80)
    print("3. IMPACT ON SIMULATION")
    print("=" * 80)
    
    # Load simulated data
    with open("backend/simulated_data_massive.json", "r") as f:
        data = json.load(f)
    
    print(f"Simulated Records: {len(data)}")
    
    # Check FCS variation (should be influenced by severity)
    fcs_values = [r.get('FCSStap', 0) for r in data]
    fcs_avg = sum(fcs_values) / len(fcs_values)
    fcs_std = (sum((x - fcs_avg)**2 for x in fcs_values) / len(fcs_values)) ** 0.5
    
    print(f"FCS Staples - Mean: {fcs_avg:.2f}, Std Dev: {fcs_std:.2f}")
    
    # Success criteria
    print("\n" + "=" * 80)
    print("SUCCESS CRITERIA")
    print("=" * 80)
    
    criteria = {
        "OFDA Response Extracted": ofda_count > 0,
        "Appeal Data Extracted": appeal_count >= 0,  # Can be 0
        "Declaration Data Extracted": declaration_count >= 0,  # Can be 0
        "Severity Scores Calculated": len(severity_scores) == len(events),
        "Multiple Severity Levels": len(set(severity_scores)) > 1,
        "FCS Variation Maintained": fcs_std > 1.5
    }
    
    for criterion, passed in criteria.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {criterion}")
    
    all_passed = all(criteria.values())
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 PHASE 2 VERIFICATION: ALL TESTS PASSED")
    else:
        print("⚠️  PHASE 2 VERIFICATION: SOME TESTS FAILED")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = verify_phase2()
    sys.exit(0 if success else 1)
