
var csrftoken = getCookie('csrftoken');

/* Auto compete on search*/
var i,
    textid,
    textinput,
    option,
    matched,
    siteid = [],
    sitename = [];

$.post("/search",{csrfmiddlewaretoken: csrftoken},function(data){
    option = JSON.parse(data);

    // site names
   for (i=0;i < option.length;i++){
    sitename.push(option[i].value)
   }

   // site id
   for (i=0; i< option.length; i++){
    siteid.push(option[i].key)
   }

   var input = document.getElementById('search-site');

   //array of options
   new Awesomplete(input,{list: sitename});
});

function AutoComplete() {
      textinput = $(".form-control").val();
      for (i=0;i<sitename.length;i++){

           // checking  entered values
           if (sitename[i] == textinput){
               matched = true;
               for (i=0 ;i < option.length; i++){
                // finding id
                   if (option[i].value == textinput){
                       textid = option[i].key;
                       // redirecting
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

/*if ENTER pressed */
$('.form-control').keypress(function(event){
    var keycode = (event.keyCode ? event.keyCode : event.which);
    var matched = false;
    if(keycode == '13'){
       event.preventDefault();
       AutoComplete()
    }
});

$(".button-search").click(function(){
    AutoComplete()
});

/* Alerts modal toggle script */

  var  modal = $('#alert-modal'),
       modalToggle = $('.modal-toggle'),
       alertDataPointInfo = $('.alert-data-point-info'),
       silenceAlert = $('.silence-alert'),
       initiatingModalTime = 5000;

  setTimeout(setModalLoad, initiatingModalTime);

  function setModalLoad() {

      var alertDataContainer = $('#alert-data-container'),
          alertLoader = $('#alert-data-loader');

      $('.modal-toggle').click(function()  {

          alertLoader.show();
          alertDataContainer.hide();




          // Get necessary data for the get_alert_sort
          alertId = $(this).attr('classid');
          // Constructing the json
          var jsonData = {"alertId" : alertId,
                          csrfmiddlewaretoken: csrftoken};

          $.post('/get-alert-data', jsonData, function(data){
          /*
            This gets the alert information from a server when
            The alert is clicked on
          */
              alertLoader.hide();
              alertDataContainer.show();


              var alertData = JSON.parse(data);
              alertValue = alertData.alert_value; // Getting the property that is triggering the alert

                  for (var value in alertData) {

                      if(value == 'id'){ // Checking for alert_id so that it is not displayed
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
          alertId = parseInt($('.alert-data-point-info .alert-id').text());
          jsonData = {
                      alert_id : alertId,
                      csrfmiddlewaretoken: csrftoken
               };

          $.post('/silence-alert', jsonData, function(data) {
               modal.modal('hide');
          });
      });
}
