
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
