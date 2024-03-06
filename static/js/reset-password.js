$(document).ready(function(){
    var form = $("#password-reset-form")

    form.submit(function(e){
        e.preventDefault()
        
        if(sanitiseInputs()){
            $.ajax({
                type : 'POST',
                url: window.location.href,
                data: form.serialize(),
                success: function(res){
                    if (res.success){
                        window.location.href = "/auth/login"
                    }
                    else {
                        showToast(res.error, "error")
                    }       
                },
                error: function(xhr, status, error){
                    showToast(error.error,"error")
                }
            })
        }
    })

})

function checkPassword() {
    var password = $("#password-reset-form input[name='password']").val()
    var confirmPassword = $("#password-reset-form input[name='confirm-password']").val()

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


function sanitiseInputs(){
    return checkPassword()  // anded with future predicates
}