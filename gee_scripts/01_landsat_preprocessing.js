//=====================================================
// NAIROBI CARBON-COOLING PROJECT
// script 01: landsat preprocessing with county boundary
//=====================================================

// 1: load nairobi county boundary from uploaded asset (https://open.africa/dataset/kenya-administrative-boundaries)
//var counties = ee.FeatureCollection('projects/de-africa/assets/KE_COUNTIES');

// filter for nairobi county specifically
var nairobi = KE_COUNTIES.filter(ee.Filter.eq('ADM1_EN', 'NAIROBI'));
print(nairobi);

// visualize the boundary
Map.centerObject(nairobi, 11);
Map.addLayer(nairobi, {color: 'yellow'}, 'Nairobi County Boundary');

//============================================
// COMPLETE PREPROCESSING SCRIPT
//============================================

// 2: scaling functions
function applyScaleFactors(image) {
  var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
  var thermalBand = image.select('ST_B10').multiply(0.00341802).add(149.0);
  return image.addBands(opticalBands, null, true)
              .addBands(thermalBand, null, true);
}

// 3: cloud masking
function maskL8sr(image) {
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);
  return image.updateMask(qaMask).updateMask(saturationMask);
}

// 4: define epochs (Q1 hot dry season)
var epochs = [
  {year: 2015, start: '2015-01-01', end: '2015-03-31', name: '2015_Q1'},
  {year: 2018, start: '2018-01-01', end: '2018-03-31', name: '2018_Q1'},
  {year: 2021, start: '2021-01-01', end: '2021-03-31', name: '2021_Q1'},
  {year: 2024, start: '2024-01-01', end: '2024-03-31', name: '2024_Q1'}
];

// 5: load landsat collection
var landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2");

// 6: create composite function
function createEpochComposite(epoch) {
  var composite = landsat
    .filterBounds(nairobi) 
    .filterDate(epoch.start, epoch.end)
    .filter(ee.Filter.lt('CLOUD_COVER', 20))
    .map(applyScaleFactors)
    .map(maskL8sr)
    .median()
    .clip(nairobi); 
  
  return composite.set({
    'year': epoch.year,
    'season': 'Q1_HotDry',
    'epoch_name': epoch.name
  });
}

// 7: generate all composites
var composite2015 = createEpochComposite(epochs[0]);
var composite2018 = createEpochComposite(epochs[1]);
var composite2021 = createEpochComposite(epochs[2]);
var composite2024 = createEpochComposite(epochs[3]);

// 8: vizualization
var visParams = {
  bands: ['SR_B4', 'SR_B3', 'SR_B2'],
  min: 0.0,
  max: 0.3,
  gamma: 1.4
};

Map.addLayer(nairobi, {color: 'yellow'}, 'Nairobi County', true);
Map.addLayer(composite2024, visParams, '2024 Q1 True Color', true);
Map.addLayer(composite2015, visParams, '2015 Q1 True Color', false);

// 9: data quality checks
print('=== DATA AVAILABILITY ===');
epochs.forEach(function(epoch) {
  var count = landsat
    .filterBounds(nairobi)
    .filterDate(epoch.start, epoch.end)
    .filter(ee.Filter.lt('CLOUD_COVER', 20))
    .size();
  print(epoch.name + ' images available:', count);
});

print('=== COMPOSITE PROPERTIES ===');
print('2024 Composite bands:', composite2024.bandNames());
print('2024 Composite metadata:', composite2024.toDictionary());

// 10. lst quality checks
var lst2024 = composite2024.select('ST_B10').subtract(273.15); // Kelvin to Celsius

var lstStats = lst2024.reduceRegion({
  reducer: ee.Reducer.percentile([5, 25, 50, 75, 95]),
  geometry: nairobi,
  scale: 30,
  maxPixels: 1e9,
  bestEffort: true
});

print('=== 2024 LST STATISTICS (°C) ===');
print('LST Range:', lstStats);
// Expected: p5 ~18-22°C, p50 ~26-30°C, p95 ~35-42°C