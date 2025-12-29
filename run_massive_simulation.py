
import json
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from simulator import Simulator
from context_loader import ContextLoader

def run_massive():
    print("1. Loading ODK Structure...")
    try:
        with open("backend/latest_structure.json", "r") as f:
            structure = json.load(f)
    except FileNotFoundError:
        print("Error: backend/latest_structure.json not found. Please upload an ODK file first.")
        return

    print("2. Loading Context...")
    # Load context explicitly to ensure we have data
    loader = ContextLoader("context/public_emdat_custom_request_2025-12-04.xlsx")
    events = loader.get_events_by_country("Colombia") # Default to Colombia for testing

    print(f"3. Initializing Simulator with {len(events)} context events...")
    # Instantiate Simulator
    # Ensure country_name is passed if we want to force it, otherwise it infers from events
    sim = Simulator(structure, context_events=events, country_name="Colombia")

    print("4. Running Simulation (N=100)...")
    data = sim.simulate(count=100)

    print(f"5. Generated {len(data)} records.")
    
    # Analyze results
    print("\n--- Inspecting Shock Fields (First Record) ---")
    if data:
        first = data[0]
        for k, v in first.items():
            if "shock" in k.lower():
                print(f"{k}: {v}")

    fcs_counts = {}
    
    for row in data:
        fcs = row.get('FCSStap')
        fcs_counts[fcs] = fcs_counts.get(fcs, 0) + 1

    print("\n--- Summary ---")
    print("FCS Staples Distribution:", fcs_counts)

    # Save output
    outfile = "backend/simulated_data_massive.json"
    print(f"6. Saving to {outfile}...")
    with open(outfile, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    run_massive()
