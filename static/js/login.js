$(document).ready(function (){

    $("#login-form").submit(function(e){
        e.preventDefault();

        if (sanitiseInputs()){
            this.submit()
        }
    });
});

function sanitiseInputs(){
    if (checkEmail() && checkPassword()){ //  can add in future checks here if needed
        return true
    } else {
        return false
    }

}

function checkEmail() {
    var email = $("#login-form input[name='email']").val();
    if (!email.trim()) {
        showToast("Email can't be empty", "error");
        return false;
    } else {
        return true;
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




