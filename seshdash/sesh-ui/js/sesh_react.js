// Alerts 

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
        console.log(this.props.data);
        var alertNodes = this.props.data.map(function(alert)  {
            return(
                <TableRow site={alert.site} alert={alert.alert} date={alert.date} dataId={alert.alertId}/>
            );
        });

        return (
            <div> {alertNodes} </div>
        );
    }
});

$('.silence-alert').click(function(){
  getLatestAlerts();
});



const alertRefreshTime = 300000;
var alertsJsonData = {csrfmiddlewaretoken: csrftoken,
                      site_id: active_site_id,
                     };

getLatestAlerts();

function getLatestAlerts () {
    $.post('/get-alerts', alertsJsonData,function(data) {
        var jsonData = JSON.parse(data);
        console.log(jsonData);
        ReactDOM.render(
            <AlertList data={jsonData} />,
            document.getElementById('alerts-container')
        );
    });
   setTimeout(getLatestAlerts, alertRefreshTime) // Get alerts for every five minutes
}



// Status Card 
var LatestBoMData = React.createClass({
    render: function(){
        return(
            <div className="latestBoMData">
                <BoMLatestDataRow item="battery Voltage" value="012" />
            </div>
        );
    }
});


var BoMLatestDataRow = React.createClass({
    render: function() {
        return(
            <tr>
                <td>{this.props.item}</td>
                <td>{this.props.value}</td>
            </tr>
        );
    }
});


function getLatestBoMData(){};


ReactDOM.render(
    <LatestBoMData />,
    document.getElementById('latest-bom-data')
);
