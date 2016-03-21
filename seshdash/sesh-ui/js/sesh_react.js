

// Alert React Js

var data = [
    {site:"Mukuyu", alert:"Battery Voltage less than 30", date:"6 hours ago" },
    {site:"Mukuyu", alert:"Battery Voltage less than 30", date:"6 hours ago" },
    {site:"Mukuyu", alert:"Battery Voltage less than 30", date:"6 hours ago" },
];

var AlertsContainer = React.createClass({

    render: function() {
        return (
            <div className="panel panel-danger">
                <PanelHeading>System Alerts </PanelHeading>
	        <div className="panel-body system-alerts">
                    <div className="table-responsive">
                        <table className="table table-hover table-fixed">
                            <thead>
                                <TableRow site="Site" alert="Alert" date="Date"></TableRow>
                            </thead>
                            <AlertList data={this.props.data} />
                        </table>
                    </div>
                </div>
            </div>
        );
    },
});


var PanelHeading = React.createClass({

    render: function() {
        return (
            <div className="panel-heading">
                <i className="fa fa-exclamation-triangle fa-fw"></i>
                {this.props.children}
            </div>
        );
    }

});



var TableRow = React.createClass({

    render: function() {
        console.log(this.props.alertId);
        return(
            <tr className="modal-toggle" classID={this.props.dataId}>
                <td>{this.props.site}</td>
                <td>{this.props.alert}</td>
                <td>{this.props.date}</td>
            </tr>
        );
    }
});


var AlertList = React.createClass({
    render: function() {
        var alertNodes = this.props.data.map(function(alert)  {
            return(
                <TableRow site={alert.site} alert={alert.alert} date={alert.date} dataId={alert.alertId}/>
            );
        });

        return (
            <tbody>
                {alertNodes}
            </tbody>
        );
    }
});

$('.silence-alert').click(function(){
  getLatestAlerts();
});




var alertsJsonData = {csrfmiddlewaretoken: csrftoken,
                      site_id: active_site_id,
                     };

getLatestAlerts();
function getLatestAlerts () {
    $.post('/get-alerts', alertsJsonData,function(data) {
        var jsonData = JSON.parse(data);
        ReactDOM.render(
            <AlertsContainer data={jsonData} />,
            document.getElementById('alerts-container')
        );
    });
   setTimeout(getLatestAlerts, 300000) // Get alerts for every five minutes
}

