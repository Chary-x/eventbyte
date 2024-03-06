$(document).ready(function(){
    $(".edit").click(function(){
        // get event id for this button by traversing up
        var event_id = $(this).closest(".card-container").attr("id")
       
        window.location.href = "/events/edit/" + event_id
    })

    $(".delete").click(function(){
        var event_id = $(this).closest(".card-container").attr("id")
        var event = $(this).closest(".card-container")

        var deleteButton = $(this)
        var editButton = event.find(".edit")
        console.log(editButton)
        $.ajax({
            type: "PUT",
            url: "/events/cancel/" + event_id,
            success: function(res){
                if (res.success){
                    event.addClass("cancelled")
                    deleteButton.hide()
                    editButton.hide()
                    showToast(res.success, "success")
                } else {
                    showToast(res.error, "error")
                }
            },
            error: function(xhr, status, error){
                showToast(error.error, "error")
            }
        });
    });

    
    $(".book-ticket").click(function(e) {
        e.preventDefault();
    
        var event_id = $(this).closest(".card-container").attr("id")
        var button = $(this)
        $.ajax({
            type: "POST",
            url: "/events/book/" + event_id,
            data: { event_id: event_id },
            success: function(res) {
                if(res.success){
                    showToast(res.success, "success")
                }
                else if (res.error){
                    showToast(res.error, "error")
                }
                else if (res.max_tickets) {
                    button.hide();
                }
            },
            error: function(xhr, status, error) {
                showToast(error.error, "error")
            }
        });
    });

})



// todo , do some ajax for book-ticket