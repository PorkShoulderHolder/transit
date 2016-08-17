// $('#sidebar-bottom').sidebar({side: 'bottom'});
var Controls = React.createClass({
  render: function(){
    return (
      <div className="controls">
        <a href="#" id="flows" className="button">congestion</a>
        <a href="#" id="stations" className="button">stations</a>
        <a href="#" id="entrances" className="button">entrances</a>
      </div>
      )
  }
});
var DateElement = React.createClass({
  getInitialState: function() {
      return {data: {updated:""}};
    },
  componentWillMount: function(){
    set_update_date = (date) => {
        this.setState({data: {updated: date}});
      };
  },
  render: function(){
    return (<div className="date">Data last updated the week of {this.state.data.updated}</div>)
  }
      
})
var SidebarBottom = React.createClass({
    getInitialState: function() {
    	return {data: {station: {Label:"Station Data", Line:"gravy", Division:"IRT", ENTRIES:0, EXITS:0}, updated:""}};
  	},
  	componentWillMount: function(){
  		set_highlight = (data) => {
  			this.setState({data: {station: data, updated: this.state.data.updated}});
  		};
  	},
    render: function () {
    	var info = this.state.data.station.Label.split('_');
        return (
        	<div className="container">
            <div className="info">
            </div>
	          <Controls />
            <div className="text">
              <div className="heading">
  	        		{info[0]}
  	      		</div>
  	      		<div className="caption">
  	        		Provides service to the {info[1]} train(s) 
  	        		and is part of the {this.state.data.station.Line} line 
  	        		and {this.state.data.station.Division} divsion
  	      		</div>
            </div>
            <div className="infographics">
              <div className="knob">
                 <div className="label">Morning entries</div>
	      		     <input type="text" value={parseInt(this.state.data.station.ENTRIES)} className="dial" ></input>
              </div>
              <div className="knob">
                 <div className="label">Evening entries</div>
                 <input type="text" value={parseInt(this.state.data.station.EXITS)} className="dial"></input>
      		    </div>
            </div>
          </div>
        )
    }
});



ReactDOM.render(<SidebarBottom />, document.getElementById('sidebar-bottom'));
ReactDOM.render(<DateElement />, document.getElementById('sidebar-top'));
Waves.attach('.button', ['waves-button']);
Waves.init();
$(".waves-button").css("padding",".6em .6em");

