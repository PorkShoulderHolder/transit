
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
var set_info = undefined;
var lastLoop = new Date;
function gameLoop() {
    var thisLoop = new Date;
    var fps = 1000 / (thisLoop - lastLoop);
    lastLoop = thisLoop;
    //console.log(fps);
}




map.on('load', function () {
    
    $(".dial").knob({
        "max":"600000", 
        "height":100, 
        "width":100, 
        "thickness":0.12,
        "readOnly":true, 
        "fgColor":"#000000",
        "fontSize":16,
        "font":"Montserrat"
    });
    $("#sidebar-bottom").css("display","block")

    $.get("flowdata", function(d){
        var json_d = JSON.parse(d);
        var paths = clean_paths(json_d);
        var stations = clean_stations(json_d);

        station_group = new StationsGroup(stations);
        transit_flows = new FlowSystem(paths);

        station_group.add_stations(map);
        station_group.add_entrances(map);
        transit_flows.setup_flows_on(map);
        transit_flows.hide(map);
        station_group.hide_stations_on(map);
        station_group.hide_entrances_on(map);
        map.on('zoom', function () {
            transit_flows.speed = (21.0 - map.transform.zoom) * 0.1 - 0.098;
        });

        map.on("click", function(e){
            var features = map.queryRenderedFeatures(e.point, { layers: ["stations"] });
            if (features.length) {
                var meta = station_group.stations[parseInt(features[0].properties.name)];
                map.setFilter("station_highlight", ["==", "name", features[0].properties.name]);
                set_highlight(meta.stats);
                $(".dial").trigger('change');
                $(".dial").css("font-size",15);
                // $('#sidebar-bottom').trigger("sidebar:open");
            }
        });
        $("#stations").hover(
            function(){
                $(".info").html(
                    "<i class='fa fa-question-circle-o' style='font-size:24px; margin-right:8px; display:inline'></i>" + 
                    "<div style='display:inline'>Click on stations on the map to show turnstile data</div>"
                );
            }, 
            function(){
                $(".info").html("");
            }
        );

        $("#flows").hover(
            function(){
                $(".info").html(
                    "<i class='fa fa-question-circle-o' style='font-size:24px; margin-right:8px; display:inline'></i>" +
                    "<div style='display:inline'>The number of dots for each track segment is proportional to the minimum cost ridership " + 
                    "suggested by the turnstile data</div>"
                );
            }, 
            function(){
                $(".info").html("");
            }
        );

        $("#flows").on('click', function(e){
            if (transit_flows.animation_id){
                $("#flows").css("color","black");
                $("#flows").css("background","#dddddd");
                transit_flows.hide(map);
            } 
            else{
                $("#flows").css("color","whitesmoke");
                $("#flows").css("background","#dd7c33");
                transit_flows.show_on(map);
            }
        });
        $("#stations").on('click', function(e){
            if (station_group.active){
                $("#stations").css("color","black");
                $("#stations").css("background","#dddddd");

                station_group.hide_stations_on(map);
            } 
            else{
                $("#stations").css("color","whitesmoke");
                $("#stations").css("background","#18c8ca");
                station_group.show_stations_on(map);
            }
        });
        $("#entrances").on('click', function(e){
            if (station_group.entrances_active){
                $("#entrances").css("color","black");
                $("#entrances").css("background","#dddddd");

                station_group.hide_entrances_on(map);
            } 
            else{
                $("#entrances").css("color","whitesmoke");
                $("#entrances").css("background","#fee08b");
                station_group.show_entrances_on(map);
            }
        });
    });
});
