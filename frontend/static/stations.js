var StationsGroup = function(stations){
    this.stations = stations;
    this.active = false;
    this.entrances_actice = false;
}

StationsGroup.prototype.show_stations_on = function(map){
    map.setLayoutProperty('stations', 'visibility', 'visible');
    this.active = true;
}

StationsGroup.prototype.hide_stations_on = function(map){
    map.setLayoutProperty('stations', 'visibility', 'none');
    this.active = false;
}

StationsGroup.prototype.show_entrances_on = function(map){
    map.setLayoutProperty('entrances', 'visibility', 'visible');
    this.entrances_active = true;
}

StationsGroup.prototype.hide_entrances_on = function(map){
    map.setLayoutProperty('entrances', 'visibility', 'none');
    this.entrances_active = false;
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


StationsGroup.prototype.features = function(){
    var k = -1;
    return this.stations.map(function(station){
        k++;
        return {
            "type":"Feature",
            "properties":{"name": k.toString()},
            "geometry":{
                "type": "MultiPoint",
                "coordinates": [[station.longitude, station.latitude]]
            }
        };
    });
}

StationsGroup.prototype.add_stations = function(map){
    var size_multiplier = 2.5;
    var self = this;
    var rad_scale = [[10, size_multiplier * 1],
            [12, size_multiplier * 2], [14, size_multiplier * 3], [15, size_multiplier * 3], [16, size_multiplier * 5],
            [17, size_multiplier * 7], [18, size_multiplier * 9]];
    map.addSource('stations', {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features":self.features()
        }
    });

    map.addLayer({
        "id": "stations",
        "source": "stations",
        "type": "circle",
        "paint": {
            "circle-radius":  {"stops": rad_scale},
            "circle-color": "#18c8ca",
            "circle-opacity": {"stops": [[10, 0.7], [18, 1]]}
        }
    });
    map.addLayer({
        "id": "station_highlight",
        "source": "stations",
        "type": "circle",
        "paint": {
            "circle-radius":  {"stops": rad_scale.map(function(s){ return [s[0], s[1] * 2] })},
            "circle-color": "#ff414d",
            "circle-opacity": 1
        },
        "filter": ["==", "name", ""]
    });
}



StationsGroup.prototype.add_entrances = function(map){
    var size_multiplier = 0.6;
    var self = this;
    map.addSource('entrances', {
        "type": "geojson",
        "data": {
            "type": "MultiPoint",
            "coordinates":self.entrances()
        }
    });

    map.addLayer({
        "id": "entrances",
        "source": "entrances",
        "type": "circle",
        "paint": {
            "circle-radius":  {"stops": [[10, size_multiplier * 1],
            [12, size_multiplier * 2], [14, size_multiplier * 3], [15, size_multiplier * 3], [16, size_multiplier * 5],
            [17, size_multiplier * 7], [18, size_multiplier * 9]]},
            "circle-color": "#fee08b",
            "circle-opacity": {"stops": [[10, 0.4], [18, 0.9]]}
        }
    });
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