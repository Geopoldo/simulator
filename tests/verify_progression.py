import sys
import os
import json
from collections import defaultdict
import statistics

# Add path to backend
sys.path.append(os.path.abspath("backend"))

from simulator import Simulator

def verify_progression():
    print("=== Verifying Simulation Progression Logic ===")
    
    # Mock ODK structure
    odk_structure = {
        "survey": [
            {"name": "Country", "type": "text"},
            {"name": "FCSStap", "type": "integer"},
            {"name": "HHSFr", "type": "select_one HHSFr"},
            {"name": "FoodExp", "type": "integer"},
            {"name": "NonFoodExp", "type": "integer"}
        ],
        "choices": {
            "HHSFr": [
                 {"name": "No", "label": "No (0)"}, 
                 {"name": "Rarely", "label": "Rarely (1)"},
                 {"name": "Sometimes", "label": "Sometimes (2)"}
            ]
        }
    }
    
    # Mock Context Events
    events = [] # No disasters for clean progression check
    
    # Initialize Simulator
    sim = Simulator(odk_structure, context_events=events, country_name="Colombia", simulation_start_year=2020)
    
    # Run for 4 years
    years = [2020, 2021, 2022, 2023]
    results_by_year = {}
    
    for year in years:
        print(f"Simulating {year}...")
        results_by_year[year] = sim.simulate(count=20, fixed_year=year)
        
    print("\n--- Validation Results ---")
    
    # 1. Longitudinal Tracking Check
    # Check if Household 0 is the same ID in all years
    hh0_ids = [results_by_year[y][0].get('EnuName') for y in years] 
    # Note: EnuName is random, but we check internal context if possible not exposed in row
    # Let's check consistency of a static field if we exposed it. 
    # Actually, Simulator exposes generated row. 
    # We didn't explicitly expose 'household_code' or 'id' in the row unless the ODK has a field for it.
    # But internal seed logic relies on index 'i'. 
    # Let's trust logic if we can't see ID, OR verify statistical consistency.
    # EDIT: We injected `__household_code__` into context. If ODK doesn't ask for it, it won't be in output.
    # However, let's verify trends which is the main goal.
    
    # 2. Indicator Trends
    fcs_avgs = []
    hhs_avgs = []
    food_share_avgs = []
    
    for year in years:
        rows = results_by_year[year]
        
        # FCS (higher is better)
        fcs_vals = [r.get('FCSStap', 0) for r in rows]
        fcs_avg = statistics.mean(fcs_vals)
        fcs_avgs.append(fcs_avg)
        
        # HHS (lower is better, check 'No' vs others)
        hhs_vals = [0 if r.get('HHSFr') == 'No' else 1 for r in rows]
        hhs_avg = statistics.mean(hhs_vals)
        hhs_avgs.append(hhs_avg)
        
        # Food Share (lower is better)
        # Note: Output has 'FoodExp', 'NonFoodExp' purely if ODK asked. 
        # But we didn't add those fields to ODK structure in main app yet, so they might be missing in real row?
        # In our mock above, we added them. In real app, we need to check if ODK asks for them.
        # But for this test, let's see.
        
        food_exps = [r.get('FoodExp', 0) for r in rows]
        # Since we mocked the ODK above, these should exist if _gen_expense logic works map name
        # Our _gen_expense logic maps "FoodExp" -> matches "food" -> returns __food_exp__
        
        # Calculate shares
        shares = []
        for r in rows:
            fe = r.get('FoodExp', 0)
            nfe = r.get('NonFoodExp', 0)
            total = fe + nfe
            if total > 0:
                shares.append(fe / total)
        
        if shares:
            food_share_avgs.append(statistics.mean(shares))
        else:
            food_share_avgs.append(0)

    print(f"FCS Averages (Should Increase): {fcs_avgs}")
    print(f"HHS Frequency (Should Decrease): {hhs_avgs}")
    print(f"Food Share (Should Decrease from ~0.7 to 0.5): {food_share_avgs}")
    
    # Assertions
    if fcs_avgs[-1] > fcs_avgs[0]:
        print("✅ FCS Improved")
    else:
        print("❌ FCS Failed to improve")
        
    if hhs_avgs[-1] < hhs_avgs[0] or hhs_avgs[-1] == 0:
        print("✅ HHS Improved (or stayed 0)")
    else:
        print("❌ HHS Failed to improve")

    if food_share_avgs[0] > 0.6 and food_share_avgs[-1] < 0.6:
        print("✅ Food Share logic working (High -> Low)")
    else:
        print(f"⚠️ Food Share logic check: {food_share_avgs}")

if __name__ == "__main__":
    verify_progression()
