# Nairobi Urban Green Spaces Carbon-Cooling Analysis
## Phase 1: Data Acquisition and Multi-Service Indicator Generation

---

## 📋 Project Overview

This repository contains a modular Google Earth Engine workflow for analyzing the relationship between carbon sequestration and thermal regulation in Nairobi's urban green spaces.

### Research Objectives

1. **Generate indicators** enabling better understanding of linkages between carbon sequestration and cooling
2. **Characterize spatio-temporal structure** of urban green spaces (UGS)
3. **Determine carbon-cooling linkages** through derived indicators and statistical models
4. **Develop ecological performance indicators** and generate greening priority maps

### Phase 1 Deliverables

**Carbon Indicators:**
- NDVI (dual-purpose proxy for VCSD and cooling)
- Foundation for integration with i-Tree Eco field data

**Cooling Indicators:**
- LST (Land Surface Temperature) rasters
- RLST (Relative LST) using mean-SD method
- CICS (Cold Island Core Sources) identification

**Land Cover:**
- Multi-temporal LULC classifications
- UGS patch delineation and characterization

---

## 📁 Repository Structure

```
gee_scripts/
├── 01_lst_retrieval.js          # Landsat LST extraction
├── 02_index_calculation.js      # Sentinel-2 NDVI & NDBI
├── 03_lulc_classification.js    # Supervised land cover classification
├── 04_rlst_cics_analysis.js     # Relative LST & CICS identification
└── README.md                    # This file
```

---

## 🚀 Quick Start Guide

### Prerequisites

1. **Google Earth Engine account** (sign up at https://earthengine.google.com)
2. **Study area defined**: Nairobi City (36.7958, -1.2995, 36.8362, -1.2695)
3. **Google Drive space**: ~2-3 GB for all outputs

### Recommended Execution Order

Run scripts in numerical order for optimal workflow:

01 → 02 → 03 → 04
LST → NDVI → LULC → RLST/CICS

### Time Estimates

| Script | Processing Time | Manual Effort |
|--------|-----------------|---------------|
| 01 -   | 5-10 min        | Minimal       |
| 02 -   | 5-10 min        | Minimal       |
| 03 -   | 10-15 min       | 1-2 hours     |
| 04 -   | 5-10 min        | Minimal       |

**Total:** ~30-45 min processing + 1-2 hours training data collection

---

## 📜 Script Details

### Script 01: Land Surface Temperature (LST) Retrieval

**Purpose:** Extract LST from Landsat 8/9 thermal bands

**Key Features:**
- Cloud-masked thermal composites
- Kelvin → Celsius conversion
- Quality statistics for validation
- Landsat 8 (2015-2021) and Landsat 9 (2022+) support

**Outputs:**
- `LST_2015.tif` (30m resolution)
- `LST_2018.tif`
- `LST_2021.tif`
- `LST_2024.tif`

**Expected LST Ranges (Nairobi):**
- Water/Dense vegetation: 18-25°C
- Mixed urban: 25-32°C
- Urban core/Bare soil: 32-45°C

**Usage:**
```javascript
// 1. Open Code Editor
// 2. Copy script content
// 3. Run
// 4. Tasks tab → Run all exports
```

---

### Script 02: Spectral Indices (NDVI & NDBI)

**Purpose:** Calculate vegetation and built-up indices from Sentinel-2

**Key Features:**
- Cloud Score+ masking (threshold: 0.6)
- Median compositing for gap-filling
- Dual outputs: NDVI + NDBI

**NDVI Formula:** `(NIR - RED) / (NIR + RED)` = `(B8 - B4) / (B8 + B4)`

**NDBI Formula:** `(SWIR - NIR) / (SWIR + NIR)` = `(B11 - B8) / (B11 + B8)`

**Outputs:**
- `NDVI_YYYY.tif` (10m resolution) × 4 epochs
- `NDBI_YYYY.tif` (10m resolution) × 4 epochs

**Research Applications:**
- **NDVI:** Predictor for VCSD (carbon), cooling efficacy
- **NDBI:** Urban expansion tracking, UGS boundary delineation

**NDVI Interpretation:**
| Range | Land Cover |
|-------|-------------------------|
| < 0.2 | Water, bare soil, urban |
|0.2-0.5| Grassland, sparse vegetation |
|0.5-0.7| Moderate vegetation |
| > 0.7 | Dense vegetation, forests |

---

### Script 03: Land Use/Land Cover Classification

**Purpose:** Supervised classification to map UGS and other land cover types

**Land Cover Classes (5-class scheme):**
0. **Urban/Built-up** - Impervious surfaces
1. **Bare Land** - Exposed soil
2. **Water** - Rivers, lakes, dams
3. **Grassland** - Parks, sports fields
4. **Forest** - Dense tree cover

**Key Features:**
- Random Forest classifier (50 trees)
- 70/30 train/validation split
- Feature engineering: spectral bands + indices + terrain
- Accuracy assessment (confusion matrix)
- Area statistics per class

**Training Data Requirements:**

⚠️ **CRITICAL:** You must create training samples before classification

**How to Create Training Data:**

1. Open Code Editor with Script 03
2. Use drawing tools (polygon/point marker)
3. Create 5 FeatureCollections:

```javascript
// For each class, create a collection with property 'landcover'
urban      → landcover: 0  (100 points)
bare       → landcover: 1  (80 points)
water      → landcover: 2  (60 points)
grassland  → landcover: 3  (100 points)
forest     → landcover: 4  (100 points)
```

4. Merge collections:
```javascript
var trainingData = urban.merge(bare).merge(water)
                        .merge(grassland).merge(forest);
```

5. Set `hasTrainingData = true` in script
6. Re-run script

**Expected Accuracy Targets:**
- Overall Accuracy: >85%
- Kappa: >0.80
- Per-class Producers/Consumers: >75%

**Outputs:**
- `LULC_YYYY.tif` (10m resolution) × 4 epochs
- Accuracy metrics (printed in Console)

---

### Script 04: Relative LST & CICS Identification

**Purpose:** Normalize LST and identify Cold Island Core Sources

**RLST Formula:** `RLST = (LST - μ) / σ`
- μ = mean LST across study area
- σ = standard deviation of LST

**RLST Interpretation:**
| Value | Thermal Status |
|-------|----------------|
| < -2 | Extreme cold (very strong CICS) |
| -2 to -1 | Significantly cooler (CICS) |
| -1 to +1 | Average |
| +1 to +2 | Significantly warmer (heat island) |
| > +2 | Extreme heat (strong UHI) |

**CICS Definition (both criteria must be met):**
1. **Thermal:** RLST < -1°C
2. **Ecological:** Land cover = Forest (4), Grassland (3), or Water (2)

**Key Features:**
- Thermal anomaly identification
- CICS mask generation
- Area statistics and coverage percentage
- Thermal zone classification
- Change detection between epochs

**Outputs:**
- `RLST_YYYY.tif` (30m resolution) × 4 epochs
- `CICS_YYYY.tif` (binary mask) × 4 epochs
- CICS area statistics (ha and %)

**Expected CICS in Nairobi:**
- Nairobi National Park (large, stable)
- Karura Forest (large, stable)
- City Park, Uhuru Park (medium/small)
- Water bodies (small, intense)

**Prerequisites:**
- LST rasters from Script 01
- LULC classifications from Script 03

---

## 📊 Complete Output Inventory

### After Running All Scripts:

| Data Product | Count | Resolution | Total Size |
|--------------|-------|------------|------------|
| LST | 4 | 30m | ~80 MB |
| NDVI | 4 | 10m | ~120 MB |
| NDBI | 4 | 10m | ~120 MB |
| LULC | 4 | 10m | ~120 MB |
| RLST | 4 | 30m | ~80 MB |
| CICS | 4 | 30m | ~80 MB |
| **TOTAL** | **24 files** | **Mixed** | **~600 MB** |

All outputs saved to: `Google Drive/nairobi_phase1/`

---

## 🔍 Quality Control Checklist

### Visual Inspection

- [ ] **LST:** Hot spots align with urban areas, cool spots with water/forests
- [ ] **NDVI:** High values in known green spaces (Karura, National Park)
- [ ] **NDBI:** High values in CBD, industrial areas
- [ ] **LULC:** Classes match Google Earth imagery
- [ ] **RLST:** Thermal anomalies make sense spatially
- [ ] **CICS:** Located in major parks and forests

### Statistical Checks

- [ ] **LST:** Mean 25-35°C, no extreme outliers
- [ ] **NDVI:** Mean 0.3-0.5, range 0-0.9
- [ ] **NDBI:** Mean around 0, range -0.5 to +0.5
- [ ] **LULC:** Overall accuracy >85%, Kappa >0.80
- [ ] **RLST:** Mean ≈0, Std Dev ≈1 (by definition)
- [ ] **CICS:** Coverage 10-30% of study area

### Temporal Consistency

- [ ] No abrupt, unexplained changes between years
- [ ] NDVI trends align with rainfall patterns
- [ ] Urban expansion visible in NDBI and LULC
- [ ] CICS changes correspond to known land use changes

---

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### "No images found"
**Cause:** Too strict cloud filtering or limited Landsat/Sentinel-2 coverage

**Solutions:**
```javascript
// Increase cloud threshold
var cloudThreshold = 40; // Instead of 30

// Expand date range
var startDate = ee.Date.fromYMD(year, 10, 1); // Start Oct instead of Jan
var endDate = startDate.advance(6, 'month');  // 6 months instead of 12

// Lower Cloud Score+ threshold
var csThreshold = 0.5; // Instead of 0.6
```

#### "Computation timed out"
**Solutions:**
```javascript
// Add tileScale parameter
var training = composite.sampleRegions({
  collection: trainingData,
  properties: ['landcover'],
  scale: 10,
  tileScale: 16  // Add this
});

// Process years individually
var epochs = [2024]; // Instead of [2015, 2018, 2021, 2024]

// Clip earlier
var composite = masked.median().clip(geometry); // Clip before computations
```

#### "Export fails"
**Solutions:**
- Check Google Drive storage
- Reduce `exportScale` from 10m to 30m
- Use `maxPixels: 1e13` parameter
- Export to Asset first, then to Drive

#### "Training data accuracy low (<80%)"
**Solutions:**
1. Collect more training samples (200+ per class)
2. Improve spatial distribution
3. Remove ambiguous/mixed pixels
4. Add more feature variables
5. Try different classifier (SVM, CART)

---

## 📈 Next Steps (Phase 2)

After Phase 1 completion:

### Spatial Analysis
- [ ] Calculate landscape metrics (fragmentation, connectivity)
- [ ] Delineate individual UGS patches
- [ ] Analyze patch size distribution
- [ ] Assess spatial autocorrelation

### Integration with Field Data
- [ ] Import i-Tree Eco outputs (VCSD from field surveys)
- [ ] Correlate VCSD with NDVI at sample sites
- [ ] Develop NDVI-VCSD regression model
- [ ] Predict VCSD across entire study area

### Carbon-Cooling Linkage Analysis
- [ ] Correlate NDVI with LST/RLST
- [ ] Analyze VCSD-cooling relationships
- [ ] Identify optimal UGS characteristics
- [ ] Develop multi-service performance metrics

### Priority Mapping
- [ ] Integrate carbon + cooling indicators
- [ ] Identify underserved areas
- [ ] Generate greening priority zones
- [ ] Support urban planning decisions

---

## 📚 References & Resources

### Key Methodologies
- **RLST:** Mean-standard deviation method for thermal normalization
- **CICS:** Dual-criteria approach (thermal + ecological)
- **Supervised Classification:** Random Forest with feature engineering
- **Cloud Masking:** Cloud Score+ for Sentinel-2

### Data Sources
- **Sentinel-2 SR Harmonized:** https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED
- **Landsat Collection 2:** https://www.usgs.gov/landsat-missions/landsat-collection-2
- **Cloud Score+:** https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_CLOUD_SCORE_PLUS_V1_S2_HARMONIZED
- **ALOS World 3D DEM:** https://developers.google.com/earth-engine/datasets/catalog/JAXA_ALOS_AW3D30_V4_1

### Learning Resources
- **End-to-End GEE Course:** https://courses.spatialthoughts.com/end-to-end-gee.html
- **GEE Documentation:** https://developers.google.com/earth-engine
- **GEE Community:** https://groups.google.com/g/google-earth-engine-developers

---

## 🤝 Workflow Best Practices

### Data Management
1. **Version control:** Include date/version in filenames
2. **Metadata:** Document processing parameters in file properties
3. **Backup:** Keep copies of training data and scripts
4. **Organization:** Use consistent folder structure

### Reproducibility
1. **Fixed seeds:** Use same random seed for train/test splits
2. **Parameter documentation:** Record all thresholds and settings
3. **Script versioning:** Save dated copies of scripts
4. **Processing logs:** Export Console output for records

### Efficiency
1. **Asset usage:** Upload LST/LULC as assets, load in later scripts
2. **Batch processing:** Process all years together when possible
3. **Scale appropriately:** Match resolution to analysis needs
4. **Incremental development:** Test on small areas first

---

## ⚠️ Important Notes

### Study Area Constraints
- Scripts are configured for Nairobi (UTM 37S)
- Modify CRS for other regions
- Adjust cloud thresholds based on local climate

### Temporal Coverage
- Sentinel-2: 2015-present
- Landsat 8: 2013-present
- Landsat 9: 2021-present
- Choose years with data availability

### Computing Limits
- Code Editor: 5-minute timeout for on-demand computation
- Export tasks: No timeout (run in background)
- Use exports for large/complex computations

### Data Licensing
- Landsat: Public domain (USGS)
- Sentinel-2: Free and open (Copernicus)
- Generated outputs: Your research, cite data sources

---

## 📧 Support

For questions or issues:
1. Check troubleshooting section above
2. Review GEE documentation
3. Search GEE Developers forum
4. Post detailed questions to: https://groups.google.com/g/google-earth-engine-developers

---

## ✅ Completion Checklist

Track your progress through Phase 1:

### Script Execution
- [ ] Script 01: LST retrieval completed
- [ ] Script 02: Indices calculated
- [ ] Script 03: Training data collected
- [ ] Script 03: LULC classification completed
- [ ] Script 04: RLST and CICS generated

### Quality Control
- [ ] Visual inspection completed
- [ ] Statistical validation passed
- [ ] Temporal consistency verified
- [ ] Outputs organized in Drive

### Documentation
- [ ] Processing parameters recorded
- [ ] Accuracy metrics saved
- [ ] Known issues documented
- [ ] Next steps planned

### Data Readiness
- [ ] All 24 rasters exported
- [ ] File naming conventions followed
- [ ] Metadata embedded
- [ ] Ready for Phase 2 analysis

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Study Area:** Nairobi, Kenya  
**Coordinate System:** EPSG:32737 (UTM Zone 37S)
