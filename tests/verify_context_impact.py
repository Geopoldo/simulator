
import sys
import os
import random
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulator import Simulator

def run_tests():
    print("=== REGRESSION & FEATURE VERIFICATION: CONTEXT IMPACT ===")
    
    # Mock ODK Structure
    mock_odk = {
        "survey": [
            {"type": "text", "name": "Country"},
            {"type": "select_one Yesno", "name": "HHAffectedClimate"},
            {"type": "select_one Yesno", "name": "ReceivedAssistance"}, # Maps to assistance logic
            {"type": "select_one Yesno", "name": "Displaced"}, # Maps to displacement logic
            {"type": "select_one LcsCl", "name": "LCS_Status"}, # Maps to Economic Shock
            {"type": "decimal", "name": "FoodExp_Purch"}, # Maps to Economic Shock
            {"type": "text", "name": "Comments"}
        ],
        "choices": {
            "Yesno": [{"name": "Yes"}, {"name": "No"}],
            "LcsCl": [{"name": "None"}, {"name": "Stress"}, {"name": "Crisis"}, {"name": "Emergency"}]
        }
    }
    
    # --- TEST CASE 1: HIGH SEVERITY & RESPONSE ---
    print("\n[TEST 1] High Severity + Humanitarian Response")
    high_severity_event = {
        "Country": "Colombia",
        "Start Year": 2024,
        "Total Affected": 100000,
        "ofda_response": "Yes",
        "appeal": "Yes", 
        "declaration": "Yes",
        "end_date": "2024-12-01", # Recent
        "duration_days": 180
    }
    
    sim_high = Simulator(mock_odk, context_events=[high_severity_event], country_name="Colombia")
    # Force year to 2024
    results_high = []
    for _ in range(50):
        # Manually trigger internal generation to bypass random year picking if needed, 
        # but simulator favors context years, so it should pick 2024.
        res = sim_high.simulate(1)[0]
        if res['year'] == 2024:
            results_high.append(res)
            
    # Analyze Assistance
    yes_assist = sum(1 for r in results_high if r.get('ReceivedAssistance') == 'Yes')
    print(f"  > Responses generated (2024): {len(results_high)}")
    print(f"  > Received Assistance 'Yes' count: {yes_assist} ({yes_assist/len(results_high)*100:.1f}%)")
    
    # Expectation: High probability (>50%) due to all indicators being Yes
    if yes_assist / len(results_high) > 0.4:
        print("  > PASS: High assistance probability detected.")
    else:
        print("  > FAIL: Assistance probability too low for high severity event.")

    # --- TEST CASE 2: DISPLACEMENT ---
    print("\n[TEST 2] High Homelessness -> Displacement")
    high_homeless_event = {
        "Country": "Colombia",
        "Start Year": 2023,
        "Total Affected": 50000,
        "homeless": 6000, # Corrected key
        "end_date": "2023-06-01"
    }
    
    sim_disp = Simulator(mock_odk, context_events=[high_homeless_event], country_name="Colombia")
    results_disp = [r for r in sim_disp.simulate(50) if r['year'] == 2023]
    
    yes_disp = sum(1 for r in results_disp if r.get('Displaced') == 'Yes')
    print(f"  > Displaced 'Yes' count: {yes_disp} ({yes_disp/len(results_disp)*100:.1f}%)")
    
    # Expectation: ~60% probability
    if yes_disp / len(results_disp) > 0.4:
         print("  > PASS: Significant displacement detected.")
    else:
         print("  > FAIL: Displacement probability lower than expected.")

    # --- TEST CASE 3: ECONOMIC SHOCK ---
    print("\n[TEST 3] High Economic Damage -> Coping Strategies")
    high_damage_event = {
        "Country": "Colombia",
        "Start Year": 2022,
        "Total Affected": 50000,
        "total_damage_usd": 1000000000, # Corrected key and value (1 Billion USD)
        "end_date": "2022-01-01"
    }
    
    sim_shock = Simulator(mock_odk, context_events=[high_damage_event], country_name="Colombia")
    results_shock = [r for r in sim_shock.simulate(50) if r['year'] == 2022]
    
    # Count LCS Status
    lcs_counts = {"None": 0, "Stress": 0, "Crisis": 0, "Emergency": 0}
    for r in results_shock:
        val = r.get('LCS_Status')
        if val in lcs_counts:
            lcs_counts[val] += 1
            
    print(f"  > LCS Distribution: {lcs_counts}")
    
    # Expectation: Shift towards Crisis/Emergency
    severe_ratio = (lcs_counts["Crisis"] + lcs_counts["Emergency"]) / len(results_shock)
    print(f"  > Severe Coping Ratio: {severe_ratio:.2f}")
    
    if severe_ratio > 0.4: # Baseline is much lower (weights 0.3 + 0.05 = 0.35 normally, but biased to first options)
         print("  > PASS: Economic shock shifted coping strategies.")
    else:
         print("  > FAIL: Coping strategies did not shift enough.")
         
    # Check Income/Expense reduction
    # We can't easily compare to baseline without running a baseline sim, but we can check if values exist
    avg_exp = sum(r.get('FoodExp_Purch', 0) for r in results_shock) / len(results_shock)
    print(f"  > Average Expense: {avg_exp:.2f} (Should be lower than typical base)")

    # --- TEST CASE 4: HYPER-REALISM (Narrative & Sectorial) ---
    print("\n[TEST 4] Hyper-Realism: Narrative & Shortages")
    realism_event = {
        "Country": "Colombia",
        "Start Year": 2024,
        "event_name": "Hurricane Beta", # Internal key
        "origin_desc": "Heavy coastal rains", # Internal key
        "associated_shortages": ["Food shortage", "Water shortage"], # Pre-processed list
        "magnitude": 7.5,
        "magnitude_scale": "Richter",
        "total_damage_usd": 5000000 
    }
    
    sim_real = Simulator(mock_odk, context_events=[realism_event], country_name="Colombia")
    results_real = [r for r in sim_real.simulate(20) if r['year'] == 2024]
    
    # Check Narrative
    comments = [r.get('Comments', '') for r in results_real]
    beta_mentions = sum(1 for c in comments if "Beta" in c)
    food_mentions = sum(1 for c in comments if "food" in c.lower() or "hambre" in c.lower())
    
    print(f"  > Narrative mentions of 'Beta': {beta_mentions} ({beta_mentions/len(results_real)*100:.1f}%)")
    
    if beta_mentions > 0:
        print("  > PASS: Narrative injection working.")
    else:
        print("  > FAIL: No narrative injection found.")
        
    # Check Sectorial Impact (implied by narrative or lower scores if we checked them)
    # Since we don't have FCS question in mock_odk, we rely on narrative "We have no food left" logic verification
    shortage_mentions = sum(1 for c in comments if "no food" in c.lower())
    print(f"  > Shortage Narrative: {shortage_mentions}")


if __name__ == "__main__":
    run_tests()
