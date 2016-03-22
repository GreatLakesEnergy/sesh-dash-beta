// Alerts

var TableRow = React.createClass({

    render: function() {
        return(
            <tr className="modal-toggle" classID={this.props.dataId}>
                <td>{this.props.site}</td>
                <td>{this.props.alert}</td>
                <td>{this.props.date}</td>
            </tr>
        );
    }
});

var TableRowHeader = React.createClass({
  render: function(){
    return(
      <thead>
        <tr>
          <th>Site</th>
          <th>Alert</th>
          <th>Time</th>
        </tr>
      </thead>
    );
  },
});

var AlertList = React.createClass({
    render: function() {
        var alertNodes = this.props.data.map(function(alert)  {
            return(
                <TableRow site={alert.site} alert={alert.alert} date={alert.date} dataId={alert.alertId}/>
            );
        });

        return (
            <table className="table table-hover table-striped">
              <TableRowHeader />
              <tbody>{alertNodes}</tbody>
            </table>
        );
    }
});

// $('.silence-alert').click(function(){
//   getLatestAlerts();
// });



const REFRESH_TIME = 300000;
var alertsJsonData = {csrfmiddlewaretoken: csrftoken,
                      site_id: active_site_id,
                     };

getLatestAlerts();

function getLatestAlerts () {
    $.post('/get-alerts', alertsJsonData,function(data) {
        console.log(data);
        var jsonData = JSON.parse(data);
        ReactDOM.render(
            <AlertList data={jsonData} />,
            document.getElementById('alerts-container')
        );
    });
   setTimeout(getLatestAlerts, REFRESH_TIME) // Get alerts for every five minutes
}


$('.silence-alert').click(function(){
   setTimeout(getLatestAlerts, 1000);
});

// Status Card
var LatestBoMHeader = React.createClass({
    render: function(){
      return(
        <thead>
          <tr>
            <th>Metric</th>
            <th>Status</th>
          </tr>
        </thead>
      );
    }
});


var LatestBoMData = React.createClass({
    render: function(){
        var BoMDataRows = this.props.data.map(function(BoMDataRow){
            return(
                 <BoMLatestDataRow item={BoMDataRow.item} value={BoMDataRow.value} />
            );
        });
        return(
          <table className="table table-striped">
                <LatestBoMHeader />
                <tbody>{BoMDataRows}</tbody>
          </table>
        );
    }
});


var BoMLatestDataRow = React.createClass({
    render: function() {
        return (
            <tr>
                <td>{this.props.item}</td>
                <td>{this.props.value}</td>
            </tr>
        );
    },
});



function getLatestBoMData(){
    var bomJsonData = {
            csrfmiddlewaretoken: csrftoken,
        };

    $.post('/get-latest-bom-data', bomJsonData, function(data){
        data = JSON.parse(data);
        console.log(data);
        ReactDOM.render(
           <LatestBoMData data={data} />,
           document.getElementById('latest-bom-data')
        );
    });
    setTimeout(getLatestBoMData, REFRESH_TIME);
};

getLatestBoMData();
