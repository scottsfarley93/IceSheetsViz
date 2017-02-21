fs = require('fs');
// geojson = require('geojson')


filename = 'geojson/ice5g_v1.2_00.0k_1deg.tif.geojson'

function addField(filename, fieldName, fieldValue){
  //add a field to the properties of the geojson file
  fs.readFile(filename, 'utf8', function (err, data) { //open the file
      if (err) throw err;

      //read the json -> assumes valid json
      var collection = JSON.parse(data);
      var features = collection.features
      for (var i=0; i < features.length; i++){
        //iter through all features
        thisFeature = features[i];
        thisProps = thisFeature.properties

        //set key and value
        thisProps[fieldName] = fieldValue

        //ensure geojson is legit
        geom = thisFeature.geometry
        coordinates = geom.coordinates[0]
        for (var p=0; p < coordinates.length; p++){
          q = coordinates[p]
          console.log(q)
          if (q[0] > 180){
            thisFeature.geometry.coordinates[0][p][0] = 180
          }
          if (q[0] < -180){
            thisFeature.geometry.coordinates[0][p][0] = -180
          }
          if (q[1] > 90){
            thisFeature.geometry.coordinates[0][p][1] = 90
          }
          if (q[1] < -90){
            thisFeature.geometry.coordinates[0][p][1] = -90
          }
        }
      } //end loop

      //once finished, write the modified file
      mod = JSON.stringify(collection)
      fs.writeFile(filename, mod, function(err){
        if (err) throw err;
        console.log("Wrote file " + filename)
      }) //end async write file
  }); // end async read file
} //end function


//read the directory and apply to all
inDir = "geojson"
fs.readdir(inDir, function(err, files){
  if (err) throw err;
  files.forEach(function(file, index){
    fdcomp = file.split("_")
    age = fdcomp[2]
    years = +(age.replace("k", "")) * 1000;
    infile = "geojson/" + file
    addField(infile, "Age", years)
  })
})

//
