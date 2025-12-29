
import requests

BASE_URL = "http://localhost:8000"

def verify():
    print(f"Checking API at {BASE_URL}")
    try:
        r = requests.get(f"{BASE_URL}/")
        print(f"Root: {r.status_code} {r.json()}")
        
        r = requests.get(f"{BASE_URL}/countries")
        countries = r.json()
        print(f"Countries loaded: {len(countries)}. Sample: {countries[:3]}")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    verify()
