
mapboxgl.accessToken = 'pk.eyJ1Ijoic2Nod2Fua3N0YSIsImEiOiIwTXZySHdVIn0.2RSD-PKkyPIboteVeFcZ2g';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/dark-v9',
    center: [-73.97426810851839, 40.69680336061833],
    zoom: 11
});

var radius = 20;
var station_group = undefined;
var transit_flows = undefined;
var set_highlight = undefined;
var lastLoop = new Date;
function gameLoop() {
    var thisLoop = new Date;
    var fps = 1000 / (thisLoop - lastLoop);
    lastLoop = thisLoop;
    //console.log(fps);
}




map.on('load', function () {

    $.get("flowdata", function(d){
        var json_d = JSON.parse(d);
        var paths = clean_paths(json_d);
        var stations = clean_stations(json_d);

        station_group = new StationsGroup(stations);
        transit_flows = new FlowSystem(paths);

        station_group.add_stations(map);
        // station_group.add_entrances(map);
        // transit_flows.setup_flows_on(map);
        // transit_flows.start_animation_on(map);
        console.log(station_group.features())
        map.on('zoom', function () {
            transit_flows.speed = (21.0 - map.transform.zoom) * 0.1 - 0.098;
            console.log(transit_flows.speed);
        });
        map.on("click", function(e){
            var features = map.queryRenderedFeatures(e.point, { layers: ["stations"] });
            if (features.length) {
                map.setFilter("station_highlight", ["==", "name", features[0].properties.name]);
                var meta = station_group.stations[parseInt(features[0].properties.name)];
                set_highlight(meta.stats);
                $(".dial").knob({
                    "max":"600000", 
                    "height":100, 
                    "width":100, 
                    "thickness":0.1,
                    "readOnly":true, 
                    "fgColor":"#000000",
                    "fontSize":16,
                    "font":"Montserrat"
                });

                $(".dial").trigger('change');
                $(".dial").css("font-size",15);
                $('#sidebar-bottom').trigger("sidebar:open");

            }
        });
    });
});
