$(document).ready(function(){

    var form = $("#forgot-form");  
    form.submit(function(e){
        e.preventDefault()
        if (sanitiseEmail()){
            this.submit()
        }
    })
    
})

function sanitiseEmail(){
    var email = $("#forgot-form input[name='email']").val()

    if (!email.trim()){
        showToast("You must enter an email", "error")
        return false
    }
    return true
}
