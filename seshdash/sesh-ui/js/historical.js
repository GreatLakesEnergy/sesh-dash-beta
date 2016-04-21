$(function(){ 

    // Change dates Properties to native javascript date objects
    function convertDateStringProperty(data) {
        for(i = 0; i < data.length; i++) {
            data[i].date = new Date(Date.parse(data[i].date));
        }
        return data;
    }

    // Function renders the historical Page
    function historicalRender(sortValue='daily_pv_yield' ) {
        // Resets
        
        var elementChart = '',
            wholeChart = '';

        historicalLoader.show();
        chartContainer.hide();

        $.post('/historical_data', {csrfmiddlewaretoken:csrftoken, sort_value:sortValue }, function(data) {
        chartData = JSON.parse(data);
        
        
        for(var i = 0; i < chartData.length; i++) { // For each site
            var siteName = chartData[i].site_name,
                numberOfAlerts = chartData[i].number_of_alerts,
                avgPvYield = chartData[i].average_pv_yield,
                avgPowerConsumptionTotal = chartData[i].average_power_consumption_total
                chartId = 'chart' + chartData[i].site_id,
                

            elementChart = '<div class="panel panel-default">'
            elementChart += '<div class="panel-heading"><strong>' + siteName + '</strong></div>';
            elementChart += '<div class="panel-body"><div class="table-responsive">' +
                                                    '<div class="chart-container" id="' + chartId + '"></div></div></div> ';
            elementChart += '<div class="panel-footer">'
            elementChart += '<div class="row hist-extra-info">'

            elementChart += '<div class="col-sm-4 extra-info-entity"><h4>Alerts</h4><span="value"> '
                            + numberOfAlerts + 
                            '</span> </div>';
            elementChart += '<div class="col-sm-4 extra-info-entity"><h4>Average Pv</h4><span="value"> '
                            + Math.round(avgPvYield * 100) / 100 + ' kw' +
                            '</span> </div>';
            elementChart += '<div class="col-sm-4 extra-info-entity"><h4>Average Power</h4><span="value"> '
                            + Math.round(avgPowerConsumptionTotal * 100) / 100 + ' kw' + 
                            '</span> </div>';

            elementChart += '</div></div></div>';
           
            wholeChart += elementChart;
            
        }
          
        // Append the string containing all the site holders
        chartContainer.html(wholeChart);
        
        for(var i = 0; i < chartData.length; i++) { // For each site generate chart
            

            var siteData = chartData[i].site_historical_data,
                chartId = 'chart' + chartData[i].site_id;
            
            siteData = convertDateStringProperty(siteData);

            
            var chart = calendarHeatmap()
                        .data(siteData)
                        .tooltipUnit(chartData[0].data_unit)
                        .selector('#' + chartId)
                        .onClick(function(data){
                            $.post('/get_historical_day', {csrfmiddlewaretoken:csrftoken}, function(data) {
                                // Add Modal Toggle
                                // Pull data from the web based on the date
                                // Print data
                                alert(data);
                            });
                        });
               
            chart(); 
            
            historicalLoader.hide();
            chartContainer.show();
        }

    });
 

    }

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


    var historicalLoader = $('.historical-loader'),
        chartContainer = $('.chart-data-container'),
        dataSort=$('#data-sort');

    historicalLoader.show();
    historicalRender();
       
    
    // Data sorting based on the selected value from the dropdown
    dataSort.change(function(){
        historicalRender(dataSort.val());
    });


});
