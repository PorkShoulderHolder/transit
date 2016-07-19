function clean_paths(data){
    var paths = [];
    return data.edges.map(function(e){
        var src = data.nodes[e.source];
        var target = data.nodes[e.target];
        return new GeoFlow(e.source, e.target, parseFloat(e.flow), parseFloat(src.latitude), parseFloat(src.longitude),
                            parseFloat(target.latitude), parseFloat(target.longitude), parseFloat(e.distances), parseFloat(e.travel_time));
    });
}