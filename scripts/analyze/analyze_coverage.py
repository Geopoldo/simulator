#!/usr/bin/env python3
"""
Analyze simulation coverage to identify which fields were properly simulated
vs. which received placeholder/default values.
"""

import json
import sys
from collections import defaultdict

# Known placeholder patterns
PLACEHOLDERS = {
    "Simulated Text",
    "choice_1",
    None
}

def analyze_coverage(data_path, structure_path):
    """Analyze which fields have meaningful vs placeholder values."""
    
    # Load data
    with open(data_path, 'r') as f:
        records = json.load(f)
    
    with open(structure_path, 'r') as f:
        structure = json.load(f)
    
    if not records:
        print("No records found in simulation data.")
        return
    
    # Get all field names from structure
    all_fields = set()
    field_types = {}
    for q in structure.get('survey', []):
        if 'name' in q and not q.get('is_group_start'):
            name = q['name']
            all_fields.add(name)
            field_types[name] = q.get('type', 'unknown')
    
    # Analyze each field
    field_stats = defaultdict(lambda: {
        'total': 0,
        'placeholder': 0,
        'meaningful': 0,
        'missing': 0,
        'sample_values': set()
    })
    
    for record in records:
        for field in all_fields:
            stats = field_stats[field]
            stats['total'] += 1
            
            if field not in record:
                stats['missing'] += 1
            else:
                value = record[field]
                
                # Check if placeholder
                if value in PLACEHOLDERS or value == "Simulated Text":
                    stats['placeholder'] += 1
                else:
                    stats['meaningful'] += 1
                    # Store sample (limit to 5 unique values)
                    if len(stats['sample_values']) < 5:
                        stats['sample_values'].add(str(value)[:50])  # Truncate long values
    
    # Report
    print("=" * 80)
    print("SIMULATION COVERAGE ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Records: {len(records)}")
    print(f"Total Fields in Structure: {len(all_fields)}")
    print(f"Fields Present in Data: {len([f for f in all_fields if field_stats[f]['meaningful'] > 0 or field_stats[f]['placeholder'] > 0])}")
    
    # Categorize fields
    well_simulated = []
    partially_simulated = []
    placeholder_only = []
    never_generated = []
    
    for field, stats in field_stats.items():
        if stats['missing'] == stats['total']:
            never_generated.append(field)
        elif stats['meaningful'] == stats['total']:
            well_simulated.append(field)
        elif stats['placeholder'] == stats['total']:
            placeholder_only.append(field)
        else:
            partially_simulated.append(field)
    
    print("\n" + "=" * 80)
    print(f"✅ WELL SIMULATED ({len(well_simulated)} fields)")
    print("=" * 80)
    for field in sorted(well_simulated)[:20]:  # Show first 20
        stats = field_stats[field]
        samples = list(stats['sample_values'])[:3]
        print(f"  {field:30} | Type: {field_types.get(field, 'unknown'):20} | Samples: {samples}")
    if len(well_simulated) > 20:
        print(f"  ... and {len(well_simulated) - 20} more")
    
    print("\n" + "=" * 80)
    print(f"⚠️  PLACEHOLDER ONLY ({len(placeholder_only)} fields)")
    print("=" * 80)
    for field in sorted(placeholder_only)[:20]:
        print(f"  {field:30} | Type: {field_types.get(field, 'unknown'):20}")
    if len(placeholder_only) > 20:
        print(f"  ... and {len(placeholder_only) - 20} more")
    
    print("\n" + "=" * 80)
    print(f"❌ NEVER GENERATED ({len(never_generated)} fields)")
    print("=" * 80)
    for field in sorted(never_generated)[:20]:
        print(f"  {field:30} | Type: {field_types.get(field, 'unknown'):20}")
    if len(never_generated) > 20:
        print(f"  ... and {len(never_generated) - 20} more")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    coverage_pct = (len(well_simulated) / len(all_fields) * 100) if all_fields else 0
    print(f"Coverage: {coverage_pct:.1f}% ({len(well_simulated)}/{len(all_fields)} fields)")
    print(f"Needs Implementation: {len(placeholder_only) + len(never_generated)} fields")
    
    # Save detailed report
    report_path = "simulation_coverage_report.json"
    report = {
        "summary": {
            "total_records": len(records),
            "total_fields": len(all_fields),
            "well_simulated": len(well_simulated),
            "placeholder_only": len(placeholder_only),
            "never_generated": len(never_generated),
            "coverage_percentage": coverage_pct
        },
        "well_simulated": well_simulated,
        "placeholder_only": placeholder_only,
        "never_generated": never_generated
    }
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    analyze_coverage(
        "backend/simulated_data_massive.json",
        "backend/latest_structure.json"
    )
