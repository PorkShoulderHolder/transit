var StationsGroup = function(stations){
    this.stations = stations;
}

StationsGroup.prototype.locations = function(){
    return this.stations.map(function(station){
        return [station.longitude, station.latitude];
    });
}

StationsGroup.prototype.entrances = function(){
    var entrances = []
    this.stations.forEach(function(station){
        entrances = entrances.concat(station.entrances);
    });
    return entrances;
}

var Station = function(lat, lng, entrances, stats){
    // lat: station latitude
    // lng: station longitude
    // entrances: list of latlng pairs of each stations entrance
    // stats: key/values pairs for different numerical stats
    this.latitude = lat;
    this.longitude = lng;
    this.entrances = entrances;
    this.stats = stats;
}

Station.prototype.highlight = function(){

}