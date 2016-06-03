
var csrftoken = getCookie('csrftoken');

/* Function For Daily DataPoints Graph Generation */
function daily_data_points_graph() {
   drop_choice1 = $("#drop1").val();
   drop_choice2 = $("#drop2").val();
   time_value = $('#time_dropdown').val();
   var title = $('#time_dropdown').find(":selected").text();
   message = (title +" " + drop_choice1 + '  With  ' + drop_choice2);
   $("#title-message").html(message);

   //$("#dynamic_graph").hide();
  $(".graph-loader").hide();

  $.post("/graphs",{csrfmiddlewaretoken: csrftoken, 'choice': [drop_choice1,drop_choice2], 'time':time_value , 'active_site_id':active_site_id},function(data){

        var response = JSON.parse(data);

        dropdown1_values = response[drop_choice1][0];
        SI_unit1 = response[drop_choice1][1];

        dropdown2_values = response[drop_choice2][0];

        SI_unit2 = response[drop_choice2][1];

        for (i=0;i<dropdown1_values.length;i++){
        dropdown1_values[i][0]=dropdown1_values[i][0] * 1000
        }
        for (i=0;i<dropdown2_values.length;i++){
        dropdown2_values[i][0]=dropdown2_values[i][0] * 1000
        }

        $('#containerhigh').highcharts({
                 chart: {
            zoomType: 'xy'
        },
        title: {
            text: title + " " + drop_choice1 + ' with ' + drop_choice2 + ' In High Charts'
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
                text: drop_choice2,
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            }
        }, { // Secondary yAxis
            title: {
                text: drop_choice1,
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
            name: drop_choice1 ,
            type: 'spline',
            yAxis: 1,
            data: dropdown1_values,
            tooltip: {
                valueSuffix: SI_unit1
            }

        }, {
            name: drop_choice2,
            type: 'column',
            data: dropdown2_values,
            tooltip: {
                valueSuffix: SI_unit2
            }
        }]
    });

});

    //$("#dynamic_graph").show();
    //$(".graph-loader").hide();
}




$(document).ready(function(){

 daily_data_points_graph()

 });

/* Update Daily Data Point Graph on Click */
$("#dynamic_graph_button").click(function(){
  daily_data_points_graph()
});
