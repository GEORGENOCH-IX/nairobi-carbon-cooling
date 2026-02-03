# Nairobi Carbon–Cooling Linkages

This repository contains scripts, notebooks, and documentation for analyzing
the relationship between urban green spaces, carbon proxies, and land surface
cooling effects in Nairobi.

## Repository Structure

- `gee_scripts/`  
  Google Earth Engine JavaScript scripts for preprocessing, index calculation,
  LST retrieval, LULC classification, and exports.

- `notebooks/`  
  Jupyter notebooks for validation, landscape metrics, MSPA, modeling, and
  priority mapping.

- `scripts/`  
  Standalone Python scripts used across analyses.

- `data/`  
  Directory structure for raw, processed, and output data.
  **Data files are not tracked in Git.**

- `docs/`  
  Methodology notes, data sources, and validation documentation.

## Reproducibility

All results can be reproduced by:
1. Running GEE scripts in sequence
2. Exporting derived products
3. Executing notebooks in numerical order

See `docs/methodology.md` for details.
