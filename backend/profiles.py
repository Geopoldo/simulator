"""
Country Profiles Module

Provides country-specific parameters for food security simulations.
Configuration is loaded from config/country_profiles.yaml.
"""
from __future__ import annotations

import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import yaml
from faker import Faker


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass(frozen=True)
class ExpenseParameters:
    base_mean: float
    base_std: float
    min_value: float
    decay_range: Tuple[float, float]
    scale: float


@dataclass(frozen=True)
class CountryProfile:
    name: str
    iso2: Optional[str]
    locales: List[str]
    timezone: str
    currency: str
    region: str
    enumerators: List[str]
    supervisors: List[str]
    organizations: List[str]
    settlements: List[str]
    administrative: Dict[str, List[str]]
    household_size_range: Tuple[int, int]
    expense: ExpenseParameters
    fcs_base_range: Tuple[float, float]
    fcs_improve_range: Tuple[float, float]
    yesno_adjust: float
    geopoints: List[Tuple[float, float]]
    altitude_base: float
    altitude_variation: float
    accuracy_range: Tuple[float, float]

    def generate_household_profile(self, rng: Optional[random.Random] = None) -> Dict[str, Any]:
        """Generates basic household characteristics."""
        use_rng = rng if rng else random
        return {
            "__household_head_gender__": use_rng.choice(["Male", "Female"]),
            "__household_head_age__": use_rng.randint(18, 85),
            "__wealth_quintile__": use_rng.randint(1, 5)
        }


# =============================================================================
# YAML LOADER
# =============================================================================

_CONFIG_CACHE: Dict[str, Any] = {}


def _load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if _CONFIG_CACHE:
        return _CONFIG_CACHE
    
    config_path = Path(__file__).parent / "config" / "country_profiles.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    _CONFIG_CACHE.update(config)
    return _CONFIG_CACHE


def _get_region_defaults() -> Dict[str, Dict[str, Any]]:
    """Get region defaults from config."""
    config = _load_config()
    return config.get("region_defaults", {})


def _get_country_metadata() -> Dict[str, Dict[str, Any]]:
    """Get country metadata from config."""
    config = _load_config()
    countries = config.get("countries", {})
    # Convert to expected format (adding 'name' key)
    result = {}
    for name, data in countries.items():
        entry = {"name": name}
        entry.update(data)
        result[name] = entry
    return result


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _wrap_longitude(value: float) -> float:
    wrapped = (value + 180.0) % 360.0 - 180.0
    if wrapped == -180.0 and value > 0:
        return 180.0
    return wrapped


def _unique_values(generator, rng: random.Random, count: int) -> List[str]:
    values: List[str] = []
    attempts = 0
    while len(values) < count and attempts < count * 15:
        candidate = generator()
        if candidate:
            normalized = str(candidate).strip()
            if normalized and normalized not in values:
                values.append(normalized)
        attempts += 1
    while len(values) < count:
        filler = f"Sample {len(values) + 1}"
        if filler not in values:
            values.append(filler)
    return values


def _location_values(fake: Faker, rng: random.Random, count: int, attributes: List[str]) -> List[str]:
    for attr in attributes:
        func = getattr(fake, attr, None)
        if callable(func):
            values = _unique_values(func, rng, count)
            if values:
                return values
    return _unique_values(fake.city, rng, count)


def _generate_small_units(fake: Faker, rng: random.Random, count: int) -> List[str]:
    suffixes = ["Village", "Settlement", "Camp", "Quarter", "Ward", "Locality"]
    values: List[str] = []
    attempts = 0
    while len(values) < count and attempts < count * 20:
        base = fake.city() if callable(getattr(fake, "city", None)) else fake.last_name()
        suffix = rng.choice(suffixes)
        name = f"{base.strip()} {suffix}".strip()
        if name not in values:
            values.append(name)
        attempts += 1
    while len(values) < count:
        values.append(f"Locality {len(values) + 1}")
    return values


def _build_organizations(meta: Dict[str, Any], fake: Faker, rng: random.Random) -> List[str]:
    short_name = str(meta.get("short_name", meta["name"]))
    red_label = "Red Crescent" if meta.get("region") in {"middle_east", "north_africa"} else "Red Cross"
    base_orgs = [
        f"WFP {short_name}",
        f"UNICEF {short_name}",
        "Save the Children",
        f"{short_name} {red_label}",
        f"{short_name} Social Protection Agency",
        f"{short_name} Community Relief",
    ]
    extras: List[str] = meta.get("extra_organizations", [])
    for extra in extras:
        if extra not in base_orgs:
            base_orgs.append(extra)
    while len(base_orgs) < 8:
        candidate = fake.company()
        if candidate not in base_orgs:
            base_orgs.append(candidate)
    return base_orgs[:8]


def _build_settlements(meta: Dict[str, Any], fake: Faker, rng: random.Random) -> List[str]:
    settlements = _unique_values(fake.city, rng, 6)
    templates: List[str] = meta.get("settlement_templates", [])
    for template in templates:
        if template not in settlements:
            settlements.append(template)
    return settlements[:6]


def _build_geopoints(meta: Dict[str, Any], defaults: Dict[str, Any], rng: random.Random, count: int = 200) -> List[Tuple[float, float]]:
    preset: List[List[float]] = meta.get("preset_geopoints", [])
    points: List[Tuple[float, float]] = []
    
    if preset:
        preset_tuples = [(p[0], p[1]) for p in preset]
        while len(points) < count:
            base_lat, base_lon = rng.choice(preset_tuples)
            lat = max(-90.0, min(90.0, base_lat + rng.uniform(-0.3, 0.3)))
            lon = _wrap_longitude(base_lon + rng.uniform(-0.3, 0.3))
            points.append((lat, lon))
        return points[:count]

    faker_geo = Faker()
    faker_geo.seed_instance(rng.randint(0, 2**31 - 1))
    iso2: Optional[str] = meta.get("iso2")
    bounds = meta.get("geo_bounds") or defaults.get("geo_bounds", {"lat": [-90, 90], "lon": [-180, 180]})
    lat_bounds = bounds["lat"]
    lon_bounds = bounds["lon"]

    attempts = 0
    while len(points) < count and attempts < count * 20:
        latlon = None
        if iso2:
            latlon = faker_geo.local_latlng(iso2, coords_only=True)
        if latlon:
            lat, lon = float(latlon[0]), float(latlon[1])
        else:
            lat = rng.uniform(lat_bounds[0], lat_bounds[1])
            lon = rng.uniform(lon_bounds[0], lon_bounds[1])
        lat = max(-90.0, min(90.0, lat))
        lon = _wrap_longitude(lon)
        points.append((lat, lon))
        attempts += 1

    if not points:
        lat = rng.uniform(lat_bounds[0], lat_bounds[1])
        lon = rng.uniform(lon_bounds[0], lon_bounds[1])
        points.append((lat, _wrap_longitude(lon)))

    rng.shuffle(points)
    return points[:count]


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def build_country_profile(country: str, rng: random.Random) -> CountryProfile:
    """
    Build a CountryProfile for the given country.
    
    Args:
        country: Country name (must match key in countries section of YAML)
        rng: Random number generator for reproducibility
    
    Returns:
        CountryProfile instance
    
    Raises:
        KeyError: If country is not found in configuration
    """
    country_metadata = _get_country_metadata()
    region_defaults = _get_region_defaults()
    
    meta = country_metadata.get(country)
    if not meta:
        raise KeyError(f"Country '{country}' is not registered in configuration")

    region = meta["region"]
    defaults = region_defaults.get(region, {})
    
    locales: List[str] = meta.get("locales", [])
    if not locales:
        locales = ["en_GB"]

    fake = Faker(locales)
    fake.seed_instance(rng.randint(0, 2**31 - 1))

    enumerators = _unique_values(fake.name, rng, 8)
    supervisors = _unique_values(fake.name, rng, 3)
    organizations = _build_organizations(meta, fake, rng)
    settlements = _build_settlements(meta, fake, rng)

    administrative = {
        "ADM0": [meta.get("short_name", meta["name"])],
        "ADM1": _location_values(fake, rng, 8, ["state", "prefecture", "province"]),
        "ADM2": _location_values(fake, rng, 8, ["city", "town", "county"]),
        "ADM3": _location_values(fake, rng, 8, ["city", "town", "municipality"]),
        "ADM4": _location_values(fake, rng, 8, ["street_name", "secondary_address", "city_suffix"]),
        "ADM5": _generate_small_units(fake, rng, 8),
    }

    overrides: Dict[str, List[str]] = meta.get("administrative_overrides", {})
    for level, values in overrides.items():
        administrative[level] = list(values)

    # Get values with fallback to region defaults
    household_range = meta.get("household_size_range") or defaults.get("household_size_range", [3, 7])
    
    expense_defaults = defaults.get("expense", {})
    expense = ExpenseParameters(
        base_mean=float(meta.get("expense_mean", expense_defaults.get("base_mean", 5000))),
        base_std=float(meta.get("expense_std", expense_defaults.get("base_std", 2000))),
        min_value=float(meta.get("expense_min", expense_defaults.get("min_value", 500))),
        decay_range=tuple(meta.get("expense_decay", expense_defaults.get("decay_range", [0.05, 0.10]))),
        scale=float(meta.get("expense_scale", expense_defaults.get("scale", 1.0))),
    )

    fcs_base = tuple(meta.get("fcs_base_range", defaults.get("fcs_base_range", [1.7, 3.7])))
    fcs_improve = tuple(meta.get("fcs_improve_range", defaults.get("fcs_improve_range", [0.22, 0.48])))
    yesno_adjust = float(meta.get("yesno_adjust", defaults.get("yesno_adjust", 0.0)))
    altitude_base = float(meta.get("altitude_base", defaults.get("altitude_base", 100.0)))
    altitude_variation = float(meta.get("altitude_variation", defaults.get("altitude_variation", 400.0)))
    accuracy_range = tuple(meta.get("accuracy_range", defaults.get("accuracy_range", [3.5, 9.0])))

    geopoints = _build_geopoints(meta, defaults, rng)

    return CountryProfile(
        name=meta["name"],
        iso2=meta.get("iso2"),
        locales=locales,
        timezone=str(meta["timezone"]),
        currency=str(meta["currency"]),
        region=str(meta["region"]),
        enumerators=enumerators,
        supervisors=supervisors,
        organizations=organizations,
        settlements=settlements,
        administrative=administrative,
        household_size_range=tuple(household_range),
        expense=expense,
        fcs_base_range=fcs_base,
        fcs_improve_range=fcs_improve,
        yesno_adjust=yesno_adjust,
        geopoints=geopoints,
        altitude_base=altitude_base,
        altitude_variation=altitude_variation,
        accuracy_range=accuracy_range,
    )
