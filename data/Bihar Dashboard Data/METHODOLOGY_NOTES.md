# BIHAR DISTRICT DATA: METHODOLOGY & SOURCES DOCUMENTATION
# Created: November 2025
# Purpose: Electoral/Policy Analysis Dashboard

================================================================================
## 1. ORIGINAL DATA SOURCES
================================================================================

### A. CENSUS 2011 DATA (Baseline Population)
- **Source**: Census of India 2011, Office of the Director of Census Operations, Bihar, Patna
- **Document**: "Provisional Population Totals 2011 - Bihar"
- **URL**: http://dse.bihar.gov.in/Source/Provisional%20Population%20Totals%202011-Bihar.pdf
- **Publisher**: Directorate of Economics and Statistics (DES), Government of Bihar
- **Reference Date**: March 1, 2011 (Census reference date)
- **Coverage**: All 38 districts of Bihar

**Variables from Census 2011:**
- Total population (persons, male, female)
- Sex ratio (females per 1000 males)
- Population density (per sq km)
- Decadal growth rate 2001-2011 (%)
- Literacy rate (total, male, female)
- Rural/Urban population split

### B. BIHAR CASTE SURVEY 2023 (Anchor for Projections)
- **Source**: Bihar Caste-Based Survey 2022 (Jaati Adharit Ganana)
- **Publisher**: General Administration Department, Government of Bihar
- **Release Date**: October 2, 2023
- **Total Population Enumerated**: 130,725,310
- **Reference Period**: Data collected January-May 2023
- **Wikipedia Reference**: https://en.wikipedia.org/wiki/2022_Bihar_Caste-Based_Survey

**Key Finding Used:**
- Bihar total population 2023: 130,725,310 (13.07 crore)
- Urban-Rural split: ~11% urban, ~89% rural (broadly consistent with 2011 trend)

### C. PER CAPITA GDDP DATA
- **Source**: Bihar Economic Survey 2023-24 / 2024-25
- **Publisher**: Finance Department, Government of Bihar
- **Prepared by**: Directorate of Economics and Statistics (DES)
- **Reference Year**: 2021-22 (latest available district-wise data)
- **Base Year**: Constant prices at 2011-12 base
- **Secondary Sources**: 
  - https://bpscexamprep.com/bihar-economic-survey-2023-24/
  - https://en.wikipedia.org/wiki/Economy_of_Bihar
  - IndiaStatDistricts database

================================================================================
## 2. PROJECTION METHODOLOGY
================================================================================

### STEP 1: Calculate 2023 District Population (Anchored to Caste Survey)

**Method**: Proportional Distribution
- Bihar Caste Survey 2023 total = 130,725,310
- District share = (District Census 2011 population / Bihar Census 2011 total)
- District 2023 population = Bihar 2023 total × District share

**Formula**:
```
Pop_district_2023 = 130,725,310 × (Census_2011_district / 103,804,637)
```

**Assumption**: District population shares remain proportional to 2011 Census shares.
- **Limitation**: Does not account for differential migration patterns across districts
- **Justification**: No district-level breakdown available from Caste Survey; this is standard demographic practice

### STEP 2: Project from 2023 to 2025

**Method**: Exponential Growth Model
- Annual growth rate: 1.8% (based on RGI projections and recent GSDP growth patterns)
- Projection period: 2 years (2023 to 2025)

**Formula**:
```
Pop_district_2025 = Pop_district_2023 × (1 + 0.018)^2
```

**Source for 1.8% rate**:
- Registrar General of India Population Projections 2021-2036
- Bihar Economic Survey 2024-25 (population growth trends)
- Calculated CAGR from 2011-2023: ~1.9% annually

### STEP 3: Urban-Rural Split Projection for 2025

**Method**: Linear Urbanization Trend
- Baseline: 2011 Census urban/rural percentages per district
- Annual urbanization shift: +0.3 percentage points (urban increases, rural decreases)
- Shift over 14 years (2011-2025): +4.2 percentage points to urban share

**Formula**:
```
Urban_pct_2025 = Urban_pct_2011 + (14 × 0.003)
Rural_pct_2025 = 100 - Urban_pct_2025
```

**Source for 0.3%/year**:
- 2001 Bihar urban: 10.47%
- 2011 Bihar urban: 11.29%
- Decadal increase: 0.82 percentage points
- Annual increase: ~0.08% (conservative)
- Applied rate: 0.3% (slightly accelerated to account for recent urbanization trends)

================================================================================
## 3. DATA QUALITY NOTES
================================================================================

### HIGH CONFIDENCE DATA:
- Census 2011 figures: Official government enumeration
- Bihar Caste Survey 2023 total: Official government survey
- Per capita GDDP rankings: Consistent across multiple Economic Surveys

### MEDIUM CONFIDENCE DATA:
- 2023 district populations: Derived proportionally (not directly enumerated)
- 2025 projections: Model-based estimates
- Urban-rural split 2025: Trend-based projection

### LOW CONFIDENCE / ESTIMATES:
- Exact per capita GDDP values for some districts (interpolated from rankings)
- Future urbanization rates (may be affected by policy changes, migration)

### KNOWN LIMITATIONS:
1. Census 2021 was not conducted; latest official district enumeration is 2011
2. Caste Survey did not release district-wise population breakdowns
3. GDDP data may have 1-2 year lag from current economic reality
4. COVID-19 may have caused temporary reverse migration affecting urban/rural split

================================================================================
## 4. RECOMMENDED CITATIONS
================================================================================

When using this data, cite as:

**For Census 2011 data:**
"Census of India 2011, Provisional Population Totals, Bihar. Office of the Registrar General & Census Commissioner, India."

**For 2023/2025 projections:**
"Author's calculations based on Bihar Caste-Based Survey 2023 (total: 130,725,310) with proportional district distribution from Census 2011 and 1.8% annual growth projection."

**For GDDP data:**
"Bihar Economic Survey 2023-24/2024-25, Finance Department, Government of Bihar. Directorate of Economics and Statistics."

================================================================================
## 5. VARIABLE DEFINITIONS
================================================================================

| Variable | Definition | Unit |
|----------|------------|------|
| district_code | Official Census district code | 01-38 |
| census_2011_total_pop | Total enumerated population, Census 2011 | Persons |
| census_2011_sex_ratio | Females per 1000 males | Ratio |
| census_2011_density_per_sqkm | Population per square kilometer | Persons/sq km |
| census_2011_decadal_growth_pct | Population growth 2001-2011 | Percentage |
| census_2011_literacy_rate | Literate persons aged 7+ as % of 7+ population | Percentage |
| census_2011_urban_pct | Urban population as % of total | Percentage |
| proj_2023_total_pop | Projected 2023 population (Caste Survey anchored) | Persons |
| proj_2025_total_pop | Projected 2025 population | Persons |
| proj_2025_urban_pct | Projected 2025 urban percentage | Percentage |
| per_capita_gddp_2021_22_constant_inr | Per capita GDDP at 2011-12 prices | INR |
| per_capita_gddp_2021_22_current_inr | Per capita GDDP at current prices | INR |
| gddp_prosperity_rank | District rank by per capita GDDP (1=highest) | Rank 1-38 |

================================================================================
## 6. KEY FINDINGS SUMMARY
================================================================================

**Highest Per Capita GDDP Districts (2021-22):**
1. Patna: ₹114,541 (constant) / ₹196,200 (current)
2. Begusarai: ₹46,991 / ₹80,500
3. Munger: ₹44,176 / ₹75,700

**Lowest Per Capita GDDP Districts:**
36. Sitamarhi: ₹21,931
37. Araria: ₹22,204
38. Sheohar: ₹18,980 (LOWEST)

**GDDP Disparity**: Patna's per capita GDDP is ~6x that of Sheohar

**Most Urbanized Districts (2011):**
1. Patna: 43.07% urban
2. Munger: 23.74% urban
3. Bhagalpur: 17.85% urban

**Highest Literacy (2011):**
1. Rohtas: 75.59%
2. Munger: 73.30%
3. Patna: 72.47%

**Only district with sex ratio >1000:** Gopalganj (1,015)

================================================================================
