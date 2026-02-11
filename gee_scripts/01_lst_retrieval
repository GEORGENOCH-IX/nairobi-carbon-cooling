/**
 * SCRIPT 01: LAND SURFACE TEMPERATURE (LST) RETRIEVAL
 * =====================================================
 * Purpose: Retrieve and process Land Surface Temperature from Landsat 8/9
 * 
 * Objective 1 - Phase 1: Cooling Indicators
 * - Calculate LST for multi-temporal analysis
 * - Foundation for RLST (Relative LST) calculation
 * - Identify thermal patterns across Nairobi
 * 
 * Outputs:
 * - LST rasters for 2015, 2018, 2021, 2024 (°C)
 * - Quality-checked, cloud-masked thermal composites
 * 
 * Next Steps:
 * - Use these LST outputs in Script 04 for RLST calculation
 * - Identify Cold Island Core Sources (CICS)
 */

// STEP 1: CONFIGURATION
// Study area - Nairobi City
var bounds = [36.7958, -1.2995, 36.8362, -1.2695]; // W,S,E,N
var geometry = ee.Geometry.Rectangle(bounds);
// Analysis epochs
var epochs = [2015, 2018, 2021, 2024];
// Cloud threshold for filtering
var cloudThreshold = 30;
// Export configuration
var exportFolder = 'nairobi_phase1';
var exportScale = 30; // meters
var exportCrs = 'EPSG:32737'; // UTM Zone 37S
// Visualization
var lstVis = {
  min: 20, 
  max: 45, 
  palette: [
    '#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
    '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026'
  ]
};
Map.centerObject(geometry, 12);
Map.addLayer(geometry, {color: 'red'}, 'Study Area', false);

// STEP 2: CLOUD MASKING FUNCTION
/**
 * Mask clouds and cloud shadows in Landsat Collection 2
 * Uses QA_PIXEL band for quality assessment
 */
function maskLandsatClouds(image) {
  var qa = image.select('QA_PIXEL');
  // Bit masks for different quality issues
  var cloudBit = 1 << 3;        // Bit 3: Cloud
  var cloudShadowBit = 1 << 4;  // Bit 4: Cloud shadow
  var snowBit = 1 << 5;         // Bit 5: Snow
  // Create mask for clear pixels
  var mask = qa.bitwiseAnd(cloudBit).eq(0)
    .and(qa.bitwiseAnd(cloudShadowBit).eq(0))
    .and(qa.bitwiseAnd(snowBit).eq(0));
  return image.updateMask(mask);
}

// STEP 3: LST CALCULATION FUNCTION
/**
 * Calculate Land Surface Temperature from Landsat thermal band
 * 
 * Landsat Collection 2 ST products provide surface temperature in Kelvin
 * with a scale factor that needs to be applied
 * 
 * Formula: LST (°C) = (ST_B10 × scale_factor + offset) - 273.15
 */
function calculateLST(image) {
  // Select thermal band ST_B10 (Band 10 thermal infrared)
  var thermal = image.select('ST_B10');
  // Apply scale factor and convert Kelvin to Celsius
  // Collection 2 ST products: scale = 0.00341802, offset = 149.0
  var lstCelsius = thermal
    .multiply(0.00341802)
    .add(149.0)
    .subtract(273.15);
  // Copy metadata for temporal information
  return lstCelsius
    .rename('LST')
    .copyProperties(image, ['system:time_start', 'system:time_end']);
}

// STEP 4: LST PROCESSING FOR A SINGLE EPOCH
/**
 * Process LST for a specific year
 * Returns median composite and image count
 */
function processLST(year) {
  print('Processing LST for ' + year);
  var startDate = ee.Date.fromYMD(year, 1, 1);
  var endDate = startDate.advance(1, 'year');
  // Select appropriate Landsat collection
  var collection;
  var collectionName;
  if (year >= 2022) {
    // Landsat 9 (launched September 2021, data from Oct 2021)
    collection = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2');
    collectionName = 'Landsat 9';
  } else {
    // Landsat 8 (launched February 2013, data from April 2013)
    collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2');
    collectionName = 'Landsat 8';
  }
  print('Collection:', collectionName);
  // Filter collection
  var filtered = collection
    .filter(ee.Filter.date(startDate, endDate))
    .filter(ee.Filter.bounds(geometry))
    .filter(ee.Filter.lt('CLOUD_COVER', cloudThreshold));
  var imageCount = filtered.size();
  print('Images available:', imageCount.getInfo());
  // Check if we have sufficient images
  if (imageCount.getInfo() === 0) {
    print('⚠ WARNING: No images found for ' + year);
    print('  Try increasing cloud threshold or expanding date range');
    return null;
  }
  // Apply cloud masking
  var masked = filtered.map(maskLandsatClouds);
  // Calculate LST for each image
  var lstCollection = masked.map(calculateLST);
  // Create median composite
  var lstComposite = lstCollection.median().clip(geometry);
  // Calculate statistics for quality check
  var stats = lstComposite.reduceRegion({
    reducer: ee.Reducer.minMax().combine({
      reducer2: ee.Reducer.mean(),
      sharedInputs: true
    }),
    geometry: geometry,
    scale: 100,
    maxPixels: 1e9
  });
  print('LST Statistics (°C):');
  print('  Min:', stats.get('LST_min'));
  print('  Max:', stats.get('LST_max'));
  print('  Mean:', stats.get('LST_mean'));
  print('✓ LST composite created');
  return {
    image: lstComposite,
    count: imageCount,
    year: year
  };
}

// EXPORT FUNCTION
/**
 * Export LST raster to Google Drive
 */
function exportLST(lstResult) {
  if (!lstResult) {
    return;
  }
  var year = lstResult.year;
  var image = lstResult.image;
  Export.image.toDrive({
    image: image,
    description: 'LST_' + year + '_Nairobi',
    folder: exportFolder,
    fileNamePrefix: 'LST_' + year,
    region: geometry,
    scale: exportScale,
    crs: exportCrs,
    maxPixels: 1e13,
    fileFormat: 'GeoTIFF'
  });
  print('  ► Export task created: LST_' + year);
}

// VISUALIZATION FUNCTION
/**
 * Add LST layers to map for visual inspection
 */
function visualizeLST(lstResult) {
  if (!lstResult) {
    return;
  }
  var year = lstResult.year;
  var image = lstResult.image;
  // Add to map (only show most recent year by default)
  var layerName = 'LST ' + year + ' (°C)';
  var visible = (year === 2024);
  Map.addLayer(image, lstVis, layerName, visible);
}

// MAIN PROCESSING LOOP
// Process each epoch
var results = epochs.map(function(year) {
  var result = processLST(year);
  
  if (result) {
    visualizeLST(result);
    exportLST(result);
  }  
  return result;
});

// SUMMARY
print('PROCESSING COMPLETE');
print('Total epochs processed:', epochs.length);
print('');
print('NEXT STEPS:');
print('1. Go to Tasks tab → Run all LST exports');
print('2. Download from Google Drive/' + exportFolder);
print('3. Visual QC: Check LST maps for anomalies');
print('4. Proceed to Script 02 for NDVI calculation');
print('5. Use LST outputs in Script 04 for RLST analysis');
// QUALITY CONTROL NOTES
/**
 * EXPECTED LST RANGES FOR NAIROBI:
 * 
 * - Cool areas (water, dense vegetation): 18-25°C
 * - Moderate areas (mixed land use): 25-32°C
 * - Hot areas (urban, bare soil): 32-45°C
 * 
 * RED FLAGS:
 * - Mean LST < 15°C or > 50°C → Check cloud masking
 * - Very few images (< 5) → Consider expanding date range
 * - Large data gaps → Increase cloud threshold cautiously
 * 
 * SEASONAL CONSIDERATIONS:
 * - Nairobi has two rainy seasons (Mar-May, Oct-Dec)
 * - Dry seasons (Jan-Feb, Jun-Sep) may have higher LST
 * - Annual composites capture overall thermal patterns
 * 
 * VALIDATION:
 * - Compare LST patterns with known features:
 *   • Nairobi National Park → cooler
 *   • CBD/Industrial areas → warmer
 *   • Water bodies (dams/rivers) → coolest
 */
// TROUBLESHOOTING GUIDE
/**
 * ISSUE: "No images found"
 * SOLUTION:
 * - Increase cloudThreshold to 40-50%
 * - Expand date range: use ±2 months buffer
 * - Check if Landsat data exists for that period
 * 
 * ISSUE: "Computation timed out"
 * SOLUTION:
 * - Process years individually (comment out others in epochs array)
 * - Reduce study area temporarily for testing
 * - Use .clip(geometry) before heavy computations
 * 
 * ISSUE: "Export fails"
 * SOLUTION:
 * - Check Google Drive storage space
 * - Reduce maxPixels if needed
 * - Export smaller regions separately
 * 
 * ISSUE: "Strange LST values"
 * SOLUTION:
 * - Verify cloud masking is working (check masked collection)
 * - Ensure scale factor is correct (0.00341802 for Collection 2)
 * - Check for sensor anomalies in source data
 */