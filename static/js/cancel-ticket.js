$(document).ready(function(){

    $(".delete").click(function(e){
        var cancelButton = $(this)
        var ticket = $(this).closest('.card-container')
        var ticketID = ticket.attr('id')
        e.preventDefault()
        $.ajax({
            type: 'PUT',
            url: '/tickets/' + ticketID + '/cancel',
            success : function(res){
                if (res.success){
                    showToast(res.success, "success")
                    ticket.addClass('cancelled')
                    cancelButton.hide()
                }
                else {
                    showToast(res.error, "error")
                }
            },
            error : function(xhr, status, error){
                showToast(error.error, "error")
            }
        })
    })




})