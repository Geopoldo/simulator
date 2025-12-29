
import pandas as pd
import json

class ContextLoader:
    def __init__(self, emdat_path=None):
        self.emdat_path = emdat_path
        self.em_dat_df = None
        
        if self.emdat_path:
            self.load_data()

    def load_data(self):
        print(f"Loading Context Data from {self.emdat_path}...")
        self.em_dat_df = pd.read_excel(self.emdat_path, sheet_name='EM-DAT Data')
        # Normalize country names to uppercase for easier matching
        if 'Country' in self.em_dat_df.columns:
            self.em_dat_df['Country_Norm'] = self.em_dat_df['Country'].str.upper().str.strip()

    def get_countries(self):
        if self.em_dat_df is None:
            return []
        return sorted(self.em_dat_df['Country'].unique().tolist())

    def get_events_by_country(self, country_name):
        if self.em_dat_df is None:
            return []
        
        from datetime import datetime
        
        country_norm = country_name.upper().strip()
        filtered = self.em_dat_df[self.em_dat_df['Country_Norm'] == country_norm]
        
        if filtered.empty:
            return []

        # Return list of dicts, converting NaNs to None (JSON compliant)
        records = filtered.to_dict(orient='records')
        clean_records = []
        for r in records:
            clean_r = {k: (v if pd.notna(v) else None) for k, v in r.items()}
            
            # Parse Admin Units JSON
            if clean_r.get('Admin Units'):
                try:
                    clean_r['Admin Units'] = json.loads(clean_r['Admin Units'])
                except:
                    clean_r['Admin Units'] = []
            
            # PHASE 1: Add temporal and specificity fields
            # Disaster Subtype (already in data, just ensure it's accessible)
            clean_r['disaster_subtype'] = clean_r.get('Disaster Subtype')
            
            # Temporal fields
            clean_r['start_month'] = clean_r.get('Start Month')
            clean_r['end_month'] = clean_r.get('End Month')
            clean_r['end_year'] = clean_r.get('End Year')
            clean_r['start_day'] = clean_r.get('Start Day', 1)
            clean_r['end_day'] = clean_r.get('End Day', 28)
            
            # Calculate dates and duration
            try:
                start_year = int(clean_r.get('Start Year', 2000))
                start_month = int(clean_r.get('start_month', 1))
                start_day = int(clean_r.get('start_day', 1))
                
                end_year = int(clean_r.get('end_year', start_year))
                end_month = int(clean_r.get('end_month', start_month))
                end_day = int(clean_r.get('end_day', 28))
                
                start_date = datetime(start_year, start_month, start_day)
                end_date = datetime(end_year, end_month, end_day)
                
                clean_r['start_date'] = start_date.isoformat()
                clean_r['end_date'] = end_date.isoformat()
                clean_r['duration_days'] = (end_date - start_date).days
            except:
                clean_r['start_date'] = None
                clean_r['end_date'] = None
                clean_r['duration_days'] = 0
            
            # Magnitude fields
            clean_r['magnitude'] = clean_r.get('Magnitude')
            clean_r['magnitude_scale'] = clean_r.get('Magnitude Scale')
            
            # Geographic coordinates (actual disaster location)
            clean_r['latitude'] = clean_r.get('Latitude')
            clean_r['longitude'] = clean_r.get('Longitude')
            clean_r['location'] = clean_r.get('Location')
            
            # PHASE 2: Humanitarian response and severity indicators
            clean_r['ofda_response'] = clean_r.get('OFDA/BHA Response')
            clean_r['appeal'] = clean_r.get('Appeal')
            clean_r['declaration'] = clean_r.get('Declaration')
            
            # PHASE 3: Detailed humanitarian impact metrics
            clean_r['homeless'] = clean_r.get('No. Homeless')
            clean_r['injured'] = clean_r.get('No. Injured')
            # Convert to USD (data is in thousands)
            total_damage_k = clean_r.get('Total Damage (\'000 US$)')
            clean_r['total_damage_usd'] = total_damage_k * 1000 if total_damage_k else None
            
            # PHASE 4: Hyper-Realism Fields
            # 1. Sectorial Shortages
            assoc_types = clean_r.get('Associated Types')
            if pd.notna(assoc_types):
                # Split by pipe or comma just in case, though analyzing showed usually pipe?
                # The analysis showed 'Food shortage|Water shortage'.
                clean_r['associated_shortages'] = str(assoc_types).split('|')
            else:
                clean_r['associated_shortages'] = []

            # 2. Narrative Fields
            clean_r['event_name'] = clean_r.get('Event Name')
            clean_r['origin_desc'] = clean_r.get('Origin')

            # 3. Recovery / Aid Efficiency
            aid_k = clean_r.get('AID Contribution (\'000 US$)')
            clean_r['aid_contribution_usd'] = aid_k * 1000 if pd.notna(aid_k) else 0.0
            
            clean_records.append(clean_r)
        
        return clean_records

if __name__ == "__main__":
    loader = ContextLoader("../context/public_emdat_custom_request_2025-12-04.xlsx")
    countries = loader.get_countries()
    print(f"Loaded {len(countries)} countries")
    events = loader.get_events_by_country("Colombia")
    print(f"Details for Colombia: {len(events)} events found.")
    if events:
        print(events[0]['Disaster Type'])
