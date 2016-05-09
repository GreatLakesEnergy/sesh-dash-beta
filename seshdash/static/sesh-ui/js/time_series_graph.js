
var csrftoken = getCookie('csrftoken');

function graph() {
    measurement_value = $('#measurements_dropdown').val();
    time_value = $('#time_dropdown').val();
  $.post('/time_series',{csrfmiddlewaretoken:csrftoken,'measurement':measurement_value,'time':time_value,'active_id':active_site_id},function(data){
                 var data_values = JSON.parse(data)
                 si_units = data_values.units;
                 graph_data_values=data_values.graph_values;


                  for(var i =0 , l= graph_data_values.length ; i<l ;i++){
                      graph_data_values[i][0] = graph_data_values[i][0] * 1000;
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

  $('#update-butt').click(function(){
    graph()
   });

  $(document).ready(function(){
    graph()
  });

                
