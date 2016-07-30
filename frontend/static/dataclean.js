function clean_paths(data){
    var paths = [];
    return data.edges.map(function(e){
        var src = data.nodes[e.source];
        var target = data.nodes[e.target];
        return new GeoFlow(e.source, e.target, parseFloat(e.flow), parseFloat(src.latitude), parseFloat(src.longitude),
        parseFloat(target.latitude), parseFloat(target.longitude), parseFloat(e.distances), parseFloat(e.travel_time));
    });
}

function clean_stations(data){
    var stations = [];
    for( key in data.nodes ){
        var station = data.nodes[key];
        var entrances = JSON.parse(station.station_access.replace(/\(/g,"[").replace(/\)/g,"]"));
        entrances = entrances.map(function(e){ return [e[1], e[0]]})
        stations.push(new Station(parseFloat(station.latitude), parseFloat(station.longitude), entrances, station));
    }
    return stations;
}