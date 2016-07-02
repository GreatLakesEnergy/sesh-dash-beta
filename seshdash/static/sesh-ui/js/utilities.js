/* This is a Javascript Utilities File Where all Helper Functions Are Kept */


/*function to auto-generate a CRSF cookie */
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
/*ALerts Notification modal */

 $(document).ready(function(){
    alertId = $(this).attr('classid');
    // getting alerts site and number from the server
    var jsonData = {"alertId" : alertId,
                      csrfmiddlewaretoken: csrftoken};
     $.post('/notifications',jsonData, function(data){

         //parsing data objects into a json file
          var alertData = JSON.parse(data);

          //declaring variables
          var out= $("#alert-notification-list");
          var element = '';
          var i;
          var sum_of_counters = 0;

          //looping through the json object appending to a table
          for(i=0 ; i<alertData.length ; i++){
              sum_of_counters += alertData[i].counter;                                                                                      element += '<li>'+
                             '<a href="/dash/' +alertData[i].site_id+'#alerts-panel">' +
                               '<div class="task-icon badge badge-danger">'+
                                 '<i class="icon-energy">'+'</i>'+
                                '</div>'+
                                '<p class="task-details">' + '<strong>'+alertData[i].site +'</strong>'+ '</p>' +
                                '<span class="badge badge-roundless badge-danger pull-right">' +
                                  alertData[i].counter +
                                '</span>' +
                             '</a>'+
                         '</li>';
          }

         out.append(element);

         //appending table into the notification dropdown box
         $('.alerts_counter ,#alerts_counter').html(sum_of_counters);

         if (sum_of_counters > 0){
             $('#alerts_counter').show();
          }
     });
});
