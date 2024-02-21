$(document).ready(function(){
    $(".edit").click(function(){
        // get event id for this button by traversing up
        var event_id = $(this).closest(".event-container").attr("id")
        // redirect to edit page via get req
        window.location.href = "/events/edit/" + event_id;
    })


    $(".cancel").click(function(){
        var event_id = $(this).closest(".event-container").attr("id")
        window.location.href = "/events/cancel/" + event_id
    })
    

})

