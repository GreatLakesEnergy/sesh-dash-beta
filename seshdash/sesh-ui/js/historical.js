$(function(){ 

    // Csrf token function from cookie
    function getCookie(name) {
    var cookieValue = null;
        if (document.cookie && document.cookie != '') {
           var cookies = document.cookie.split(';');
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

    $.post('/historical-data', {csrfmiddlewaretoken:csrftoken}, function(data) {
        
    });
    
    var chartData = [
        {date: new Date(Date.parse('2016-01-01')), count: 10},
        {date: new Date(Date.parse('2016-01-02')), count: 20},
        
    ];  

    chart = calendarHeatmap()
            .data(chartData)
            .selector('.chart-container');
  
    chart();

    var chartContainer = $('.chart-data-container');


});
