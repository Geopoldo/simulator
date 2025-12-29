import requests
import os
import json

BASE_URL = "http://localhost:9005"
ODK_FILE = "ODK/HFA + CARI (FES) + HHS + climate shocks and SEI checked.xlsx"

def verify_backend_flow():
    print("=== 1. Testing Un-mocked Upload ===")
    if not os.path.exists(ODK_FILE):
        print(f"❌ ODK File not found at {ODK_FILE}")
        return

    files = {'file': open(ODK_FILE, 'rb')}
    try:
        res = requests.post(f"{BASE_URL}/upload", files=files)
        if res.status_code == 200:
            print("✅ Upload Successful")
            structure = res.json()
            # print("Structure keys:", structure.keys())
        else:
            print(f"❌ Upload Failed: {res.text}")
            return
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    print("\n=== 2. Testing Simulation (Colombia 2020-2023) ===")
    payload = {
        "odk_structure": structure,
        "countries": ["Colombia"],
        "start_year": 2020,
        "end_year": 2023,
        "count_per_country_year": 5 # Small count for speed
    }
    
    try:
        res = requests.post(f"{BASE_URL}/simulate", json=payload)
        if res.status_code == 200:
            data = res.json()
            print(f"✅ Simulation Successful. Generated {len(data)} records.")
            # Verify fields
            first = data[0]
            if "FCSStap" in first:
                print("✅ Data contains 'FCSStap'")
            else:
                 print("⚠️ Data missing 'FCSStap'")
            
            if "__progression__" in first: # Internal field, might not be in output if filtered? 
                # Simulator returns 'row'. 'row' is result of _generate_single_response.
                # _generate_single_response returns 'data' dict.
                # In simulator.py, 'data' is populated. 
                # Does it include internal keys? Usually yes unless filtered.
                pass
        else:
            print(f"❌ Simulation Failed: {res.text}")
            return
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    print("\n=== 3. Testing Persistence (Scene 3 Data Fetch) ===")
    try:
        res = requests.get(f"{BASE_URL}/simulation-results")
        if res.status_code == 200:
            persisted_data = res.json()
            print(f"✅ Fetch /simulation-results Successful. Got {len(persisted_data)} records.")
            
            if len(persisted_data) == len(data):
                print("✅ Data Persistence Verified (Counts match).")
            else:
                print(f"❌ Data Mismatch: Generated {len(data)} vs Persisted {len(persisted_data)}")
        else:
            print(f"❌ Fetch Failed: {res.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    verify_backend_flow()
