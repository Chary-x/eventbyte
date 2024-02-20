$(document).ready(function (){

    $("#login-form").submit(function(e){
        e.preventDefault();

        if (sanitiseInputs()){
            this.submit()
        }
    });
});


function showToast(message, type) {
    var toast = $('<div class="toast"></div>'); // create new div for toast

    if (type == "error") {
        toast.addClass("error")
    } else if(type == "success") {
        toast.addClass("success")
    } else {
        toast.addClass("message")
    }

    toast.text(message); 
    toast.appendTo("body"); 
    toast.fadeIn(400).delay(3000).fadeOut(400);
}

function sanitiseInputs(){
    if (checkPassword()){ //  can add in future checks here if needed
        return true
    } else {
        return false
    }

}
function checkPassword() {
    var password = $("#login-form input[name='password']").val();

    if (password.length < 8) {
        showToast("Password must be at least 8 characters long", "error");
        return false;
    }
    return true;
}




