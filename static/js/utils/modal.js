
$(document).ready(function(){
    $(".create-event").click(function(e){
        showModal();
    });

    $(".close-modal").click(function(e){
        $("#myModal").hide();
    });
});


function showModal(){
    $('.modal-background').show()
    $(".modal").show();
}

function hideModal(){
    $(".modal").hide()
    $('.modal-background').remove()
}