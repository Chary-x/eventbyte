
$(document).ready(function(){
    $(".create-event").click(function(e){
        showModal();
    });

    $(".close-modal").click(function(e){
        hideModal();
    });

    $(".modal-form").submit(function(){
        if(sanitiseInputs()){           
            $(this).submit()
        }
    })
});


function showModal(){
    $('.modal-background').show()
    $(".modal").show();
}

function hideModal(){
    $('.modal-background').hide()
    $(".modal").hide()
}

function sanitiseInputs(){
    // todo later

}


