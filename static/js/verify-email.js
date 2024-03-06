$(document).ready(function(){
    var form = $("#verification-form");

    form.submit(function(e){
        e.preventDefault();
        if (sanitiseField()){
            $.ajax({
                type: 'POST',
                url: window.location.href,
                data: form.serialize(),
                success: function(res){
                    if (res.success){
                        window.location.href = "/auth/login";
                    }
                    else {
                        showToast(res.error, "error");
                    }
                },
                error: function(xhr, status, error){
                    showToast(error.error, "error");
                }
            });
        }
    });
});


function sanitiseField(){
    var field = $("#verification-form input[name='token']").val()
    if (!field.trim()){
        showToast("Field can't be empty", "error")
        return false
    }
    return true
}
