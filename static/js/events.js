$(document).ready(function(){
    $(".edit").click(function(){
        // get event id for this button by traversing up
        var event_id = $(this).closest(".card-container").attr("id")
       
        window.location.href = "/events/edit/" + event_id;
    })


    $(".delete").click(function(){
        var event_id = $(this).closest(".card-container").attr("id")
        window.location.href = "/events/cancel/" + event_id
    })
    

})

