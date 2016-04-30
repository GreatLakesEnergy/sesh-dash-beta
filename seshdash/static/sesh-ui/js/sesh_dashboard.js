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
/*
 * Barchart for energy production
*/

      /* Auto compete on search*/
var i;
var textid;
var textinput;
var option;
var matched;
var siteid = [];
var sitename = [];
/* post request to retrieve all sitename and site id */
$.post("/search",{csrfmiddlewaretoken: csrftoken},function(data){
    option = JSON.parse(data);
    //console.log(option)
    /* extracting site name array from response dict */
   for (i=0;i < option.length;i++){
    sitename.push(option[i].value)
   }
   /* extracting site id array from response dict */
   for (i=0; i< option.length; i++){
    siteid.push(option[i].key)
   }
   var input = document.getElementById('search');
   /* proving an array of options to be suggested when a user types using awesomplete plugin */
   new Awesomplete(input,{list: sitename});
});
/* checking if ENTER button is pressed */
$('.form-control').keypress(function(event){
    var keycode = (event.keyCode ? event.keyCode : event.which);
    var matched = false;
    if(keycode == '13'){
        textinput = $(".form-control").val();
        for (i=0;i<sitename.length;i++){
            /* checking if entered value exists in a sitename array */
             if (sitename[i] == textinput){
                  matched = true;
                  for (i=0 ;i < option.length; i++){
                    /* finding the id of the entered sitename */
                       if (option[i].value == textinput){
                             textid = option[i].key;
                             /* Linking to the asked sitename`s page */
                             window.location.replace("/dash/" + textid);
                        }
                  }
             { break; }
             }
        }
        if (!matched){
          document.getElementById("search").className = document.getElementById("search").className + " error";
        }
    }
});
/* search button */
$(".btn-default").click(function(){
        textinput = $(".form-control").val();
        for (i=0;i<sitename.length;i++){
            /* checking if entered value exists in a sitename array */
             if (sitename[i] == textinput){
                  matched = true;
                  for (i=0 ;i < option.length; i++){
                    /* finding the id of the entered sitename */
                       if (option[i].value == textinput){
                             textid = option[i].key;
                             /* Linking to the asked sitename`s page */
                             window.location.replace("/dash/" + textid);
                        }
                  }
             { break; }

             }
        }
        if (!matched){
          document.getElementById("search").className = document.getElementById("search").className + " error";
        }
});

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


/*
 High Chart Draw Function
*/
//function get_high_chart(date,pv,cloud)
//{
  var dropdown1;
  var dropdown2;
  var dropdown1_values = [];
  var dropdown2_values = [];
  var drop_choice1;
  var drop_choice2;
  var message;
  /*------------------------------------GRAPH-DEFAULT-----------------------------------*/
  var default1 = $("#drop1").val();
  var default2 = $("#drop2").val();
  message = (default1 + '  With  ' + default2);
  $("#title-message").html(message);

  $.post("/get_measurements_values",{csrfmiddlewaretoken: csrftoken, choice1:default1, choice2:default2 , active_site_id:active_site_id},function(data){
        var response = JSON.parse(data);
        dropdown1_values = response['drop1'];
        dropdown2_values = response['drop2'];
        SI_unit1 = response['SI_unit1'];
        SI_unit2 = response['SI_unit2'];
        $('#containerhigh').highcharts({
                 chart: {
            zoomType: 'xy'
        },
        title: {
            text: ' Daily ' + default1 + ' with ' + default2 + ' In High Charts'
        },
        xAxis: [{
            crosshair: true
        }],
        yAxis: [{ // Primary yAxis
            labels: {
                format: '{value} '+SI_unit2,
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            },
            title: {
                text: default2,
                style: {
                    color: Highcharts.getOptions().colors[1]
                }
            }
        }, { // Secondary yAxis
            title: {
                text: default1,
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
            name: default1 ,
            type: 'spline',
            yAxis: 1,
            data: dropdown1_values,
            tooltip: {
                valueSuffix: SI_unit1
            }

        }, {
            name: default2,
            type: 'spline',
            data: dropdown2_values,
            tooltip: {
                valueSuffix: SI_unit2
            }
        }]
    });
    });
/*-------------------------------END-OF-DEFAULT-GRAPH-------------------------------------*/
/*-----------------------------DROPDOWN-CHOICES------------------------------------------*/
    $("#drop1").change(function(){

         drop_choice1 = $("#drop1").val();
  });

  $("#drop2").change(function(){
        drop_choice2 = $("#drop2").val();
  });
/*-----------------------------END-OF-DROPDOWN-CHOICES-------------------------------------*/
/*----------------------------------------GRAPH-------------------------------------------*/
  $(".butt").click(function(){
      $.post("/get_measurements_values",{csrfmiddlewaretoken: csrftoken, choice1:drop_choice1, choice2:drop_choice2 , active_site_id:active_site_id},function(data){
        var response = JSON.parse(data);
        dropdown1_values = response['drop1'];
        dropdown2_values = response['drop2'];
        SI_unit1 = response['SI_unit1'];
        SI_unit2 = response['SI_unit2'];
        message = (drop_choice1 + '  With  ' + drop_choice2);
        $("#title-message").html(message);
        $('#containerhigh').highcharts({
                 chart: {
            zoomType: 'xy'
        },
        title: {
            text: ' Daily ' + drop_choice1 + ' with ' + drop_choice2 + ' In High Charts'
        },
        xAxis: [{
            crosshair: true
        }],
        yAxis: [{ // Primary yAxis
            labels: {
                format: '{value}'+SI_unit2,
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
                format: '{value} '+SI_unit1,
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
                valueSuffix:SI_unit1,
            }

        }, {
            name: drop_choice2,
            type: 'spline',
            data: dropdown2_values,
            tooltip: {
                valueSuffix: SI_unit2,
            }
        }]
    });
    });
  });
  /*-------------------------------------END--OF-GRAPH-----------------------------------*/
//}

// Get high chart data here

//get_high_chart( date, HighChartHighPvProduction, HighChartHighCloudCover);


/* Alerts modal toggle script */

  var  modal = $('#alert-modal'),
       modalToggle = $('.modal-toggle'),
       alertDataPointInfo = $('.alert-data-point-info'),
       silenceAlert = $('.silence-alert'),
       initiatingModalTime = 5000;

  setTimeout(setModalLoad, initiatingModalTime);



/*ALerts Notifoication modal */


    $(document).ready(function(){
    alertId = $(this).attr('classid');

    var jsonData = {"alertId" : alertId,
                      csrfmiddlewaretoken: csrftoken};
     $.post('/notifications',jsonData, function(data){

          var alertData = JSON.parse(data);
 
          var out= $("#alert-notification-table");
          var element = '';
          var i;
          var sum_of_counters = 0;

          for(i=0 ; i<alertData.length ; i++){

              sum_of_counters += alertData[i].counter;                                                                                      element += '<tr class ="clickable-row" data-href="/dash/' +alertData[i].site_id+'#alerts-panel">' +
                               '<td>'+ alertData[i].site +  '</td>' +
                               '<td id="site-counter">'+ alertData[i].counter + '</td>' +
                               '</tr>';
                    
                   out.append(element);
                   }

                 $('#pop').html(sum_of_counters);
                 if (sum_of_counters > 0){
                     $('#pop').show();
                  }


                $('.clickable-row').click(function(){
                   window.location.href =$(this).data("href");
                 });
             });
        });




  function setModalLoad() {

      $('.modal-toggle').click(function()  {
          // Get necessary data for the get_alert_sort
          alertId = $(this).attr('classid');
          // Constructing the json
          var jsonData = {"alertId" : alertId,
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

/*----------------------------    High chart-------------------------------------*/
/*$('#containerhigh').highcharts({
        chart: {
            zoomType: 'xy'
        },
        title: {
            text: ' Daily '+ dropdown1 +' with Cloud cover forecast In High Charts'
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
                text: dropdown1,
                style: {
                    color: Highcharts.getOptions().colors[0]
                }
            },
            labels: {
                format: '{value} Wh',
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
            name: dropdown1 ,
            type: 'column',
            yAxis: 1,
            data: values,
            tooltip: {
                valueSuffix: ' Wh'
            }

        }, {
            name: 'Percent Cloud Cover',
            type: 'spline',
            data: [9,8,7,6,5,4,3,2,1,0],
            tooltip: {
                valueSuffix: ' % '
            }
        }]
    });*/

/*------------------------------------------------------------------*/
