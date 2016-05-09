
var csrftoken = getCookie('csrftoken');

function time_series_graph() {
                 measurement_value = $('#measurements_dropdown').val();
                 time_value = $('#time_dropdown').val();
    $.post('/graphs',{csrfmiddlewaretoken:csrftoken,'choice':[measurement_value],'time':time_value,'active_site_id':active_site_id},function(data){
                 var response = JSON.parse(data)
                graph_data_values = response[measurement_value][0]
                 si_units = response[measurement_value][1]
                 for (i=0;i<graph_data_values.length;i++){
                 graph_data_values[i][0]=graph_data_values[i][0]*1000
                 }


         $('#time_series_graph').highcharts({
           chart : {
                zoomtype : 'x'
           },
           title : {
                text: 'Time Series Graph '
           },
           xAxis : {
                  type : 'datetime'
                  },
           yAxis : [{
                   labels : {
                         format : '{value}'+ si_units,
                         style : {
                               color : Highcharts.getOptions().colors[1]
                         },
                     },
                   title : {
                         text : measurement_value,
                   },

           }],
           legend : {
                layout : 'vertical',
                align : 'left',
                x:40,
                varticalAlign: 'top',
                y :-350,
                floating:true,
           },
           series :[{
                 name : measurement_value,
                 type : 'spline',
                 data :graph_data_values,
                 tooltip : {

                        valueSuffix : si_units
                 },
            }],


          });
     });
}
function daily_data_points_graph() {
   drop_choice1 = $("#drop1").val();
   drop_choice2 = $("#drop2").val();
   time = "24h";
  message = ('Daily ' + drop_choice1 + '  With  ' + drop_choice2);
  $("#title-message").html(message);
  $.post("/graphs",{csrfmiddlewaretoken: csrftoken, 'choice': [drop_choice1,drop_choice2], 'time':time , 'active_site_id':active_site_id},function(data){
        //alert(data)
        var response = JSON.parse(data);
        //alert('response is')

        dropdown1_values = response[drop_choice1][0];
        SI_unit1 = response[drop_choice1][1];

        //alert(dropdown1_values)
        //alert(SI_unit1)
        dropdown2_values = response[drop_choice2][0];

        SI_unit2 = response[drop_choice2][1];

        for (i=0;i<dropdown1_values.length;i++){
        dropdown1_values[i][0]=dropdown1_values[i][0]*1000
        }
        for (i=0;i<dropdown2_values.length;i++){
        dropdown2_values[i][0]=dropdown2_values[i][0]*1000
        }

        $('#containerhigh').highcharts({
                 chart: {
            zoomType: 'xy'
        },
        title: {
            text: ' Daily ' + drop_choice1 + ' with ' + drop_choice2 + ' In High Charts'
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
            type: 'spline',
            data: dropdown2_values,
            tooltip: {
                valueSuffix: SI_unit2
            }
        }]
    });

});
}




$(document).ready(function(){
   time_series_graph()
   daily_data_points_graph()
 });

$("#update-button").click(function(){
  time_series_graph()
});

$("#dynamic_graph_button").click(function(){
  daily_data_points_graph()
});


