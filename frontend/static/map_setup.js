
mapboxgl.accessToken = 'pk.eyJ1Ijoic2Nod2Fua3N0YSIsImEiOiIwTXZySHdVIn0.2RSD-PKkyPIboteVeFcZ2g';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v9',
    center: [-73.97426810851839, 40.69680336061833],
    zoom: 11
});

var radius = 20;

var lastLoop = new Date;
function gameLoop() {
    var thisLoop = new Date;
    var fps = 1000 / (thisLoop - lastLoop);
    lastLoop = thisLoop;
    //console.log(fps);
}

function setup_flows(ff){
    map.addSource('flows', {
        "type": "geojson",
        "data": ff(0)
    });

    map.addLayer({
        "id": "flows",
        "source": "flows",
        "type": "circle",
        "paint": {
            "circle-radius":  {"stops": [[10, 1], [12, 2],  [14, 3], [15, 3], [16, 5], [17, 7], [18, 9]]},
            "circle-color": "#dd7c33",
            "circle-opacity": {"stops": [[10, 0.4], [18, 0.9]]}
        }
    });
}

function add_stations(station_group){
    var size_multiplier = 4;
    map.addSource('stations', {
        "type": "geojson",
        "data": {
            "type": "MultiPoint",
            "coordinates":station_group.locations()
        }
    });

    map.addLayer({
        "id": "stations",
        "source": "stations",
        "type": "circle",
        "paint": {
            "circle-radius":  {"stops": [[10, size_multiplier * 1],
            [12, size_multiplier * 2], [14, size_multiplier * 3], [15, size_multiplier * 3], [16, size_multiplier * 5],
            [17, size_multiplier * 7], [18, size_multiplier * 9]]},
            "circle-color": "#007c33",
            "circle-opacity": {"stops": [[10, 0.4], [18, 0.9]]}
        }
    });
}

function add_entrances(station_group){
    var size_multiplier = 1;
    map.addSource('entrances', {
        "type": "geojson",
        "data": {
            "type": "MultiPoint",
            "coordinates":station_group.entrances()
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
            "circle-color": "#ff0033",
            "circle-opacity": {"stops": [[10, 0.4], [18, 0.9]]}
        }
    });
}



map.on('load', function () {

    $.get("flowdata", function(d){
        var json_d = JSON.parse(d);
        var paths = clean_paths(json_d);
        var stations = clean_stations(json_d);

        var station_group = new StationsGroup(stations);
        var transit_flows = new FlowSystem(paths);

        function flow_animate(angle) {
            transit_flows.update();
            var coordinates = transit_flows.positions;
            return {
                "type": "MultiPoint",
                "coordinates":coordinates
            };
        }

//        add_stations(station_group);
//        add_entrances(station_group);
        setup_flows(flow_animate);

        function animateMarker(timestamp) {
            fdata = flow_animate(timestamp / 1000);
            map.getSource('flows').setData(fdata);
            gameLoop();
            requestAnimationFrame(animateMarker);
        }
        map.on('zoom', function () {
            transit_flows.speed = (21.0 - map.transform.zoom) * 0.1 - 0.098;
            console.log(transit_flows.speed);
        });
        animateMarker(0);
    });

});