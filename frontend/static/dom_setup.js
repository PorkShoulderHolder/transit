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

var SidebarBottom = React.createClass({
    getInitialState: function() {
    	return {data: {Label:"Station Data", Line:"gravy", Division:"IRT", ENTRIES:0, EXITS:0}};
  	},
  	componentWillMount: function(){
  		set_highlight = (data) => {
  			this.setState({data: data});
  		}
  	},
    render: function () {
    	var info = this.state.data.Label.split('_');
        return (
        	<div className="container">
	          <Controls />
            <div className="text">
              <div className="heading">
  	        		{info[0]}
  	      		</div>
  	      		<div className="caption">
  	        		Provides service to the {info[1]} train(s) 
  	        		and is part of the {this.state.data.Line} line 
  	        		and {this.state.data.Division} divsion
  	      		</div>
            </div>
            <div className="infographics">
              <div className="knob">
                 <div className="label">Morning entries</div>
	      		     <input type="text" value={this.state.data.ENTRIES} className="dial" ></input>
              </div>
              <div className="knob">
                 <div className="label">Evening entries</div>
                 <input type="text" value={this.state.data.EXITS} className="dial"></input>
      		    </div>
            </div>
            <div className="info">
              <i className="fa fa-question-circle-o" style={{"font-size":"24px", "margin":"8px"}}></i>
              blach the don is gonna kill u
            </div>
          </div>
        )
    }
});



ReactDOM.render(<SidebarBottom />, document.getElementById('sidebar-bottom'));

Waves.attach('.button', ['waves-button']);
Waves.init();
$(".waves-button").css("padding",".6em .6em");

