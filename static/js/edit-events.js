$(document).ready(function(){
    $("#edit-form").submit(function(e){
        if (sanitiseInputs()){
            this.submit();
        }
    });
});



function checkCapacity(){
    
}

function sanitiseInputs(){
    return true
}
