
import random
import datetime
from collections import Counter, OrderedDict
from typing import Dict, Any, List

# Integration of legacy logic
from profiles import build_country_profile, CountryProfile
from rules import evaluate_relevant, satisfies_constraint
from config_loader import get_config

# Modular simulation components
from simulation import (
    calculate_enhanced_impact,
    calculate_temporal_impact,
    calculate_severity_score,
    calculate_physical_destruction_prob,
    calculate_assistance_probability,
    check_displacement,
    check_health_impact,
    calculate_economic_shock,
)

class Simulator:
    # Field definitions loaded from config
    _config = None
    
    @classmethod
    def _get_config(cls):
        if cls._config is None:
            cls._config = get_config()
        return cls._config

    def __init__(self, odk_structure, context_events=None, country_name=None, simulation_start_year=2020):
        self.survey = odk_structure.get('survey', [])
        self.choices = odk_structure.get('choices', {})
        self.context_events = context_events or []
        self.rng = random.Random(42) # Fixed seed for reproducibility
        self.simulation_start_year = simulation_start_year
        self.config = self._get_config()
        
        # Identify country - store the REQUESTED country name
        if country_name:
            self.country_name = country_name
        else:
            self.country_name = self._infer_country(context_events)
        
        # Load Field definitions from config
        self.FCS_FIELDS = set(self.config.get_fcs_fields())
        self.RCSI_FIELDS = set(self.config.get_rcsi_fields()) 
        
        # Flag to track if we're using a fallback profile
        self._use_fallback_profile = False
        
        try:
            self.profile = build_country_profile(self.country_name, self.rng)
            self.profile_country = self.profile.name
        except Exception as e:
            print(f"Warning: Country {self.country_name} not found in profiles. Using fallback with Faker geopoints.")
            self.profile = build_country_profile("Colombia", self.rng)
            self.profile_country = self.country_name  # Keep original country name
            self._use_fallback_profile = True  # Flag to use Faker for geopoints
    
    # Common country name to ISO2 mapping for Faker (countries without profiles)
    COUNTRY_ISO2_MAP = {
        # Americas
        'Argentina': 'AR', 'Bahamas': 'BS', 'Barbados': 'BB', 'Belize': 'BZ',
        'Brazil': 'BR', 'Canada': 'CA', 'Chile': 'CL', 'Costa Rica': 'CR',
        'Dominica': 'DM', 'Grenada': 'GD', 'Guyana': 'GY', 'Jamaica': 'JM',
        'Mexico': 'MX', 'Panama': 'PA', 'Paraguay': 'PY', 'Suriname': 'SR',
        'Trinidad and Tobago': 'TT', 'Uruguay': 'UY',
        'United States of America': 'US', 'United States': 'US', 'USA': 'US',
        'Venezuela (Bolivarian Republic of)': 'VE',
        # Europe
        'Albania': 'AL', 'Austria': 'AT', 'Belarus': 'BY', 'Belgium': 'BE',
        'Bosnia and Herzegovina': 'BA', 'Bulgaria': 'BG', 'Croatia': 'HR',
        'Cyprus': 'CY', 'Czechia': 'CZ', 'Denmark': 'DK', 'Estonia': 'EE',
        'Finland': 'FI', 'France': 'FR', 'Germany': 'DE', 'Greece': 'GR',
        'Hungary': 'HU', 'Iceland': 'IS', 'Ireland': 'IE', 'Italy': 'IT',
        'Latvia': 'LV', 'Lithuania': 'LT', 'Luxembourg': 'LU', 'Malta': 'MT',
        'Montenegro': 'ME', 'Netherlands (Kingdom of the)': 'NL', 'North Macedonia': 'MK',
        'Norway': 'NO', 'Poland': 'PL', 'Portugal': 'PT', 'Romania': 'RO',
        'Russian Federation': 'RU', 'Russia': 'RU', 'Serbia': 'RS', 'Slovakia': 'SK',
        'Slovenia': 'SI', 'Spain': 'ES', 'Sweden': 'SE', 'Switzerland': 'CH',
        'Türkiye': 'TR', 'United Kingdom of Great Britain and Northern Ireland': 'GB', 'United Kingdom': 'GB',
        # Asia
        'Azerbaijan': 'AZ', 'Georgia': 'GE', 'Iran (Islamic Republic of)': 'IR',
        'Israel': 'IL', 'Japan': 'JP', 'Kazakhstan': 'KZ', 'Kuwait': 'KW',
        'Kyrgyzstan': 'KG', 'Malaysia': 'MY', 'Maldives': 'MV', 'Mongolia': 'MN',
        'Oman': 'OM', 'Qatar': 'QA', 'Republic of Korea': 'KR', 'Saudi Arabia': 'SA',
        'Singapore': 'SG', 'Taiwan (Province of China)': 'TW', 'Thailand': 'TH',
        'Turkmenistan': 'TM', 'United Arab Emirates': 'AE', 'Uzbekistan': 'UZ', 'Viet Nam': 'VN',
        'China': 'CN', 'India': 'IN',
        # Oceania
        'Australia': 'AU', 'Fiji': 'FJ', 'New Zealand': 'NZ', 'Papua New Guinea': 'PG',
        'Samoa': 'WS', 'Solomon Islands': 'SB', 'Tonga': 'TO', 'Vanuatu': 'VU',
        # Africa
        'Botswana': 'BW', 'Cabo Verde': 'CV', 'Comoros': 'KM', 'Côte d\'Ivoire': 'CI',
        'Equatorial Guinea': 'GQ', 'Eritrea': 'ER', 'Gabon': 'GA', 'Mauritius': 'MU',
        'Morocco': 'MA', 'Seychelles': 'SC', 'South Africa': 'ZA',
        # Others with special names
        'Republic of Moldova': 'MD',
    }

    def _infer_country(self, context_events):
        if context_events and len(context_events) > 0:
            first = context_events[0]
            return first.get('Country') or "Colombia"
        return "Colombia"

    def simulate(self, count=1, fixed_year=None):
        results = []
        
        # Analyze context for disasters by year
        disasters_by_year = self._analyze_disasters_by_year()
        
        for i in range(count):
            # Determine Year
            if fixed_year:
                year = fixed_year
            else:
                 # Assign a random year for this response (favors years present in context)
                if disasters_by_year and self.rng.random() < 0.8:
                     year = self._pick_year(disasters_by_year)
                else:
                     year = self.rng.randint(2020, 2024)

            # LONGITUDINAL TRACKING: Create a deterministic seed for this household
            # This ensures "Household i" is always the same entity across years/runs
            household_id = f"{self.country_name}_HH_{i:04d}"
            hh_seed = f"{household_id}_static"
            hh_rng = random.Random(hh_seed)
            
            # Household level context (Static traits generated with hh_rng)
            # Pass custom rng to profile generator to ensure consistency
            hh_context = self.profile.generate_household_profile(rng=hh_rng)
            
            # Add System/Simulation Context
            hh_context["__year__"] = year
            hh_context["__household_id__"] = household_id
            hh_context["__household_code__"] = f"HH-{i:04d}"
            
            # Temporal Progression Factors
            # Calculate index relative to the simulation start (baseline)
            year_idx = year - self.simulation_start_year
            hh_context["__year_index__"] = max(0, year_idx)
            
            # Pre-generate ADMIN1 to allow filtering (Static location)
            if self.profile.administrative.get('ADM1'):
                # Location should be static for the household -> use hh_rng
                admin1 = hh_rng.choice(self.profile.administrative['ADM1'])
                hh_context["__admin1__"] = admin1
                hh_context["ADMIN1"] = admin1 
            
            # Generate one row
            row = self._generate_single_response(hh_context, i)
            results.append(row)
            
        return results

    def _analyze_disasters_by_year(self):
        """Map year -> list of event objects"""
        years = {}
        for event in self.context_events:
            # Try to parse Year
            y = event.get('Start Year') or event.get('Year')
            if y:
                try:
                    y_int = int(y)
                    if y_int not in years:
                        years[y_int] = []
                    years[y_int].append(event)
                except:
                    pass
        return years

    def _pick_year(self, disasters_by_year):
        # If we have context years, pick one of them, otherwise current year
        if disasters_by_year:
            available_years = list(disasters_by_year.keys())
            return self.rng.choice(available_years)
        return datetime.date.today().year

    def _progress_factor(self, context: Dict[str, Any]) -> float:
        """
        Calculate progression factor based on 4-year cycle.
        0.0 = Baseline (Worst)
        1.0 = Max Improvement (Best)
        Values loaded from config/simulation_params.yaml
        """
        idx = context.get("__year_index__", 0)
        return self.config.get_progression_value(idx)

    def _generate_single_response(self, context, hh_index):
        # Use OrderedDict to preserve survey field order in output
        data = OrderedDict()
        
        year = context["__year__"]
        
        # YEAR-SPECIFIC RNG: Seed = HouseholdID + Year
        # This ensures year-specific variations (like expenses) are consistent but different from other years
        step_seed = f"{context['__household_id__']}_{year}"
        self.rng = random.Random(step_seed)
        
        # --- PHASE 4 IMPL: PROGRESSION LOGIC ---
        progression = self._progress_factor(context)
        context["__progression__"] = progression
        
        current_year_events = [e for e in self.context_events if e.get('Start Year') == year]
        
        household_admin1 = context.get("__admin1__")
        
        # PHASE 1: Enhanced impact calculation
        from datetime import datetime
        survey_date = datetime(year, 6, 15)  # Mid-year survey
        context["__survey_date__"] = survey_date
        
        disaster_impact = 0.0
        disaster_types = set()
        disaster_subtypes = set()  # PHASE 1: Track subtypes
        filtered_events = []  # Store filtered events for later use
        
        for event in current_year_events:
            # Regional Filtering - RELAXED to avoid ADM1 mismatch issues
            # EM-DAT uses department names (Antioquia) but profile may use municipality names (Mutatá)
            # Instead of strict filtering, we include all events for the country
            # and apply probability-based impact
            affects_region = True  # Always include country-level events
            
            # Optional: Apply reduced impact if admin unit doesn't match
            # This preserves some locality while not excluding events entirely
            impact_reduction = 1.0
            if household_admin1 and event.get('Admin Units'):
                affected_names = []
                for u in event['Admin Units']:
                    affected_names.append(u.get('adm1_name', '').upper())
                    affected_names.append(u.get('adm2_name', '').upper())
                
                if household_admin1.upper() not in affected_names:
                    # Event affects different region - reduce impact but don't exclude
                    impact_reduction = 0.3  # 30% of full impact for non-local events
            
            if affects_region:
                filtered_events.append(event)
                
                # PHASE 1: Enhanced impact calculation
                impact = calculate_enhanced_impact(event, survey_date, self.config)
                disaster_impact += impact
                
                # Store types for narrative consistency
                dtype = event.get('Disaster Type')
                if dtype:
                    disaster_types.add(dtype)
                
                # PHASE 1: Store subtypes (more specific)
                subtype = event.get('disaster_subtype')
                if subtype:
                    disaster_subtypes.add(subtype)
        
        context["__disaster_types__"] = list(disaster_types)
        context["__disaster_subtypes__"] = list(disaster_subtypes)  # PHASE 1
        context["__disaster_impact__"] = disaster_impact
        context["__filtered_events__"] = filtered_events  # For later phases
        
        # PHASE 3: Economic Shock
        economic_shock = calculate_economic_shock(filtered_events)
        context["__economic_shock__"] = economic_shock

        # --- PHASE 4 IMPL: EXPENDITURE MODULE ---
        # Calculate Detailed Expenditures (Food vs Non-Food)
        # Logic: Food Share starts high (70% in baseline) and reduces by ~10% per year of success
        
        # Base Total Expenditure (Randomized by wealth)
        wealth_q = context.get("__wealth_quintile__", 3)
        base_exp = self.profile.expense.base_mean * (0.5 + (wealth_q * 0.2)) # increasing with wealth
        base_exp *= (0.8 + (self.rng.random() * 0.4)) # +/- 20% random variation
        
        # Adjust Total Exp by Shock
        total_exp = base_exp * (1.0 - (disaster_impact * 0.2)) 
        
        # Food Share Calculation
        # Baseline: ~70% (0.7)
        # Year 1 (Progression 0.6): 60%
        # Year 2 (Progression 0.9): 50%
        base_food_share = 0.75 - (context["__progression__"] * 0.25) # 0.75 -> 0.50
        base_food_share = max(0.3, min(0.9, base_food_share))
        
        # Add random variation to share
        food_share = base_food_share + self.rng.gauss(0, 0.05)
        food_share = max(0.2, min(0.95, food_share))
        
        food_exp = total_exp * food_share
        non_food_exp = total_exp * (1.0 - food_share)
        
        context["__total_exp__"] = total_exp
        context["__food_exp__"] = food_exp
        context["__non_food_exp__"] = non_food_exp
        context["__food_share__"] = food_share

        # PHASE 4: Hyper-Realism Aggregation
        # Collect narrative details
        event_names = [e.get('event_name') for e in filtered_events if e.get('event_name')]
        origins = [e.get('origin_desc') for e in filtered_events if e.get('origin_desc')]
        shortages = set()
        for e in filtered_events:
            for s in e.get('associated_shortages', []):
                shortages.add(s)
        
        context["__event_names__"] = list(set(event_names))
        context["__origins__"] = list(set(origins))
        context["__shortages__"] = list(shortages)
        
        # Calculate Physical Destruction Probability (Hyper-Realism)
        context["__physical_destruction_prob__"] = calculate_physical_destruction_prob(filtered_events, self.config)
        
        # Store internal fields temporarily - will add at end to preserve ODK survey order
        internal_fields = OrderedDict()
        
        # Add summary of events to internal fields
        if event_names:
            internal_fields["_events_summary"] = ", ".join(event_names)
        else:
            internal_fields["_events_summary"] = "None"
            
        # ENSURE LAT/LON FOR MAP
        # Generate country-specific coordinates with multi-tier priority
        lat, lon = 0, 0
        
        # PRIORITY 1: Use actual disaster coordinates from EM-DAT context
        # This provides the most accurate location (near the actual disaster site)
        if filtered_events:
            # Collect all valid coordinates from events affecting this household
            event_coords = []
            for event in filtered_events:
                e_lat = event.get('latitude')
                e_lon = event.get('longitude')
                if e_lat is not None and e_lon is not None:
                    try:
                        event_coords.append((float(e_lat), float(e_lon)))
                    except:
                        pass
            
            if event_coords:
                # Pick a random disaster location from those affecting this household
                lat, lon = self.rng.choice(event_coords)
                # Add significant variation (±50km approx) to simulate household spread around disaster
                lat += self.rng.uniform(-0.5, 0.5)
                lon += self.rng.uniform(-0.5, 0.5)
        
        # PRIORITY 2: Use profile geopoints ONLY if not using fallback profile
        # (fallback profile has Colombia's geopoints, not the actual country's)
        if lat == 0 and lon == 0 and self.profile.geopoints and not self._use_fallback_profile:
            lat, lon = self.profile.geopoints[self.rng.randint(0, len(self.profile.geopoints)-1)]
            lat += self.rng.uniform(-0.1, 0.1)
            lon += self.rng.uniform(-0.1, 0.1)
        
        # PRIORITY 3: Use Faker to generate country-specific coordinates
        if lat == 0 and lon == 0:
            try:
                from faker import Faker
                fake_geo = Faker()
                
                # First try our ISO2 mapping
                iso2 = self.COUNTRY_ISO2_MAP.get(self.country_name)
                
                # If not in mapping, try profile.iso2 (only valid if not fallback)
                if not iso2 and not self._use_fallback_profile:
                    iso2 = self.profile.iso2
                
                latlon = None
                if iso2:
                    latlon = fake_geo.local_latlng(country_code=iso2, coords_only=True)
                
                if not latlon:
                    # Try by country name directly
                    latlon = fake_geo.local_latlng(country=self.country_name, coords_only=True)
                
                if latlon:
                    lat, lon = float(latlon[0]), float(latlon[1])
                    lat += self.rng.uniform(-0.5, 0.5)
                    lon += self.rng.uniform(-0.5, 0.5)
                else:
                    raise ValueError("Faker couldn't find country")
                    
            except Exception as e:
                # PRIORITY 4: Ultimate fallback (should rarely happen)
                print(f"Warning: Could not generate geopoint for {self.country_name}: {e}. Using default.")
                lat, lon = 4.5709 + self.rng.uniform(-2, 2), -74.2973 + self.rng.uniform(-2, 2)
        
        # Store coordinates in internal fields (will be added at end)
        internal_fields["latitude"] = str(lat)
        internal_fields["longitude"] = str(lon)
        internal_fields["_Geopoint_value"] = f"{lat} {lon} 0 0"
            
        # Context for relevance: start with household context, update with answers as we go
        relevance_context = context.copy()

        for q in self.survey:
            q_type = q.get('type')
            q_name = q.get('name')
            
            if not q_type or not q_name:
                continue

            # Groups handling (simplified)
            if q_type == 'begin_group' or q_type == 'end_group':
                continue
            
            # Check Relevance - for simulation, ALWAYS include fields but use defaults when not relevant
            relevant_expr = q.get('relevant')
            is_relevant = True
            if relevant_expr:
                is_relevant = evaluate_relevant(relevant_expr, relevance_context)
            
            # If not relevant, set appropriate default value
            if not is_relevant:
                # Default values based on type
                if q_type in ('integer', 'decimal'):
                    val = 0
                elif q_type == 'calculate':
                    val = 0
                elif q_type == 'text':
                    val = ''
                elif q_type.startswith('select_'):
                    val = ''  # Empty selection
                else:
                    val = None
                
                data[q_name] = val
                relevance_context[q_name] = val
                continue  # Move to next field

            # Constraint Validation Loop
            val = None
            constraint_expr = q.get('constraint')
            max_retries = 10
            
            for attempt in range(max_retries):
                # Specialized Generation Logic
                if q_name in self.FCS_FIELDS:
                    val = self._gen_fcs(q_name, context, disaster_impact)
                    
                # 2. rCSI Fields
                elif q_name in self.RCSI_FIELDS:
                    val = self._gen_rcsi(q_name, context, disaster_impact)
                    
                # 3. Expenses/Numeric generic
                elif q_type in ('integer', 'decimal'):
                     val = self._gen_numeric(q, context, disaster_impact)
                     
                # 4. Standard types (pass relevance_context for calculate fields to access generated values)
                else:
                    val = self._generate_generic(q, relevance_context, disaster_impact)
                
                # Check Constraint
                if not constraint_expr:
                    break
                
                if satisfies_constraint(val, constraint_expr):
                    break
                # If constraint failed, loop again to retry
            
            data[q_name] = val
            relevance_context[q_name] = val
            
        # --- Calculated Fields Injection ---
        # Ensure HHSFr exists for Dashboard
        if "HHSFr" not in data:
            # Check for HHS components
            hhs_vals = []
            for k in ["HHSNoFood", "HHSBedHung", "HHSNotEat"]:
                v = data.get(k)
                # Assume 0=No, 1=Rarely, 2=Sometimes, 3=Often (or similar numeric scale)
                # Or if values are strings/None, try to parse
                try:
                    if v is not None:
                        hhs_vals.append(int(v))
                except:
                    pass
            
            if hhs_vals:
                # Logic: Take the maximum severity
                max_val = max(hhs_vals) if hhs_vals else 0
                
                if max_val >= 3:
                     data["HHSFr"] = "Often"
                elif max_val == 2:
                     data["HHSFr"] = "Sometimes"
                elif max_val == 1:
                     data["HHSFr"] = "Rarely"
                else:
                     data["HHSFr"] = "No"
            else:
                data["HHSFr"] = "No" # Default if missing
        
        # Add internal/metadata fields at the END to preserve ODK survey order
        # Survey questions come first, then our generated metadata
        data.update(internal_fields)
                
        return data

    def _gen_fcs(self, field_name, context, impact):
        base_min, base_max = self.profile.fcs_base_range
        improve_min, improve_max = self.profile.fcs_improve_range
        progression = context.get("__progression__", 0.0)
        
        base = self.rng.uniform(base_min, base_max)
        
        # IMPROVEMENT logic:
        # Instead of linear year index, use the S-curve progression
        # Max improvement added to base score
        improvement_boost = progression * 25.0 # Max +25 FCS points by year 3/4
        
        # Specific field tweaks
        boost = 0
        if "Stap" in field_name: boost = 3
        if "Sugar" in field_name: boost = 0.5
        
        raw_val = (base + boost) + (improve_min * progression * 5) - impact
        
        # If we are in Year 2+ (progression > 0.5), boost values significantly to reflect "Assistance"
        if progression > 0.5:
             # Make diet more diverse
             raw_val += 1.5
             
        # Clamp to 0-7 days
        val = int(round(max(0, min(7, raw_val + self.rng.gauss(0, 0.5)))))
        return val

    def _gen_rcsi(self, field_name, context, impact):
        progression = context.get("__progression__", 0.0)
        
        # Baseline start (High rCSI = Bad)
        start = self.rng.uniform(2.0, 5.0) 
        
        # Decay (Improvement) -> rCSI should go down
        # Max reduction of ~3.0 points
        reduction = progression * 3.5 
        
        raw_val = start - reduction + impact
        val = int(round(max(0, min(7, raw_val + self.rng.gauss(0, 1.0)))))
        return val

    def _parse_constraint_range(self, constraint):
        """Parse ODK constraint string to extract min/max values.
        Examples: '. >= 0 and . < 11' -> (0, 10)
                  '. >= 0 and .<= 25' -> (0, 25)
        """
        if not constraint or str(constraint).lower() == 'nan':
            return None, None
        
        constraint = str(constraint)
        min_val, max_val = None, None
        
        # Parse minimum: ">=" or ">"
        import re
        ge_match = re.search(r'\.\s*>=\s*(\d+(?:\.\d+)?)', constraint)
        gt_match = re.search(r'\.\s*>\s*(\d+(?:\.\d+)?)', constraint)
        
        if ge_match:
            min_val = float(ge_match.group(1))
        elif gt_match:
            min_val = float(gt_match.group(1)) + 1
        
        # Parse maximum: "<=" or "<"
        le_match = re.search(r'\.\s*<=\s*(\d+(?:\.\d+)?)', constraint)
        lt_match = re.search(r'\.\s*<\s*(\d+(?:\.\d+)?)', constraint)
        
        if le_match:
            max_val = float(le_match.group(1))
        elif lt_match:
            max_val = float(lt_match.group(1)) - 1
        
        return min_val, max_val

    def _gen_numeric(self, question, context, impact):
        q_type = question.get('type')
        q_name = question.get('name')
        constraint = question.get('constraint')
        
        # Climate shock impact count fields
        climate_count_fields = {
            # Floods
            'HHLowFloods': ('Flood', 'low'),
            'HHMedFloods': ('Flood', 'med'),
            'HHHighFloods': ('Flood', 'high'),
            # Droughts
            'HHLowDroughts': ('Drought', 'low'),
            'HHMedDroughts': ('Drought', 'med'),
            'HHHighDroughts': ('Drought', 'high'),
            # Storms
            'HHLowStorms': ('Storm', 'low'),
            'HHMedStorms': ('Storm', 'med'),
            'HHHighStorms': ('Storm', 'high'),
            # Heat Wave
            'HHLowHeatWave': ('Extreme temperature', 'low'),
            'HHMedHeatWave': ('Extreme temperature', 'med'),
            'HHHighHeatWave': ('Extreme temperature', 'high'),
            # Wildfire
            'HHLowWildFire': ('Wildfire', 'low'),
            'HHMedWildFire': ('Wildfire', 'med'),
            'HHHighWildFire': ('Wildfire', 'high'),
        }
        
        if q_name in climate_count_fields:
            disaster_type, severity = climate_count_fields[q_name]
            disaster_types = context.get("__disaster_types__", [])
            disaster_impact = context.get("__disaster_impact__", 0)
            
            # Check if affected by this disaster type
            is_affected = any(disaster_type.lower() in dt.lower() for dt in disaster_types)
            
            if not is_affected:
                return 0  # Not affected by this type
            
            # Parse constraint (typically `. >= 0 and . < 11`)
            min_val, max_val = self._parse_constraint_range(constraint)
            if max_val is None:
                max_val = 10
            
            # Generate count based on severity level and impact
            # Constraint: total across all levels should be reasonable (1-10 events typically)
            if severity == 'low':
                # Low severity more common in mild disasters
                if disaster_impact < 1.0:
                    max_count = min(3, int(max_val))
                else:
                    max_count = min(2, int(max_val))
            elif severity == 'med':
                # Medium severity
                if disaster_impact < 1.5:
                    max_count = min(2, int(max_val))
                else:
                    max_count = min(3, int(max_val))
            else:  # high
                # High severity more common in severe disasters
                if disaster_impact < 2.0:
                    max_count = min(1, int(max_val))
                else:
                    max_count = min(4, int(max_val))
            
            return self.rng.randint(0, max_count)
        
        if self._is_expense(q_name):
            return self._gen_expense(q_name, context, impact, constraint)

        # Parse constraint to get valid range
        min_val, max_val = self._parse_constraint_range(constraint)
        
        # Apply defaults if not specified
        if min_val is None:
            min_val = 0
        if max_val is None:
            max_val = 100
        
        if q_type == 'integer':
            return self.rng.randint(int(min_val), int(max_val))
        else:
            return round(self.rng.uniform(min_val, max_val), 2)

    def _is_expense(self, name):
         name_lower = name.lower()
         return 'exp' in name_lower or 'cost' in name_lower or 'spend' in name_lower or 'purch' in name_lower

    def _gen_expense(self, name, context, impact, constraint=None):
        """Generate expense value respecting ODK constraint.
        Most expense fields have constraint '. >= 0 and .<= 25' (millions in local currency).
        """
        name_lower = name.lower()
        
        # Parse constraint to get valid range
        min_val, max_val = self._parse_constraint_range(constraint)
        
        # Apply defaults based on typical constraints
        if min_val is None:
            min_val = 0
        if max_val is None:
            max_val = 25  # Default for most expense fields
        
        # Generate value within constraint range
        # Use progression to influence spending patterns
        progression = context.get("__progression__", 0)
        
        # Base value: lower in crisis (baseline), higher later
        base_fraction = 0.3 + (progression * 0.4)  # 0.3 to 0.7 of max
        
        # Add some randomness
        value = max_val * base_fraction * self.rng.uniform(0.5, 1.5)
        
        # Apply disaster impact (reduces spending capacity)
        if impact > 0:
            # Fix: Clamp impact effect to max 90% reduction to avoid 0 or negative values
            # impacts can be high (>5.0) when multiple events accumulate
            impact_factor = min(0.9, impact * 0.15) 
            value = value * (1.0 - impact_factor)
        
        # Clamp to constraint range
        value = max(min_val, min(max_val, value))
        
        return round(value, 2)

    def _generate_generic(self, question, context, impact):
        q_type = question.get('type')
        q_name = question.get('name')
        
        if q_type.startswith('select_one'):
            return self._pick_option(question, q_name, context, impact)
            
        if q_type.startswith('select_multiple'):
            return self._pick_multiple(question, context)
            
        if q_type == 'date':
             year = context["__year__"]
             month = self.rng.randint(1, 12)
             day = self.rng.randint(1, 28)
             return f"{year}-{month:02d}-{day:02d}"
             
        if q_type == 'geopoint':
            lat, lon = self.profile.geopoints[self.rng.randint(0, len(self.profile.geopoints)-1)]
            lat += self.rng.uniform(-0.01, 0.01)
            lon += self.rng.uniform(-0.01, 0.01)
            return f"{lat:.6f} {lon:.6f} 0 0"

        if q_type == 'text':
             # Geographic fields - map to administrative levels
             if q_name == 'Country':
                 # Return the REQUESTED country, not the profile's country
                 return self.country_name
             if q_name == 'State_province':
                 return context.get('__admin1__', 'Unknown Province')
             if q_name == 'City':
                 return context.get('__admin2__', 'Unknown City')
             
             # Country ISO code
             if q_name == 'country_iso' and self.profile.iso2:
                 return self.profile.iso2
             
             # PHASE 4: Narrative Injection (High Priority)
             # If we have specific event names or origins, prioritize them
             event_names = context.get("__event_names__", [])
             origins = context.get("__origins__", [])
             
             if (event_names or origins) and ("comment" in q_name.lower() or "free" in q_name.lower() or "description" in q_name.lower()):
                 narrative_parts = []
                 if event_names:
                     narrative_parts.append(f"We were hit by {self.rng.choice(event_names)}.")
                 if origins:
                     narrative_parts.append(f"The trouble started with {self.rng.choice(origins).lower()}.")
                 
                 # Add shortage context
                 shortages = context.get("__shortages__", [])
                 if shortages:
                     s = self.rng.choice(shortages)
                     if "food" in s.lower():
                         narrative_parts.append("We have no food left.")
                     elif "water" in s.lower():
                         narrative_parts.append("Clean water is impossible to find.")
                 
                 if narrative_parts:
                     return " ".join(narrative_parts)

             # Contextual comments based on food security
             if q_name in ['Comments', 'FreeResp']:
                 # Calculate approximate FCS from context if available
                 fcs_estimate = context.get('__fcs_estimate__', 35)
                 if fcs_estimate < 21:
                     comments = [
                         "Food situation is very difficult for the household",
                         "Struggling significantly to meet basic food needs",
                         "Severe food insecurity affecting daily life"
                     ]
                 elif fcs_estimate < 35:
                     comments = [
                         "Food situation is challenging but manageable",
                         "Some difficulties in accessing adequate food",
                         "Moderate food insecurity reported"
                     ]
                 else:
                     comments = [
                         "Food situation is generally acceptable",
                         "Household can meet basic food needs",
                         "Food security is stable"
                     ]
                 return self.rng.choice(comments)
             
             # Shock/disaster type injection
             disaster_types = context.get("__disaster_types__", [])
             if disaster_types and ("shock" in q_name.lower() or "disaster" in q_name.lower() or "type" in q_name.lower()):
                 return ", ".join(disaster_types)
                 
             return "Simulated Text"
             
        # Handle calculate fields (climate shock totals, etc.)
        if q_type == 'calculate':
            # Calculate fields use the relevance_context which has all generated values
            calculate_map = {
                'TotalFloods': ['HHLowFloods', 'HHMedFloods', 'HHHighFloods'],
                'TotalDroughts': ['HHLowDroughts', 'HHMedDroughts', 'HHHighDroughts'],
                'TotalStorms': ['HHLowStorms', 'HHMedStorms', 'HHHighStorms'],
                'TotalHeatWave': ['HHLowHeatWave', 'HHMedHeatWave', 'HHHighHeatWave'],
                'TotalWildFire': ['HHLowWildFire', 'HHMedWildFire', 'HHHighWildFire'],
                'TotalLowLevel': ['HHLowFloods', 'HHLowDroughts', 'HHLowStorms', 'HHLowHeatWave', 'HHLowWildFire'],
                'TotalMediumLevel': ['HHMedFloods', 'HHMedDroughts', 'HHMedStorms', 'HHMedHeatWave', 'HHMedWildFire'],
                'TotalHighLevel': ['HHHighFloods', 'HHHighDroughts', 'HHHighStorms', 'HHHighHeatWave', 'HHHighWildFire'],
            }
            
            if q_name in calculate_map:
                component_fields = calculate_map[q_name]
                total = 0
                for f in component_fields:
                    val = context.get(f)
                    if val is not None:
                        try:
                            total += int(val)
                        except:
                            pass
                return total
            
            elif q_name == 'TotalShocks':
                total_fields = ['TotalFloods', 'TotalDroughts', 'TotalStorms', 'TotalHeatWave', 'TotalWildFire']
                total = 0
                for f in total_fields:
                    val = context.get(f)
                    if val is not None:
                        try:
                            total += int(val)
                        except:
                            pass
                return total
            
            return None
             
        return None

    def _pick_option(self, question, q_name, context, impact):
        parts = question.get('type').split()
        if len(parts) <= 1:
            return "choice_1"
            
        list_name = parts[1]
        options = self.choices.get(list_name, [])
        if not options:
            return "choice_1"

        # 1. Enumerators
        if q_name == "EnuName" and self.profile.enumerators:
            return self.rng.choice(self.profile.enumerators) # Return name as value? Or code?
             # Usually standard requires a code, but for this demo simulation we can return the value if code absent
             # But let's check options. If options exist, we pick one randomly but maybe 'label' it?
             # Actually, if the ODK has a list for EnuName, we should pick from it.
             # If it's a 'select_one_external' or similar, we might mock it.
             # Assuming standard select_one. We ignore profile.enumerators if list provided in ODK?
             # Legacy logic: "pool = self.profile.enumerators ... return GeneratedValue(code, label)"
             # We will stick to ODK options if they exist.

        if q_name == "EnuPartner" and self.profile.organizations:
            pass


        # 2. Administrative Levels (ADMIN0-5)
        if q_name.startswith("ADMIN"):
             level = q_name[:6]
             
             # If we pre-generated ADMIN1 in context, use it to ensure consistency with disasters
             if level == "ADMIN1" and context.get("__admin1__"):
                 return context["__admin1__"]

             mapped_key = {"ADMIN0":"ADM0", "ADMIN1":"ADM1", "ADMIN2":"ADM2", "ADMIN3":"ADM3", "ADMIN4":"ADM4", "ADMIN5":"ADM5"}.get(level)
             if mapped_key:
                 possible_names = self.profile.administrative.get(mapped_key, [])
                 if possible_names:
                     return self.rng.choice(possible_names)
                 if possible_names:
                     # Just return a random name from the profile
                     return self.rng.choice(possible_names)
        
        # 3. Special Indicators (LCS, HHS)
        if list_name == "LcsCl":
             # Weights: [0.45, 0.2, 0.3, 0.05] (favors first options - typically "None" or low severity)
             weights = [0.45, 0.2, 0.3, 0.05]
             
             # Adjust for Economic Shock
             shock = context.get("__economic_shock__", 0.0)
             if shock > 0.3:
                 # Shift probability towards higher severity options
                 # Assuming options are ordered: None, Stress, Crisis, Emergency
                 weights = [0.2, 0.3, 0.35, 0.15] # More weight on Crisis/Emergency
             if shock > 0.6:
                 weights = [0.1, 0.2, 0.4, 0.3] # Severe shock
             
             # Trim or extend weights to match options length
             weights = weights[:len(options)]
             if len(weights) < len(options):
                 weights.extend([0.05] * (len(options) - len(weights)))
             
             selected = self.rng.choices(options, weights=weights, k=1)[0]
             # IMPORTANT: Ensure return type is string for consistency
             return str(selected['name'])
             
        if list_name == "HHSFr":
             # HHS Logic per simulated scores.docx:
             # "Solo en el primer año (línea de base) debería haber hogares reportando respuestas afirmativas"
             year_index = context.get("__year_index__", 0)
             
             if year_index == 0:
                 # Baseline Year 1: allow some severity (approx 30% of households)
                 # Weights: [No, Rarely, Sometimes] = [0.70, 0.20, 0.10]
                 weights = [0.70, 0.20, 0.10]
             else:
                 # Follow-up years (2-4): Force "No" - only exception for extreme disasters
                 disaster_impact = context.get("__disaster_impact__", 0)
                 if disaster_impact > 2.5:
                      # Very severe disaster in follow-up year: tiny chance of affirmative
                      weights = [0.97, 0.03, 0.0]
                 else:
                      # Normal follow-up: 100% "No"
                      weights = [1.0, 0.0, 0.0]

             weights = weights[:len(options)]
             if len(weights) < len(options):
                 # Fill rest with 0
                 weights.extend([0.0] * (len(options) - len(weights)))
                 
             selected = self.rng.choices(options, weights=weights, k=1)[0]
             return str(selected['name'])

        # 3.5 Climate Shock Level (CliLevel) - specialized for climate impact assessment
        if list_name == "CliLevel":
            # Options typically: 1=None/Not affected, 2=Low, 3=Medium, 4=High
            disaster_types = context.get("__disaster_types__", [])
            disaster_impact = context.get("__disaster_impact__", 0)
            
            # Map field to disaster type
            field_disaster_map = {
                "HHClimFloods": ["Flood"],
                "HHClimDroughts": ["Drought"],
                "HHStorms": ["Storm", "Cyclone", "Hurricane", "Typhoon"],
                "HHHeatWave": ["Extreme temperature", "Heat wave", "Cold wave"],
                "HHWildFire": ["Wildfire", "Forest fire"]
            }
            
            target_types = field_disaster_map.get(q_name, [])
            is_affected = any(
                any(target.lower() in dt.lower() for target in target_types)
                for dt in disaster_types
            )
            
            if is_affected:
                # Probability weighted by disaster impact
                if disaster_impact > 2.0:
                    weights = [0.05, 0.15, 0.35, 0.45]  # High bias
                elif disaster_impact > 1.0:
                    weights = [0.10, 0.25, 0.40, 0.25]  # Medium bias
                else:
                    weights = [0.20, 0.40, 0.30, 0.10]  # Low bias
            else:
                weights = [0.85, 0.10, 0.04, 0.01]  # Not affected bias
            
            weights = weights[:len(options)]
            if len(weights) < len(options):
                weights.extend([0.01] * (len(options) - len(weights)))
            
            selected = self.rng.choices(options, weights=weights, k=1)[0]
            return str(selected['name'])

        # 3.6 Climate Shock Time (CliShock) - when did the shock occur
        if list_name == "CliShock":
            # Options typically: 1=Within 3 months, 2=3-6 months, 3=6-12 months, 4=>12 months
            disaster_types = context.get("__disaster_types__", [])
            filtered_events = context.get("__filtered_events__", [])
            survey_date = context.get("__survey_date__")
            
            # Map field to disaster type
            field_disaster_map = {
                "HHAffFloods": ["Flood"],
                "HHAffDroughts": ["Drought"],
                "HHAffStorms": ["Storm", "Cyclone", "Hurricane", "Typhoon"],
                "HHAffHeatwaves": ["Extreme temperature", "Heat wave", "Cold wave"],
                "HHAffWildFire": ["Wildfire", "Forest fire"],
                "HHMontAffectedShocks": None  # General - use any disaster
            }
            
            target_types = field_disaster_map.get(q_name)
            
            # Find most recent matching event
            recent_months = None
            if filtered_events and survey_date:
                from datetime import datetime
                for event in filtered_events:
                    event_type = event.get('Disaster Type', '')
                    matches_type = target_types is None or any(
                        t.lower() in event_type.lower() for t in target_types
                    )
                    
                    if matches_type:
                        try:
                            start_year = int(event.get('Start Year', 0))
                            start_month = int(event.get('Start Month', 6))
                            event_date = datetime(start_year, start_month, 15)
                            months_diff = (survey_date.year - event_date.year) * 12 + (survey_date.month - event_date.month)
                            if recent_months is None or months_diff < recent_months:
                                recent_months = months_diff
                        except:
                            pass
            
            if recent_months is not None and recent_months >= 0:
                if recent_months <= 3:
                    weights = [0.75, 0.15, 0.07, 0.03]
                elif recent_months <= 6:
                    weights = [0.10, 0.65, 0.18, 0.07]
                elif recent_months <= 12:
                    weights = [0.05, 0.12, 0.65, 0.18]
                else:
                    weights = [0.03, 0.07, 0.15, 0.75]
            else:
                # No matching event or no context - uniform distribution
                weights = [0.25, 0.25, 0.25, 0.25]
            
            weights = weights[:len(options)]
            if len(weights) < len(options):
                weights.extend([0.1] * (len(options) - len(weights)))
            
            selected = self.rng.choices(options, weights=weights, k=1)[0]
            return str(selected['name'])


        # 4. Yes/No Dynamic Probability
        if list_name == "Yesno":
             # Special case: Climate shock affected question
             if q_name == "HHAffectedClimate":
                 # If there are disaster types in context, high probability of Yes
                 disaster_types = context.get("__disaster_types__")
                 if disaster_types and len(disaster_types) > 0:
                     prob = 0.85  # 85% chance of Yes if disasters exist
                 else:
                     prob = 0.15  # 15% chance of Yes if no disasters (random events)
             
             # HHS Yes/No questions: Only affirmative in Year 1 (baseline)
             # Per simulated scores.docx: "Solo en el primer año debería haber hogares reportando respuestas afirmativas"
             elif q_name in ["HHSNoFood", "HHSBedHung", "HHSNotEat"]:
                 year_index = context.get("__year_index__", 0)
                 if year_index == 0:
                     # Baseline Year 1: ~30% chance of affirmative
                     prob = 0.30
                 else:
                     # Follow-up years: Force "No" (0% probability of Yes)
                     prob = 0.0
             
             # PHASE 2: Assistance-related questions
             elif "asst" in q_name.lower() or "assistance" in q_name.lower() or "aid" in q_name.lower():
                 # Use humanitarian response probability
                 events = context.get("__filtered_events__", [])
                 prob = calculate_assistance_probability(events, self.config)
             # PHASE 3: Housing/shelter/displacement questions
             elif any(word in q_name.lower() for word in ["shelter", "dwelling", "house", "displaced", "homeless"]):
                 # Use physical destruction probability (Phase 4)
                 destruction_prob = context.get("__physical_destruction_prob__", 0.0)
                 
                 # Use displacement probability
                 events = context.get("__filtered_events__", [])
                 displacement_prob = check_displacement(events, self.config)
                 
                 # If the question asks if house is distinct/destroyed
                 if "destroy" in q_name.lower() or "damage" in q_name.lower():
                      prob = destruction_prob # Direct probability of destruction
                 elif "displaced" in q_name.lower() or "homeless" in q_name.lower():
                     prob = displacement_prob  # Direct displacement question
                 else:
                     prob = 1.0 - max(displacement_prob, destruction_prob)  # Inverse (Adequate shelter?)
             
             # PHASE 3: Health/medical questions
             elif any(word in q_name.lower() for word in ["health", "medical", "injury", "injured", "sick"]):
                 # Use health impact probability
                 events = context.get("__filtered_events__", [])
                 prob = check_health_impact(events, self.config)
             
             else:
                 # Base prob for "Yes"
                 # Fix 4: Increased probability for expense _Purch_ fields
                 is_expense_purch = "_Purch" in q_name and ("Exp" in q_name or "exp" in q_name.lower())
                 if is_expense_purch:
                     base_prob = 0.65  # 65% base for expense purchases
                 elif "_Purch" in q_name:
                     base_prob = 0.50  # 50% for other purchases
                 else:
                     base_prob = 0.45  # Default for other Yesno
                 
                 base_prob += self.profile.yesno_adjust
                 
                 progress = self._progress_factor(context)
                 if is_expense_purch:
                     prob = base_prob + (0.2 * progress)  # Purchases increase with stability
                 elif "_Purch" in q_name:
                     prob = base_prob + (0.25 * progress)
                 else:
                     prob = base_prob - (0.2 * progress)  # Other yes/no might decrease
                     
                 # Impact of disaster: reduces purchase power
                 if ("_Purch" in q_name) and impact > 0:
                     prob -= (impact * 0.15)
                 
                 prob = max(0.10, min(0.90, prob))
             
             # Identify which option is 'Yes' (1, yes, TRUE)
             yes_names = {"1", "yes", "Yes", "TRUE", "true", "y", "Y"}
             
             option_weights = []
             for opt in options:
                 is_yes = str(opt['name']).strip() in yes_names
                 w = prob if is_yes else (1.0 - prob)
                 option_weights.append(w)
                 
             selected = self.rng.choices(options, weights=option_weights, k=1)[0]
             return selected['name']

        # Default Random with validation
        selected = self.rng.choice(options)
        selected_value = selected['name']
        
        # Validate choice exists in options (safety check)
        valid_values = {str(opt['name']) for opt in options}
        if str(selected_value) not in valid_values:
            print(f"Warning: {q_name} generated invalid value '{selected_value}', using fallback")
            selected_value = options[0]['name']
        
        return selected_value

    def _pick_multiple(self, question, context):
        parts = question.get('type').split()
        if len(parts) > 1:
            list_name = parts[1]
            options = self.choices.get(list_name, [])
            if options:
                # Dynamic diversity logic
                progress = self._progress_factor(context)
                max_choices = len(options)
                
                # Baseline 1, adds more as progress increases
                diversity_boost = int(round(progress * max(1, max_choices - 1) * 0.4))
                k = 1 + diversity_boost + self.rng.randint(0, 1)
                k = max(1, min(max_choices, k))
                
                selected = self.rng.sample(options, k)
                # Important: Cast to string to prevent TypeError
                return " ".join([str(s['name']) for s in selected])
        return ""

