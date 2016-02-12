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
