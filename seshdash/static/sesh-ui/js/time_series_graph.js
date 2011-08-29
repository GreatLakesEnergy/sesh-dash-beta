function getCookie(name) {
    var cookieValue = null;
   if(document.cookie && document.cookie != '') {
        var cookies;
        cookies = document.cookie.split(';');
        for (var i = 0 ; i<cookies.length ; i++) {
            var cookie = jQuery.trim(cookies[i]);

            if (cookie.substring(0, name.length + 1) ==(name + '=')) {
               cookieValue = decodeURIComponent(cookie.substring(name.length +1 ))
                break;
            }
          }
       }
       return cookieValue;
}

var csrftoken = getCookie('csrftoken');

var measurement_default_value;
var time_default_value;
$(document).ready(function(){

    measurement_default_value = $('#measurements_dropdown').val();
    time_default_value = $('#time_dropdown').val();

    $.post('/time_series',{csrfmiddlewaretoken:csrftoken,'measurement':measurement_default_value,'time':time_default_value,'active_id':active_site_id},function(data){
                 alert(data)
                // var jsondata = JSON.parse(data)
               //  alert(jsondata)
          $('#time_series_graph').highcharts({
           chart : {
                zoomtype : 'yx'
           },
           title : {
                text: 'Time Series Graph '
           },
           yAxis : [{
                   labels : {
                         format : '{value}',
                         style : {
                               color : Highcharts.getOptions().colors[1]
                         },
                     },
                   title : {
                         text : measurement_default_value,
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
                 name : measurement_default_value,
                 type : 'spline',
                 data : data,
                 tooltip : {
                        valueSuffix : ''
                 },
            }],

               
          });
     });
});

var measurement_value;
var time_value;
$('#graph_change_trigger').click(function(){ 
         measurement_value = $('#measurements_dropdown').val();
         time_value = $('#time_dropdown').val();
 $.post('/time_series',{csrfmiddlewaretoken:csrftoken,'measurement':measurement_value,'time':time_value,'active_id':active_site_id},function(data){
                 alert(data)
          $('#time_series_graph').highcharts({
              chart : {
                zoomtype : 'xy'
           },
           title : {
                text: 'Time Series Graph '
           },
           yAxis : [{
                   labels : {
                         format : '{value}',
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
                 data : data,
                 tooltip : {
                        valueSuffix : 'mxioum'
                 },
            }],

         });
     });
});
       
                  
