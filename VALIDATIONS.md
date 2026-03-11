# Input Validations & GUI Specification

Complete field-by-field reference for all inputs. Covers types, rules, units, labels, conditional visibility, and cross-field dependencies. Intended as the single source of truth for GUI development.

---

## Modes of Operation

The entire input is governed by one flag:

**`general_parameters.use_global_road_user_calculations`** (`bool`)

| Value | Meaning | What the user provides |
|-------|---------|----------------------|
| `False` | Detailed mode — engine computes Road User Cost from traffic data | `traffic_and_road_data` + `WPI` |
| `True` | Global mode — user provides pre-computed Road User Cost | `daily_road_user_cost_with_vehicular_emissions` |

This flag controls which sections are shown and which are validated.

---

## Validation Layers

| Layer | Where | Triggered by |
|-------|-------|-------------|
| **Structural** | `inputs/input.py`, `inputs/input_global.py` | `InputMetaData.from_dict()` / `InputGlobalMetaData.from_dict()` |
| **Ecosystem** | `core/utils/input_validator.py` | `ironclad_validator()` after structural validation |
| **Calculation** | Sub-calculators | Not validated — input trusted after layers 1 & 2 |

---

## ADT Gate

> **If the sum of all `vehicles_per_day` = 0**, the user is opting out of road user cost.
> The following are **entirely skipped** — no validation, no calculation:
> - All `traffic_and_road_data` sub-blocks (`vehicle_data`, `accident_severity_distribution`, `additional_inputs`)
> - All ecosystem checks (carriageway sync, vehicle sync, WPI mapping)
> - All RUC calculations → `total_daily_ruc` returns `0`
>
> GUI implication: When all vehicle counts are 0, grey out / hide all road and WPI fields.

---

## Section 1 — General Parameters

`general_parameters` | Always required | Always shown

| Field | Label | Type | Unit | Rule | Notes |
|-------|-------|------|------|------|-------|
| `service_life_years` | Service Life | `int` | years | > 0 | Design life of the structure |
| `analysis_period_years` | Analysis Period | `int` | years | > 0; >= `service_life_years` | Total LCCA horizon |
| `discount_rate_percent` | Discount Rate | `float` | % | >= 0 | Time value of money |
| `inflation_rate_percent` | Inflation Rate | `float` | % | >= 0 | General price inflation |
| `interest_rate_percent` | Interest Rate | `float` | % | >= 0 | Loan/financing rate |
| `investment_ratio` | Investment Ratio | `float` | — | 0 to 1 (inclusive) | Proportion of public investment |
| `social_cost_of_carbon_per_mtco2e` | Social Cost of Carbon | `float` | USD/MtCO₂e | >= 0 | Used to monetise emissions |
| `currency_conversion` | Currency Conversion | `float` | INR per USD | > 0 | Exchange rate for cost normalisation |
| `construction_period_months` | Construction Period | `float` | months | > 0; <= `analysis_period_years × 12` | Duration of initial construction |
| `working_days_per_month` | Working Days per Month | `int` | days | > 0; <= `days_per_month` | Active working days |
| `days_per_month` | Days per Month | `int` | days | 1 to 31 (inclusive) | Calendar days in a month |
| `use_global_road_user_calculations` | RUC Mode | `bool` | — | Must be `True` or `False` | **Master switch** — controls entire form layout |

**Cross-field rules:**
- `analysis_period_years` >= `service_life_years`
- `construction_period_months` <= `analysis_period_years × 12`
- `working_days_per_month` <= `days_per_month`

---

## Section 2 — Traffic & Road Data

`traffic_and_road_data` | Required when `use_global_road_user_calculations = False`

> All sub-sections below are validated only when **ADT > 0**.
> GUI: Show this entire section only in detailed mode.

---

### 2a — Vehicle Data

`traffic_and_road_data.vehicle_data`

Eight vehicle types are always required. Each has the same fields:

| Vehicle Key | Display Name | Fuel |
|-------------|-------------|------|
| `small_cars` | Small Car | Petrol / Diesel |
| `big_cars` | Big Car | Petrol / Diesel |
| `two_wheelers` | Two Wheeler | Petrol |
| `o_buses` | Ordinary Buses | Diesel |
| `d_buses` | Deluxe Buses | Diesel |
| `lcv` | Light Commercial Vehicle (LCV) | Diesel |
| `hcv` | Heavy Commercial Vehicle (HCV) | Diesel |
| `mcv` | Multi-Axle Commercial Vehicle (MCV) | Diesel |

**Per-vehicle fields:**

| Field | Label | Type | Unit | Rule | Conditional |
|-------|-------|------|------|------|-------------|
| `vehicles_per_day` | Daily Count (ADT) | `int` | vehicles/day | >= 0 | Always shown |
| `carbon_emissions_kgCO2e_per_km` | Carbon Emission Factor | `float` | kgCO₂e/km | >= 0 | Always shown |
| `accident_percentage` | Accident Share | `float` | % | >= 0 | Always shown |
| `pwr` | Power-to-Weight Ratio | `float` | — | > 0 | **Only for `hcv` and `mcv`; required only when `vehicles_per_day > 0`; hidden for all other vehicle types** |

**Cross-field rule:**
- Sum of `accident_percentage` across all 8 vehicles must equal **100** (tolerance ±0.1)

---

### 2b — Accident Severity Distribution

`traffic_and_road_data.accident_severity_distribution`

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `fatal` | Fatal Accidents | `float` | % | >= 0; part of sum |
| `major` | Major Injury Accidents | `float` | % | >= 0; part of sum |
| `minor` | Minor Injury Accidents | `float` | % | >= 0; part of sum |

**Cross-field rule:**
- `fatal + major + minor` must equal **100** (tolerance ±1e-6)

---

### 2c — Additional Inputs

`traffic_and_road_data.additional_inputs`

| Field | Label | Type | Unit | Rule | Notes |
|-------|-------|------|------|------|-------|
| `alternate_road_carriageway` | Alternate Road Type | `string` (dropdown) | — | Must be a valid IRC carriageway code | See carriageway options below |
| `carriage_width_in_m` | Carriageway Width | `float` | m | >= 0 | Auto-filled from IRC standard; user can override; **required as custom input for Expressway types** |
| `road_roughness_mm_per_km` | Road Roughness (IRI) | `float` | mm/km | > 0 | International Roughness Index of alternate road |
| `road_rise_m_per_km` | Road Rise | `float` | m/km | >= 0 | Vertical rise per km |
| `road_fall_m_per_km` | Road Fall | `float` | m/km | >= 0 | Vertical fall per km |
| `additional_reroute_distance_km` | Additional Reroute Distance | `float` | km | >= 0 | Extra distance users travel due to detour |
| `additional_travel_time_min` | Additional Travel Time | `float` | minutes | >= 0 | Extra travel time per trip due to detour |
| `crash_rate_accidents_per_million_km` | Crash Rate | `float` | accidents/million veh-km | >= 0 | Annual crash rate for the work zone |
| `work_zone_multiplier` | Work Zone Multiplier | `float` | — | 0 to 1 (inclusive) | Scales crash rate for work zone conditions |
| `hourly_capacity` | Hourly Capacity | `int` | PCU/hour | > 0 | Auto-filled from IRC standard; GUI should show info note if user changes it |
| `peak_hour_traffic_percent_per_hour` | Peak Hour Distribution | `list[float]` | — | Each value in (0, 1]; sum of list <= 1.0; empty list is valid | Each entry = fraction of daily traffic in that peak hour; empty list = no peak hours defined |
| `force_free_flow_off_peak` | Force Free Flow (Off-Peak) | `bool` | — | `True` or `False` | If `True`, off-peak congestion is ignored (V/C treated as 0) |

**Carriageway Options** (`alternate_road_carriageway` dropdown):

| Code | Display Name | Standard Width (m) | Standard Capacity (PCU/hr) |
|------|--------------|--------------------|---------------------------|
| `SL` | Single Lane | 3.75 | 435 |
| `IL` | Intermediate Lane | 5.50 | 1158 |
| `2L` | Two Lane (Two Way) | 7.00 | 2400 |
| `2L_1W` | Two Lane (One Way) | 7.00 | 2700 |
| `3L_1W` | Three Lane (One Way) | 10.50 | 4200 |
| `4L` | Four Lane (Two Way) | 7.00 | 5400 |
| `6L` | Six Lane (Two Way) | 10.50 | 8400 |
| `8L` | Eight Lane (Two Way) | 14.00 | 13600 |
| `EW4` | 4 Lane Expressway | *custom required* | 5000 |
| `EW6` | 6 Lane Expressway | *custom required* | 7500 |
| `EW8` | 8 Lane Expressway | *custom required* | 9200 |

> When `EW4`, `EW6`, or `EW8` is selected, `carriage_width_in_m` becomes mandatory (no standard default).
> When any other code is selected, `carriage_width_in_m` is auto-filled but editable; show an info note if it differs from the standard.
> `hourly_capacity` is auto-filled from the standard; show an info note if the user provides a different value.

---

## Section 3 — Maintenance & Stage Parameters

`maintenance_and_stage_parameters` | Always required | Always shown

---

### 3a — Routine Inspection

`use_stage_cost.routine.inspection`

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `percentage_of_initial_construction_cost_per_year` | Routine Inspection Cost (% of ICC/year) | `float` | % | >= 0 |
| `interval_in_years` | Inspection Interval | `int` | years | > 0 |

---

### 3b — Routine Maintenance

`use_stage_cost.routine.maintenance`

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `percentage_of_initial_construction_cost_per_year` | Routine Maintenance Cost (% of ICC/year) | `float` | % | >= 0 |
| `percentage_of_initial_carbon_emission_cost` | Carbon Emission Cost (% of initial) | `float` | % | >= 0 |
| `interval_in_years` | Maintenance Interval | `int` | years | > 0 |

---

### 3c — Major Inspection

`use_stage_cost.major.inspection`

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `percentage_of_initial_construction_cost` | Major Inspection Cost (% of ICC) | `float` | % | >= 0 |
| `interval_for_repair_and_rehabitation_in_years` | Major Inspection Interval | `int` | years | > 0 |

---

### 3d — Major Repair

`use_stage_cost.major.repair`

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `percentage_of_initial_construction_cost` | Major Repair Cost (% of ICC) | `float` | % | >= 0 |
| `percentage_of_initial_carbon_emission_cost` | Carbon Emission Cost (% of initial) | `float` | % | >= 0 |
| `interval_for_repair_and_rehabitation_in_years` | Major Repair Interval | `int` | years | > 0 |
| `repairs_duration_months` | Repair Duration | `float` | months | > 0 |

---

### 3e — Bearing & Expansion Joint Replacement

`use_stage_cost.replacement_costs_for_bearing_and_expansion_joint`

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `percentage_of_super_structure_cost` | Replacement Cost (% of superstructure cost) | `float` | % | >= 0 |
| `interval_of_replacement_in_years` | Replacement Interval | `int` | years | > 0 |
| `duration_of_replacement_in_days` | Replacement Duration | `int` | days | > 0 |

---

### 3f — Demolition & Disposal

`end_of_life_stage_costs.demolition_and_disposal`

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `percentage_of_initial_construction_cost` | Demolition Cost (% of ICC) | `float` | % | >= 0 |
| `percentage_of_initial_carbon_emission_cost` | Carbon Emission Cost (% of initial) | `float` | % | >= 0 |
| `duration_for_demolition_and_disposal_in_months` | Demolition Duration | `float` | months | > 0 |

---

## Section 4 — Global RUC Block

`daily_road_user_cost_with_vehicular_emissions` | Only when `use_global_road_user_calculations = True`

> GUI: Show this section only in global mode. Hide entirely in detailed mode.

| Field | Label | Type | Unit | Rule |
|-------|-------|------|------|------|
| `total_daily_ruc` | Total Daily Road User Cost | `float` | INR/day | >= 0; must be numeric |
| `total_carbon_emission.total_emission_kgCO2e` | Total Daily Carbon Emission | `float` | kgCO₂e/day | >= 0; must be numeric |

---

## Section 5 — WPI (Wholesale Price Index)

`WPI` | Only when `use_global_road_user_calculations = False` **and ADT > 0**

> All WPI values are price indices — ratio of current year price to base year price.
> **All must be > 0** (a value of 1.0 means no price change from base year).
> GUI: Show this section only in detailed mode and only when at least one vehicle has count > 0.

### 5a — Fuel Cost Index

`WPI.fuel_cost`

| Field | Label | Rule |
|-------|-------|------|
| `petrol` | Petrol Price Index | > 0 |
| `diesel` | Diesel Price Index | > 0 |
| `engine_oil` | Engine Oil Price Index | > 0 |
| `other_oil` | Other Oil Price Index | > 0 |
| `grease` | Grease Price Index | > 0 |

---

### 5b — Vehicle Cost Indices

`WPI.vehicle_cost` — Three sub-blocks, each indexed by vehicle type.

**Vehicle keys in WPI:** `small_cars`, `big_cars`, `two_wheelers`, `o_buses`, `lcv`, `hcv`, `mcv`

> Note: `d_buses` in vehicle input maps to `o_buses` in all WPI lookups — there is no `d_buses` key in WPI.

| Sub-block | Label | Rule |
|-----------|-------|------|
| `property_damage` | Property Damage Index (per vehicle type) | > 0 for each vehicle key |
| `tyre_cost` | Tyre Cost Index (per vehicle type) | > 0 for each vehicle key |
| `spare_parts` | Spare Parts Index (per vehicle type) | > 0 for each vehicle key |
| `fixed_depreciation` | Fixed Depreciation Index (per vehicle type) | > 0 for each vehicle key |

---

### 5c — Commodity Holding Cost Index

`WPI.commodity_holding_cost` — Indexed by vehicle type (same 7 keys as above)

| Rule |
|------|
| > 0 for each vehicle key |

---

### 5d — Value of Time Cost Index

`WPI.vot_cost` — Indexed by vehicle type (same 7 keys as above)

| Rule | Note |
|------|------|
| > 0 for each vehicle key | Used as a multiplier — zero causes division by zero |

---

### 5e — Passenger & Crew Cost Index

`WPI.passenger_crew_cost`

| Field | Label | Rule |
|-------|-------|------|
| `passenger_cost` | Passenger Cost Index | > 0 |
| `crew_cost` | Crew Cost Index | > 0 |

---

### 5f — Medical Cost Index

`WPI.medical_cost`

| Field | Label | Rule |
|-------|-------|------|
| `fatal` | Medical Cost Index — Fatal | > 0 |
| `major` | Medical Cost Index — Major Injury | > 0 |
| `minor` | Medical Cost Index — Minor Injury | > 0 |

---

### 5g — WPI Year

`WPI.year`

| Field | Label | Type | Rule |
|-------|-------|------|------|
| `year` | WPI Reference Year | `int` | > 0 |

---

## Ecosystem / Cross-block Rules

Enforced in `core/utils/input_validator.py` — runs after structural validation, only when `use_global_road_user_calculations = False` **and ADT > 0**.

| Rule | Severity | GUI Behaviour |
|------|----------|---------------|
| `traffic_and_road_data` block must be present | Error | Block whole submission |
| `traffic_and_road_data` present but `use_global = True` | Warning | Show notice; allow submission |
| `alternate_road_carriageway` must be a valid IRC code | Error | Dropdown enforces this automatically |
| `hourly_capacity` differs from IRC standard | Info | Show info note next to field |
| All 8 vehicle types must be present in `vehicle_data` | Error | GUI always renders all 8 rows |
| Unknown vehicle type in `vehicle_data` | Warning | Show notice |
| WPI `medical_cost` must have `fatal`, `major`, `minor` keys | Error | Block submission |
| WPI `property_damage` must have an entry for every vehicle type present | Error | Block submission |
| `wpi` must be provided when `use_global = False` and ADT > 0 | Error | Block submission |

---

## GUI Conditional Visibility Summary

| Section / Field | Show when |
|-----------------|-----------|
| `traffic_and_road_data` (entire section) | `use_global_road_user_calculations = False` |
| `daily_road_user_cost_with_vehicular_emissions` (entire section) | `use_global_road_user_calculations = True` |
| `WPI` (entire section) | `use_global_road_user_calculations = False` AND at least one `vehicles_per_day > 0` |
| `vehicle_data` field validations, `accident_severity_distribution`, `additional_inputs` validations | ADT (sum of all `vehicles_per_day`) > 0 |
| `pwr` field for `hcv` | `hcv.vehicles_per_day > 0` |
| `pwr` field for `mcv` | `mcv.vehicles_per_day > 0` |
| `carriage_width_in_m` as mandatory input | `alternate_road_carriageway` is `EW4`, `EW6`, or `EW8` |
| Info note on `carriage_width_in_m` | User value differs from IRC standard |
| Info note on `hourly_capacity` | User value differs from IRC standard for selected carriageway |
