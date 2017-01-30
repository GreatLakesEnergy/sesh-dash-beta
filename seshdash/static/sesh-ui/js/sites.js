
$(function(){


    // Confirm site delete
    var deleteSiteButton = $('.delete-site-button');

    deleteSiteButton.click(function(e){
        link = deleteSiteButton.attr('href');
        console.log("the link is " + link);
        e.preventDefault();
        bootbox.confirm("Are you sure you want to delete this site?", function(result){
           console.log(result);
           if (result == true) {
              window.location = link
           } 
        });
    });




});
