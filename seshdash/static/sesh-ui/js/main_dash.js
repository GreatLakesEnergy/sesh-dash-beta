$(function(){

    $(".site-list > li").each(function(){
      if ($(this).val() == active_site_id){
          $(this).addClass("active");
       }

    });


});


