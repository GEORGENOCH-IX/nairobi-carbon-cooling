// ======================================================
// Script 02: Landsat Preprocessing with Temporal Epochs
// ======================================================

var aoi = ee.Geometry.Rectangle([36.65, -1.45, 37.10, -1.15]);

// Function to apply scaling factors
function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBand = image.select('ST_B10').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
              .addBands(thermalBand, null, true);
}

// Cloud mask function
function maskL8sr(image) {
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);
  return image.updateMask(qaMask).updateMask(saturationMask);
}

// Define epochs (dry seasons for consistency)
var epochs = [
  {year: 2015, start: '2015-01-01', end: '2015-02-28'},
  {year: 2018, start: '2018-01-01', end: '2018-02-28'},
  {year: 2021, start: '2021-01-01', end: '2021-02-28'},
  {year: 2025, start: '2024-01-01', end: '2024-02-28'}
];

// Process one epoch as example (2024)
var currentEpoch = epochs[0]; // Change index to process different years

var landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
  .filterBounds(aoi)
  .filterDate(currentEpoch.start, currentEpoch.end)
  .filter(ee.Filter.lt('CLOUD_COVER', 20))
  .map(applyScaleFactors)
  .map(maskL8sr);

// Create median composite for the epoch
var composite = landsat.median().clip(aoi);

// Visualization
Map.centerObject(aoi, 11);

var visParams = {
  bands: ['SR_B4', 'SR_B3', 'SR_B2'],
  min: 0.0,
  max: 0.3,
  gamma: 1.4
};

Map.addLayer(aoi, {color: 'yellow'}, 'AOI', false);
Map.addLayer(composite, visParams, currentEpoch.year + ' Composite');

// Check data availability
print('Epoch:', currentEpoch.year);
print('Images available:', landsat.size());
print('Date range:', landsat.aggregate_array('DATE_ACQUIRED'));
print('Composite bands:', composite.bandNames());