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
                  chart: {
                     type : 'column',
                  },
                  title: {
                     text : 'Time Series Graph',
                  },
                 xAxis: {
                    categories : []
                 },
                 yAxis : {
                     title : {
                         text : measurement_value,
                             }
                     },
                     series : [{
                          data:data,
                     }]
                
          });
     });
});

var measurement_value;
var time_value;
$('#graph_change_trigger').click(function(){ 
     $('#measurements_dropdown').change(function(){
         measurement_value = $('#measurements_dropdown').val();
     });

     $('#time_dropdown').change(function(){
          time_value = $('#time_dropdown').val();
     });
 $.post('/time_series',{csrfmiddlewaretoken:csrftoken,'measurement':measurement_value,'time':time_value,'active_id':active_site_id},function(data){
                 alert(data)
          $('#time_series_graph').highcharts({
                  chart: {
                     type : 'column',
                  },
                  title: {
                     text : 'Time Series Graph',
                  },
                 xAxis: {
                    categories : []
                 },
                 yAxis : {
                     title : {
                         text : measurement_value,
                             }
                     },
                     series : [{
                          data:data,
                     }]
                
          });
     });
});
       
                  
