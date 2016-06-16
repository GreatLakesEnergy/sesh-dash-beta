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

/* Auto compete on search*/
var i,
    textid,
    textinput,
    option,
    matched,
    siteid = [],
    sitename = [];

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
   var input = document.getElementById('search-site');
   /* proving an array of options to be suggested when a user types using awesomplete plugin */
   new Awesomplete(input,{list: sitename});
});

function AutoComplete() {
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

/*if ENTER pressed */
$('.form-control').keypress(function(event){
    var keycode = (event.keyCode ? event.keyCode : event.which);
    var matched = false;
    if(keycode == '13'){
       AutoComplete()
    }
});

$(".button-search").click(function(){
    AutoComplete()
});
