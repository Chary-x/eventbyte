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
    
    $(".book-ticket").click(function(e) {
        e.preventDefault();
    
        var event_id = $(this).closest(".card-container").attr("id");
        var button = $(this)
        $.ajax({
            type: "POST",
            url: "/events/book/" + event_id,
            data: { event_id: event_id },
            success: function(res) {
                showToast(res.success, "success");
                if (res.max_tickets) {
                    button.hide();
                }
            },
            error: function(xhr, status, error) {
                showToast(error.error, "error");
            }
        });
    });

})



// todo , do some ajax for book-ticket