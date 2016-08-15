$('#sidebar-bottom').sidebar({side: 'bottom'});
var SidebarBottom = React.createClass({
    getInitialState: function() {
    	return {data: {Label:"Chambers st_ACE", Line:"BWAY", Division:"IRT"}};
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
	      		     <input type="text" value={this.state.data.ENTRIES} className="dial" ></input>
              </div>
              <div className="knob">
                 <input type="text" value={this.state.data.EXITS} className="dial"></input>
      		    </div>
            </div>
          </div>
        )
    }
});


ReactDOM.render(<SidebarBottom />, document.getElementById('sidebar-bottom'));
