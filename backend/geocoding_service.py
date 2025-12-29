"""
Geocoding Service for TULIAN

Provides two modes:
1. Real-time geocoding via Nominatim (user-enabled, slower but precise)
2. Cached geocoding from pre-processed batch file (fast fallback)
"""

import json
import time
from pathlib import Path
from typing import Dict, Tuple, Optional
import hashlib


class GeocodingService:
    """Handles geocoding of location strings to coordinates."""
    
    CACHE_FILE = Path(__file__).parent / 'data' / 'geocoding_database.json'
    
    def __init__(self, use_realtime: bool = False):
        """
        Initialize geocoding service.
        
        Args:
            use_realtime: If True, use Nominatim API for uncached locations.
                         If False, only return cached results or None.
        """
        self.use_realtime = use_realtime
        self.cache = self._load_cache()
        self._geocoder = None
        self._last_request_time = 0
        
    def _load_cache(self) -> Dict[str, Tuple[float, float]]:
        """Load geocoding cache from file."""
        if self.CACHE_FILE.exists():
            try:
                with open(self.CACHE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file."""
        self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def _get_cache_key(self, location: str, country: str) -> str:
        """Generate cache key for location+country."""
        combined = f"{location.strip().lower()}|{country.strip().lower()}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]
    
    def _get_geocoder(self):
        """Lazy load Nominatim geocoder."""
        if self._geocoder is None:
            try:
                from geopy.geocoders import Nominatim
                self._geocoder = Nominatim(user_agent="tulian_simulation")
            except ImportError:
                print("Warning: geopy not installed. Install with: pip install geopy")
                self._geocoder = False
        return self._geocoder
    
    def _rate_limit(self):
        """Ensure 1 second between Nominatim requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_request_time = time.time()
    
    def geocode(self, location: str, country: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a location string to coordinates.
        Tries multiple query strategies for better success rate.
        
        Args:
            location: Location description (e.g., "Pine Lake area, Alberta province")
            country: Country name
        
        Returns:
            (latitude, longitude) tuple or None if not found
        """
        if not location:
            return None
        
        cache_key = self._get_cache_key(location, country)
        
        # Check cache first
        if cache_key in self.cache:
            return tuple(self.cache[cache_key])
        
        # If not using realtime, return None
        if not self.use_realtime:
            return None
        
        # Try Nominatim with multiple query strategies
        geocoder = self._get_geocoder()
        if not geocoder:
            return None
        
        # Create list of query variations to try
        queries = self._generate_query_variations(location, country)
        
        for query in queries:
            try:
                self._rate_limit()
                result = geocoder.geocode(query, timeout=10)
                
                if result:
                    coords = (result.latitude, result.longitude)
                    self.cache[cache_key] = coords
                    self._save_cache()
                    return coords
                    
            except Exception as e:
                continue
        
        return None
    
    def _generate_query_variations(self, location: str, country: str) -> list:
        """
        Generate multiple query variations for better geocoding success.
        """
        import re
        
        queries = []
        
        # 1. Try full location + country
        queries.append(f"{location}, {country}")
        
        # 2. Extract province/region names (often in parentheses or after 'province')
        # Pattern: "Something (Region province)" or "Something, Region province"
        province_match = re.search(r'\(([^)]+(?:province|region|district|state))\)', location, re.I)
        if province_match:
            province = province_match.group(1).replace('province', '').replace('region', '').strip()
            queries.append(f"{province}, {country}")
        
        # 3. Try first major location mentioned (before comma or parenthesis)
        first_part = re.split(r'[,(]', location)[0].strip()
        if first_part and len(first_part) > 3:
            queries.append(f"{first_part}, {country}")
        
        # 4. Extract anything that looks like a province/state name
        provinces = re.findall(r'(\w+)\s+(?:province|region|state|district)', location, re.I)
        for prov in provinces[:2]:  # Try first 2 matches
            queries.append(f"{prov}, {country}")
        
        # 5. Just the country as last resort
        queries.append(country)
        
        return queries
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the geocoding cache."""
        return {
            'total_cached': len(self.cache),
            'cache_file': str(self.CACHE_FILE),
            'file_exists': self.CACHE_FILE.exists()
        }


def batch_geocode_emdat(xlsx_path: str, max_records: int = None, save_every: int = 50):
    """
    Batch geocode all locations in EM-DAT file that are missing coordinates.
    
    Args:
        xlsx_path: Path to EM-DAT Excel file
        max_records: Maximum records to process (None = all)
        save_every: Save cache every N records
    
    This function should be run separately to pre-process the data.
    """
    import pandas as pd
    
    print(f"Loading {xlsx_path}...")
    df = pd.read_excel(xlsx_path, sheet_name='EM-DAT Data')
    
    # Filter to records without coordinates but with Location
    missing_coords = df[
        (df['Latitude'].isna() | df['Longitude'].isna()) & 
        df['Location'].notna()
    ]
    
    print(f"Found {len(missing_coords)} records needing geocoding")
    
    if max_records:
        missing_coords = missing_coords.head(max_records)
        print(f"Processing first {max_records} records")
    
    service = GeocodingService(use_realtime=True)
    success_count = 0
    fail_count = 0
    
    for idx, row in missing_coords.iterrows():
        location = row['Location']
        country = row['Country']
        
        coords = service.geocode(location, country)
        
        if coords:
            success_count += 1
            print(f"✓ {country}: {location[:50]}... -> {coords}")
        else:
            fail_count += 1
            print(f"✗ {country}: {location[:50]}...")
        
        if (success_count + fail_count) % save_every == 0:
            print(f"\n--- Progress: {success_count} success, {fail_count} failed ---\n")
    
    print(f"\n=== DONE ===")
    print(f"Geocoded: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"Total cached: {len(service.cache)}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        # Run batch geocoding
        xlsx_path = "../context/public_emdat_custom_request_2025-12-04.xlsx"
        max_records = int(sys.argv[2]) if len(sys.argv) > 2 else 100  # Default: 100 for testing
        batch_geocode_emdat(xlsx_path, max_records=max_records)
    else:
        # Test mode
        service = GeocodingService(use_realtime=True)
        
        # Test geocoding
        test_cases = [
            ("Pine Lake area, Alberta province", "Canada"),
            ("California", "United States of America"),
            ("Tokyo", "Japan"),
        ]
        
        for location, country in test_cases:
            coords = service.geocode(location, country)
            print(f"{location}, {country} -> {coords}")
        
        print(f"\nCache stats: {service.get_cache_stats()}")
