// ============================================
// NAIROBI CARBON-COOLING PROJECT
// Script 01: Landsat Preprocessing & AOI Setup
// ============================================

// 1. Define Area of Interest (Nairobi)
var aoi = ee.Geometry.Rectangle([
  36.65,  // West
  -1.45,  // South  
  37.10,  // East
  -1.15   // North
]);

// 2. Load Landsat 8 Collection 2 Surface Reflectance (>TOA)
var landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")  // L2 = Surface Reflectance
  .filterBounds(aoi)
  .filterDate('2020-06-01', '2020-12-31')  // Use recent dry season data
  .filter(ee.Filter.lt('CLOUD_COVER', 20))  // Less than 20% clouds
  .map(function(image) {
    // Apply scale factors for L2 data
    var opticalBands = image.select('SR_B.').multiply(0.0000275).add(-0.2);
    var thermalBands = image.select('ST_B.*').multiply(0.00341802).add(149.0);
    return image.addBands(opticalBands, null, true)
                .addBands(thermalBands, null, true);
  });

// 3. Cloud masking function
function maskL8sr(image) {
  var qaMask = image.select('QA_PIXEL').bitwiseAnd(parseInt('11111', 2)).eq(0);
  var saturationMask = image.select('QA_RADSAT').eq(0);
  return image.updateMask(qaMask).updateMask(saturationMask);
}

// 4. Apply cloud mask and get least cloudy image
var image = landsat8.map(maskL8sr)
                    .median()  // Or use .first() for single scene
                    .clip(aoi);

// 5. Visualization
Map.centerObject(aoi, 11);

// True color visualization (for Surface Reflectance)
var visParams = {
  bands: ['SR_B4', 'SR_B3', 'SR_B2'],  // RGB
  min: 0.0,
  max: 0.3,  // SR values are 0-1 range
  gamma: 1.4
};

Map.addLayer(aoi, {color: 'yellow'}, 'AOI Boundary', false);
Map.addLayer(image, visParams, 'Nairobi True Color');

// Quick stats
var count = landsat8.size();
print(count);