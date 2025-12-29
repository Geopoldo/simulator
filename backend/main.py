
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import shutil
import tempfile
import os
import traceback
import json
import csv
import io
from typing import List, Dict, Any, Optional

from odk_parser import ODKParser
from context_loader import ContextLoader
from simulator import Simulator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State (for demo purposes)
CONTEXT_LOADER = ContextLoader("../context/public_emdat_custom_request_2025-12-04.xlsx")

class SimulationRequest(BaseModel):
    odk_structure: Dict[str, Any]
    countries: List[str] # Changed from single country to list
    start_year: int = 2020
    end_year: int = 2024
    count_per_country_year: int = 10

@app.get("/")
def read_root():
    return {"message": "ODK Simulator API is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        parser = ODKParser(file_path=tmp_path)
        structure = parser.parse()
        
        # Cleanup
        os.remove(tmp_path)
        
        # Save analysis for agent learning
        with open("latest_structure.json", "w") as f:
            json.dump(structure, f, indent=2)
            
        return structure
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/countries")
def get_countries():
    return CONTEXT_LOADER.get_countries()

@app.get("/simulation-results")
def get_simulation_results():
    path = "simulated_data_massive.json"
    if not os.path.exists(path):
         # If massive file doesn't exist, try to generate it or return empty
         return []
    with open(path, "r") as f:
        return json.load(f)

@app.get("/latest-structure")
def get_latest_structure():
    path = "latest_structure.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="ODK structure not found. Please upload an ODK file first.")
    with open(path, "r") as f:
        return json.load(f)

@app.get("/field-order")
def get_field_order():
    """
    Returns the official ODK field order from the parsed structure.
    Used by frontend to verify CSV export order matches ODK survey order.
    """
    path = "latest_structure.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="ODK structure not found. Please upload an ODK file first.")
    
    with open(path, "r") as f:
        structure = json.load(f)
    
    # Extract field names in survey order (excluding groups)
    field_order = []
    for item in structure.get("survey", []):
        if item.get("name") and not item.get("is_group_start"):
            field_order.append(item.get("name"))
    
    return {"field_order": field_order, "count": len(field_order)}

@app.post("/simulate")
def simulate(req: SimulationRequest):
    try:
        print(f"Simulating for {req.countries} Range: {req.start_year}-{req.end_year}")
        
        all_results = []
        
        for country in req.countries:
            # Load context for this country
            events = CONTEXT_LOADER.get_events_by_country(country)
            
            # Instantiate simulator once per country
            # Pass start_year for progression calculation
            sim = Simulator(req.odk_structure, context_events=events, country_name=country, simulation_start_year=req.start_year)

            # Loop through years
            for year in range(req.start_year, req.end_year + 1):
                # Generate batch for this year
                print(f"  > Generating {req.count_per_country_year} rows for {country} in {year}")
                batch_data = sim.simulate(count=req.count_per_country_year, fixed_year=year)
                all_results.extend(batch_data)
        
        # Save massive file
        with open("simulated_data_massive.json", "w") as f:
            json.dump(all_results, f, indent=2)

        return all_results
    except Exception as e:
        print("CRITICAL ERROR IN SIMULATE:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-csv")
def export_csv(data: List[Dict[str, Any]]):
    """
    Export simulation data as CSV file.
    Accepts a list of dictionaries and returns a CSV file.
    Preserves the original field order from simulation (matches ODK survey order).
    """
    try:
        if not data:
            raise HTTPException(status_code=400, detail="No data provided for export")
        
        # Create CSV in memory
        output = io.StringIO()
        
        # IMPORTANT: Preserve original order from first record
        # The simulator uses OrderedDict to maintain ODK survey order
        # Use the first record's key order as the canonical order
        fieldnames = list(data[0].keys())
        
        # Add any extra keys from other records (should be rare)
        for record in data[1:]:
            for key in record.keys():
                if key not in fieldnames:
                    fieldnames.append(key)
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=simulation_results.csv"
            }
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=9005, reload=True)
