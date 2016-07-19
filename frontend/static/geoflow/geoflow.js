
function default_multiplicity_fn(flow, distance){
    return Math.ceil(flow * 0.00000006 * distance );
}

function default_speed_fn(speed){
    return speed;
}

var GeoFlow = function(src, target, flow, src_lat, src_lng, target_lat, target_lng, distance, travel_time,
  flow_multiplicity_fn, flow_speed_fn ){
    this.src = src;
    this.target = target;
    this.flow = flow;
    this.t = 0;
    this.src_lat = src_lat;
    this.src_lng = src_lng;
    this.distance = distance;
    this.travel_time = travel_time;
    this.target_lat = target_lat;
    this.target_lng = target_lng;
    this.position = [src_lat, src_lng];
    if(flow_multiplicity_fn == undefined){
        this.flow_multiplicity_fn = default_multiplicity_fn;
    }
    else{
        this.flow_multiplicity_fn = flow_multiplicity_fn;
    }
    if(flow_speed_fn == undefined){
        this.flow_speed_fn = default_speed_fn;
    }
    this.dots = this.generate_dots();

}

GeoFlow.prototype.generate_dots = function(){
    var dots = [];
    var i = this.flow_multiplicity_fn(this.flow, this.distance);
    var speed = this.flow_speed_fn(1/this.travel_time);
    var j = i;
    self = this;
    while(i > 0){
        dots.push(new Dot(i / j, speed, self.src_lat, self.src_lng, self.target_lat, self.target_lng));
        i--;
    }
    return dots;
}

GeoFlow.prototype.update = function(parent_speed){
    var i = 0;
    var j = this.dots.length;
    var speed = this.flow_speed_fn(0.1 / this.travel_time);
    var self = this;
    this.dots.forEach(function(dot){
        dot.t = dot.t + speed * parent_speed;
        if(dot.t > 1) {
            dot.t = 0;
        }
        dot.update();
        i++;
    });
}

var Dot = function(start_t, start_speed, src_lat, src_lng, target_lat, target_lng){
    this.src_lat = src_lat + Math.random() * 0.001;
    this.src_lng = src_lng  + Math.random() * 0.001;;
    this.target_lat = target_lat  + Math.random() * 0.001;;
    this.target_lng = target_lng  + Math.random() * 0.001;;
    this.position = [this.src_lat, this.src_lng];
    this.speed = start_speed;
    this.t = start_t;
}

Dot.prototype.update = function(t){
    // t: float in [0,1]
    var lat_diff = (this.src_lat - this.target_lat) * this.t;
    var lng_diff = (this.src_lng - this.target_lng) * this.t;
    this.position = [this.src_lng - lng_diff, this.src_lat - lat_diff];
}

var FlowSystem = function(paths){
    // paths: list of GeoFlow objects
    this.paths = paths;
    this.last_update = new Date;
    this.t = 0;
    this.speed = 1;
}

FlowSystem.prototype.update = function(){
    var t = this.t;
    var pos = [];
    var self = this;
    var d = new Date;
    this.paths.forEach(function(path){
        path.t += ((d) - self.last_update) * self.speed;
//        if(path.t > 1) path.t = 0;
        path.update(self.speed);
        path.dots.forEach(function(dot){
            pos.push(dot.position);
        });
    });
    this.last_update = new Date;
    this.positions = pos;
}

