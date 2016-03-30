/*
 * Barchart for energy production
*/
function ready_graph_data(data,x_value,y_value){
    var graph_data = [];
    for (var i=0; i < data.length; i++)
    {
         var data_point = {y:data[i]["fields"][x_value],a:data[i]["fields"][y_value]};
     graph_data.push(data_point);
    }
    return graph_data;
  }


// energy production graph
/* NOTE commenting out for now, switching out nvd3 graphs
Morris.Bar({
      element: 'energy-production-last-5-days',
      data: ready_graph_data(power_data,'time','w_production'),
  xkey: 'y',
  ykeys: ['a'],
  labels: ['wh']
});

//cloudcover forecast
Morris.Bar({
  element: 'cloud-cover-forecast',
  data: ready_graph_data(weather_data,'date','cloud_cover'),
  xLabels : 'day',
  xkey: 'y',
  ykeys: ['a'],
  labels: ['Cloud Cover %']
});
*/
//nano bar
        var myfunction=function(){
        var options={
              bg :"#4AA0BD",
                    }
        var nanobar =new Nanobar(options);
        var i=1;
        for(i=1;i<=99;i++){
			   nanobar.go(i);
                          }  
                            
            }
         $("a").click(myfunction);
         

        

/*
 High Chart Draw Function
*/
function get_high_chart(date,pv,cloud)
{

$('#containerhigh').highcharts({
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: ' Daily PV Production with Cloud cover forecast In High Chart'
        },
        xAxis: [{
            categories:date,
            crosshair: true
        }],
        yAxis: [{ // Primary yAxis
            labels: {
                format: '{value}%',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            title: {
                text: 'Cloud Cover',
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            }
        }, { // Secondary yAxis
            title: {
                text: 'PV Production',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            labels: {
                format: '{value} HW',
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            opposite: true
        }],
        tooltip: {
            shared: true
        },
        legend: {
            layout: 'vertical',
            align: 'left',
            x: 120,
            verticalAlign: 'top',
            y: 100,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
        },
        series: [{
            name: 'PV Production',
            type: 'column',
            yAxis: 1,
            data:pv,
            tooltip: {
                valueSuffix: ' Wh'
            }

        }, {
            name: 'Percent Cloud Cover',
            type: 'spline',
            data: cloud,
            tooltip: {
                valueSuffix: ' % '
            }
        }]
    });

}





function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies;
        cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

//nano bar
   // var options = {
        //            bg :' #4686A1',
      //        }
    //var nanobar = new Nanobar(options);
    //var i = 1;
    // for(i=1;i<=100;i++){
			//nanobar.go(i);
                       // }
// Get high chart data here

get_high_chart( date, HighChartHighPvProduction, HighChartHighCloudCover);


/* Alerts modal toggle script */

  var  modal = $('#alert-modal'),
       modalToggle = $('.modal-toggle'),
       alertDataPointInfo = $('.alert-data-point-info'),
       silenceAlert = $('.silence-alert'),
       initiatingModalTime = 5000;

  setTimeout(setModalLoad, initiatingModalTime);

  function setModalLoad() {

      $('.modal-toggle').click(function()  {
          // Get necessary data for the get_alert_sort
          alertId = $(this).attr('classid');
          // Constructing the json
          var jsonData = {alert_id : alertId,
                          csrfmiddlewaretoken: csrftoken};

          $.post('/get-alert-data', jsonData, function(data){

              var alertData = JSON.parse(data);
              alertValue = alertData.alert_value; // Getting the property that is triggering the alert

                  for (var value in alertData) {

                      if(value == 'alert_id'){ // Checking for alert_id so that it is not displayed
                          element = '<tr><td class="alert-id hidden">' + alertData[value] + '</td></tr>';
                          alertDataPointInfo.append(element)
                          continue;
                      }
                      else if(value == 'alert_value') {
                          continue;
                      }
                      else if(value == alertValue) {
                          element = '<tr class=danger> <td>' + value + '</td> <td> ' + alertData[value] + '</td></tr>';
                          alertDataPointInfo.append(element);
                          continue;
                      }
                element = '<tr><td>' + value + '</td> <td> ' + alertData[value] + '</td></tr>';
                      alertDataPointInfo.append(element);
                  }
          });
          modal.modal('show');
      });

      modal.on('hidden.bs.modal',function(){
          alertDataPointInfo.html('');
      });

      silenceAlert.click(function(){
          alertId = parseInt($('.alert-id').text());
          jsonData = {
                      alert_id : alertId,
                      csrfmiddlewaretoken: csrftoken
                     };

          $.post('/silence-alert', jsonData, function(data) {
               modal.modal('hide');
          });
      });
     

     
                  }
