# INDIA-DATA: Bihar Electoral Roll Analysis

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Varnasr/INDIA-DATA/pulls)

Analysis of Bihar electoral roll anomalies — voter deletion patterns, demographic shifts, and election data integrity research.

## Overview

This project investigates patterns in voter roll deletions across Bihar assembly constituencies, examining correlations between deletion rates, caste demographics, religious composition, and electoral outcomes. The analysis covers constituency-level and district-level data with statistical indicators of electoral integrity.

## Key Analysis Areas

- **Voter Deletion Patterns**: Male/female deletion rates by assembly constituency
- **Caste-Based Analysis**: Top and bottom caste groups by deletion volume
- **Religious Demographics**: Muslim deletion patterns and NDA win correlations
- **District Profiles**: GDP, population, rural/urban, and demographic summaries
- **Border Constituency Analysis**: Electoral patterns in border vs interior constituencies
- **Electoral Integrity Indicators**: Statistical metrics for assessing roll integrity

## Data

All datasets are in the `/data` directory:

| File | Description |
|------|-------------|
| `Bihar_SIR_Male_Female_Deletions_By_AC.xlsx` | Deletion data by assembly constituency |
| `ac_deletions_change_2020_2024.csv` | Deletion changes 2020-2024 |
| `ac_correlation_ready.csv` | Correlation-ready dataset |
| `top5_caste_groups_deleted.csv` | Most affected caste groups |
| `bottom5_caste_groups_deleted.csv` | Least affected caste groups |
| `district_caste_summary_master.csv` | District-level caste summary |
| `district_demography_summary.csv` | Demographic profiles |
| `district_gdp_profile.csv` | Economic profiles |
| `district_population_profile.csv` | Population data |
| `ac_border_classification.csv` | Border constituency classification |

### Contextual Documents

Additional methodology and analysis documents are in `/data/Bihar Dashboard Context/`.

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Varnasr/INDIA-DATA.git
   ```

2. Open `index.html` in a browser to view the interactive dashboard.

No build step required — the dashboard is a self-contained HTML file.

## Tech Stack

- HTML/CSS/JavaScript (vanilla)
- Data: CSV, XLSX, JSON
- Hosted on Netlify

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines on data contributions, corrections, and analysis improvements.

## Citation

```bibtex
@misc{india_data_2025,
  title={INDIA-DATA: Bihar Electoral Roll Analysis},
  author={Raman, Varna Sri},
  year={2025},
  publisher={GitHub},
  url={https://github.com/Varnasr/INDIA-DATA}
}
```

## License

[MIT License](LICENSE)

## Contact

- GitHub: [@Varnasr](https://github.com/Varnasr)
- Email: hello@impactmojo.in

---

*This is independent research. Data is sourced from public electoral records and government datasets.*

