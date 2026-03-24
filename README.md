# INDIA-DATA: Bihar Electoral Roll Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Varnasr/INDIA-DATA/pulls)
[![GitHub Last Commit](https://img.shields.io/github/last-commit/Varnasr/INDIA-DATA)](https://github.com/Varnasr/INDIA-DATA/commits/main)
[![Data: Election Commission](https://img.shields.io/badge/Data-Election%20Commission%20of%20India-blue)](https://eci.gov.in/)

**Analysis of Bihar electoral roll anomalies — voter deletion patterns, demographic shifts, and election data integrity research.**

---

## About

This repository investigates statistically anomalous patterns in voter roll deletions across Bihar assembly constituencies between electoral cycles. It examines correlations between voter deletion rates, caste demographics, religious composition, and electoral outcomes — raising questions about the integrity of voter registration processes in India's most populous state cluster.

The analysis is grounded in publicly available data from the Election Commission of India, supplemented by demographic data from the Census of India and academic research on Bihar's political economy.

This is independent academic research. All conclusions are data-driven and fully cited.

---

## Key Analysis Areas

| Analysis | Description |
|----------|-------------|
| **Voter Deletion Patterns** | Male and female deletion rates by assembly constituency |
| **Caste-Based Analysis** | Top and bottom caste groups by voter deletion volume — identifying demographic targeting patterns |
| **Religious Demographics** | Muslim voter deletion rates and correlations with NDA electoral performance |
| **District Profiles** | GDP, population, rural/urban, and demographic summaries for analysis context |
| **Border Constituency Analysis** | Electoral patterns in constituencies bordering Nepal and West Bengal vs interior |
| **Electoral Integrity Indicators** | Statistical metrics for assessing voter roll integrity across election cycles |

---

## Key Findings (Summary)

| Indicator | Finding |
|-----------|---------|
| **Net deletions (2019–2024)** | Significant net deletion in 40+ constituencies |
| **Demographic concentration** | Deletions disproportionately concentrated in Muslim-majority and SC/ST constituencies |
| **Gender asymmetry** | Male deletion rates systematically higher in certain districts |
| **Correlation with outcomes** | Districts with highest deletion rates show elevated NDA vote share growth |

> Full findings and methodology in the repository's analysis notebooks.

---

## Data Sources

| Source | Data Type |
|--------|-----------|
| [Election Commission of India](https://eci.gov.in) | Voter rolls, electoral rolls, constituency-level voter counts |
| [Delimitation Commission Reports](https://eci.gov.in/delimitation/) | Constituency boundary changes |
| [Census of India 2011](https://censusindia.gov.in) | Caste, religion, and demographic data |
| [Bihar State Election Commission](https://sec.bihar.gov.in) | Local body election cross-reference data |

---

## Repository Structure

```
INDIA-DATA/
├── data/
│   ├── voter_rolls/        # Raw and processed voter roll data by constituency
│   ├── demographics/       # Caste and religious demographic data
│   └── electoral_results/  # Election result data for correlation analysis
├── analysis/
│   ├── deletion_patterns.py    # Core deletion rate analysis
│   ├── demographic_overlay.py  # Caste/religion correlation analysis
│   ├── border_analysis.py      # Border vs interior constituency analysis
│   └── integrity_metrics.py   # Electoral integrity indicator construction
├── notebooks/
│   └── Bihar_Electoral_Analysis.ipynb  # Main analysis notebook
├── outputs/
│   └── visualisations/     # Charts and maps
├── LICENSE
└── README.md
```

---

## Methodology

1. **Data acquisition** — Voter roll summary data downloaded from ECI constituency portals for 2019 and 2024 electoral cycles
2. **Cleaning and standardisation** — Constituency names normalised, data merged across cycles
3. **Deletion rate calculation** — Net change in registered voters per constituency, disaggregated by gender
4. **Demographic overlay** — Matched with Census 2011 caste and religious demographic data at constituency level
5. **Statistical analysis** — Correlation analysis between deletion rates and demographic/electoral variables
6. **Integrity index construction** — Composite index weighting deletion rate, demographic concentration, and temporal anomaly

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Analysis | Python (pandas, scipy, statsmodels) | Data processing and statistical analysis |
| Visualisation | matplotlib, seaborn, plotly | Charts and geographic visualisations |
| Notebooks | Jupyter | Reproducible analysis documentation |

---

## Limitations

- Voter roll data is summary-level, not individual-level — individual-level patterns cannot be directly inferred
- Census 2011 demographic data is 13+ years old — demographic composition has shifted
- Constituency boundary changes (delimitation) complicate longitudinal comparison for some constituencies
- Deletions may reflect legitimate database cleaning (deaths, migration) — the analysis identifies statistical anomalies, not confirmed manipulation

---

## Related Repositories

- [BiharParichay-Project](https://github.com/Varnasr/BiharParichay-Project) — Bihar demographic classification system
- [someperspective](https://github.com/Varnasr/someperspective) — India's political economy 2004–2025
- [PolicyDhara](https://github.com/Varnasr/PolicyDhara) — Indian policy tracker

---

## License

MIT License — see [LICENSE](LICENSE) for details. Data from ECI and Census of India retains its original terms of use.

---

## Contributing

Research contributions, corrections, and additional data sources are welcome. Open a pull request or [file an issue](https://github.com/Varnasr/INDIA-DATA/issues).
