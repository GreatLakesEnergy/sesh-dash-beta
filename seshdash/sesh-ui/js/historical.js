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


    var elementChart = '',
        wholeChart = '',
        historicalLoader = $('.historical-loader'),
        chartContainer = $('.chart-data-container');

    $.post('/historical_data', {csrfmiddlewaretoken:csrftoken}, function(data) {
        alert(data);
        
        chartData = JSON.parse(data);
        
        for(i = 0; i < chartData.length; i++) { // For each site
            var siteName = chartData[i].site_name,
                siteData = chartData[i].site_historical_data,
                chartId = 'chart' + chartData[i].site_id;

            elementChart = '<div class="panel panel-default">'
            elementChart += '<div class="panel-heading"><strong>' + siteName + '</strong></div>';
            elementChart += '<div class="panel-body"><div class="chart-container" id="' + chartId + '"></div></div> ';
            elementChart += '<div class="panel-footer">'
            elementChart += '<div class="row hist-extra-info">'
            elementChart += '<div class="col-sm-4 extra-info-entity"><h4>Extra Info one</h4></div>';
            elementChart += '<div class="col-sm-4 extra-info-entity"><h4>Extra Info Two</h4></div>';
            elementChart += '<div class="col-sm-4 extra-info-entity"><h4>Extra Info Three</h4></div>';
            elementChart += '</div></div></div>';
           
            wholeChart += elementChart;
            
        }
          
        // Append the string containing all the site holders
        chartContainer.append(wholeChart);
        
        for(i = 0; i < chartData.length; i++) { // For each site generate chart

            var siteData = chartData[i].site_historical_data,
                chartId = 'chart' + chartData[i].site_id;
            
            var chart = calendarHeatmap()
                        .data(siteData)
                        .selector('#' + chartId);
               
            chart(); 
            
            historicalLoader.hide();
        }

    });
    
    


});
