
import requests
import json
import random

# Use the new port
BASE_URL = "http://localhost:9005"

def test_simulation():
    print("1. Fetching Countries...")
    try:
        r = requests.get(f"{BASE_URL}/countries")
        countries = r.json()
        print(f"   Countries found: {len(countries)}")
        if not countries:
            print("   ERROR: No countries returned. Context loader might be failing.")
            return
            
        target_country = "Colombia" if "Colombia" in countries else countries[0]
        print(f"2. Simulating for {target_country}...")
        
        # We need a structure. Using a dummy structure for test if upload not done.
        # But wait, the backend needs a valid structure to simulate.
        # I'll construct a minimal structure payload.
        
        dummy_structure = {
            "survey": [
                {"type": "select_one yesno", "name": "consent", "label": "Consent"},
                {"type": "integer", "name": "age", "label": "Age", "relevant": "${consent} = '1'"},
                {"type": "integer", "name": "FCSStap", "label": "Staples"}, # Test FCS logic
                {"type": "decimal", "name": "FoodExp", "label": "Food Expense"},
                {"type": "select_multiple yesno", "name": "sources", "label": "Sources"},
                {"type": "select_one admin", "name": "ADMIN1", "label": "Department"},
                {"type": "text", "name": "shock_type", "label": "Shock Type"},
                {"type": "integer", "name": "test_constraint", "label": "Constraint Test", "constraint": ". > 50"},
                {"type": "select_one LcsCl", "name": "lcs_strategy", "label": "Livelihood Strategy"}
            ],
            "choices": {
                "yesno": [{"name": "1", "label": "Yes"}, {"name": "0", "label": "No"}],
                "admin": [{"name": "dummy", "label": "dummy"}],
                "LcsCl": [{"name": "stress", "label": "Stress"}, {"name": "crisis", "label": "Crisis"}, {"name": "emergency", "label": "Emergency"}]
            }
        }

        
        req = {
            "odk_structure": dummy_structure,
            "countries": [target_country],
            "start_year": 2020,
            "end_year": 2024,
            "count_per_country_year": 2
        }
        
        print(f"   Payload: {req.keys()}")
        r = requests.post(f"{BASE_URL}/simulate", json=req)
        if r.status_code != 200:
            print(f"   ERROR: Simulation failed {r.status_code}")
            try:
                print(r.json())
            except:
                print(r.text)
            return
            
        data = r.json()
        print(f"   Generated {len(data)} records.")
        for row in data:
            print(f"   - Consent: {row.get('consent')} | Age: {row.get('age')} | Year: {row.get('year')} | FCS: {row.get('FCSStap')} | Shock: {row.get('shock_type')} | Constrained: {row.get('test_constraint')}")
            
    except Exception as e:
        print(f"   CRASH: {e}")

if __name__ == "__main__":
    test_simulation()
