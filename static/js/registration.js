
$(document).ready(function (){
    var form = $("#register-form")

    form.submit(function(e){

        e.preventDefault()
        
        if (sanitiseInputs()) {
            $.ajax({
                type: "POST",
                url: "/auth/register",
                data: form.serialize(),
                success: function(res){
                    if (res.success){
                        showToast(res.success, "success")
                        window.location.href = "/auth/login"
                    }
                    else {
                        showToast(res.error, "error")
                    }
                },
                error: function(xhr, status, error) {
                    showToast(error.error, "error")
                    console.log(error)
                }
            })
        }
    });
});

function sanitiseInputs() {
    return checkFields() && checkPassword()
}

function checkFields() {
    var forename = $("#register-form input[name='forename']").val()
    var surname = $("#register-form input[name='surname']").val()
    var email = $("#register-form input[name='email']").val()

    if (!email.trim()){
        showToast("Please enter a valid email", "error")
        return false;
    }
    if (!forename.trim()){
        showToast("Please enter a valid forename", "error")
        return false;
    }
    
    if (!surname.trim()){
        showToast("Please enter a valid surname", "error")
        return false;
    }
    return true;
}

function checkPassword() {
    var password = $("#register-form input[name='password']").val()
    var confirmPassword = $("#register-form input[name='confirm-password']").val()

    if (password != confirmPassword){
        showToast("Passwords do not match", "error")
        return false;
    }
    
    if (password.length < 8) {
        showToast("Password must be at least 8 characters long", "error")
        return false
    }

    return true
}







/* ajax idea
var formData = $("#register-form").serialize(); // serialise form data
        $.ajax({
            type: 'POST',
            url: '/auth/register-user',
            data: formData,
            success: function(res) {
                if (res.success) {
                    console.log(res.success)
                    // email confirmation sent
                    window.location.href = '/login'
                } else if (res.error) {
                    console.log(res.error)
                }
            },
            error: function(res, status, error) {
                console.log("An error occured : ", status, error)
            }
        });
*/