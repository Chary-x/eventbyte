$(document).ready(function (){

    var form = $("#login-form")
    form.submit(function(e){
        e.preventDefault();

        if (sanitiseInputs()){
            $.ajax({
                type: "POST",
                url: "/auth/login",
                data: form.serialize(),
                success: function(res){
                    if (res.success){
                        window.location.href = "/dashboard"
                    }
                    
                    else if (res.error){
                        showToast(res.error, "error")
                    }
                },
                error: function(xhr, status, error){
                    showToast(error.error, "error")
                }
            })
        
        }
    });
});

function sanitiseInputs(){
    return checkEmail() && checkPassword()


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




