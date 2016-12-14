/* Displays the data analysis graph */




function daily_data_points_graph() {

    var drop_choice1 = $("#drop1").val(),
        drop_choice2 = $("#drop2").val(),
        start_time = $('#dynamic_graph_container #start-time').val(),
        end_time = $('#dynamic_graph_container #end-time').val(),
        measurement1 = $("#drop1 option:selected").html(),
        measurement2 = $("#drop2 option:selected").html(),
        resolution = $('#resolution').val(),
        title = $('#time_dropdown').find(":selected").text();



    $("#dynamic_graph").hide();
    $(".graph-loader").show();

    data_to_send = {
          'choice': [drop_choice1,drop_choice2],
          'start-time': start_time,
          'end-time': end_time,
          'active_site_id': active_site_id,
          'resolution': resolution
    }


    $.get("/graphs", data_to_send, function(data){

        console.log(data);
        var response = JSON.parse(data);


        dropdown1_values = response[0].data;
        SI_unit1 = response[0].si_unit;

        dropdown2_values = response[1].data;

        SI_unit2 = response[1].si_unit;

        /*
        
        for (i=0;i<dropdown1_values.length;i++){
        dropdown1_values[i][0]=dropdown1_values[i][0] * 1000
        }
        for (i=0;i<dropdown2_values.length;i++){
        dropdown2_values[i][0]=dropdown2_values[i][0] * 1000
        }
        */

        $('#containerhigh').highcharts({
                 chart: {
            zoomType: 'xy'
        },
        title: {
            text: title + " " + measurement1 + ' with ' + measurement2
        },
        xAxis: [{
            crosshair: true,
            type: 'datetime',
        }],
        yAxis: [{ // Primary yAxis
            labels: {
                format: '{value} '+SI_unit2,
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            title: {
                text: measurement2,
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            }
        }, { // Secondary yAxis
            title: {
                text: measurement1,
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            labels: {
                format: '{value} '+ SI_unit1,
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

           name: measurement2,
           type: 'column',
           data: dropdown2_values,
           tooltip: {
                   valueSuffix: SI_unit2
            }

        }, {

            name: measurement1 ,
            type: 'spline',
            yAxis: 1,
            data: dropdown1_values,
            tooltip: {
                    valueSuffix: SI_unit1
            }
        }]
    });

  });
    $(".graph-loader").hide();
    $("#dynamic_graph").show();

}
window.onload = daily_data_points_graph()
/*
$(document).ready(function(){
 alert("on page load is this")
 daily_data_points_graph()

 });
 */
/* Update Daily Data Point Graph on Click */
$("#dynamic_graph_button").click(function(){
  Pace.restart();
  /*
  paceOptions = {
  initialRate:0.7,
  minTime:1750,
  maxProgressPerFrame:2,
  ghostTime: 120000
 }
*/
paceOptions = {
 catchupTime : 10000,
 maxProgressPerFrame:1,
 ghostTime: Number.MAX_SAFE_INTEGER,
   checkInterval :{
     checkInterval: 50000
   },
   eventLag : {
     minSamples: 5,
     sampleCount: 30000000,
     lagThreshold: 0.5
   }
}
  daily_data_points_graph()
});
