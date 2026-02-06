// ==============================================
// Optimized Temporal Strategy: Q1 Hot Dry Season
// ==============================================

var aoi = ee.Geometry.Rectangle([36.65, -1.45, 37.10, -1.15]);

// Scaling functions
function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBand = image.select('ST_B10').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
              .addBands(thermalBand, null, true);
}

function maskL8sr(image) {
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);
  return image.updateMask(qaMask).updateMask(saturationMask);
}

// Define epochs - Q1 Hot Dry Season (Jan-Mar)
var epochs = [
  {year: 2015, start: '2015-01-01', end: '2015-03-31'},
  {year: 2018, start: '2018-01-01', end: '2018-03-31'},
  {year: 2021, start: '2021-01-01', end: '2021-03-31'},
  {year: 2024, start: '2024-01-01', end: '2024-03-31'}
];

// Load Landsat 8 Collection
var landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2");

// Function to create composite for each epoch
function createEpochComposite(epoch) {
  var composite = landsat
    .filterBounds(aoi)
    .filterDate(epoch.start, epoch.end)
    .filter(ee.Filter.lt('CLOUD_COVER', 20))
    .map(applyScaleFactors)
    .map(maskL8sr)
    .median()
    .clip(aoi);
  
  return composite.set('year', epoch.year);
}

// Generate composites for all epochs
var composites = epochs.map(createEpochComposite);

// Work with 2024 composite for now
var composite2024 = ee.Image(composites[3]);

// Visualization
Map.centerObject(aoi, 11);

var visParams = {
  bands: ['SR_B4', 'SR_B3', 'SR_B2'],
  min: 0.0,
  max: 0.3,
  gamma: 1.4
};

Map.addLayer(aoi, {color: 'yellow'}, 'AOI', false);
Map.addLayer(composite2024, visParams, '2024 Q1 Composite');

// Data availability check
epochs.forEach(function(epoch) {
  var count = landsat
    .filterBounds(aoi)
    .filterDate(epoch.start, epoch.end)
    .filter(ee.Filter.lt('CLOUD_COVER', 20))
    .size();
  print(epoch.year + ' Q1 images:', count);
});

print('2024 Composite bands:', composite2024.bandNames());