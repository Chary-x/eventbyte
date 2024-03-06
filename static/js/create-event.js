$(document).ready(function(){
    var form = $("#create-event")
    
    form.submit(function(e){
        e.preventDefault();
        
        if (sanitiseInputs()) {
            $.ajax({
                type: "POST",
                url: "/events/create",
                data: form.serialize(),
                success: function(res) {
                    if (res.success){
                        showToast(res.success, "success"); 
                        console.log(res);
                    }
                    else {
                        showToast(res.error, "error")
                        console.log(res)
                    }
                },
                error: function(xhr, status, error) {
                    showToast(error.error, "error")
                    console.log(error)
                }
            })
        }
    })
})

function sanitiseInputs() {
    return  checkInput('start_time', "You must enter a start time") && 
            checkInput('duration', "You must enter a duration") &&
            checkInput('date', "You must enter a date") &&
            checkInput('name', "You must enter a title") &&
            checkInput('capacity', "You must enter a capacity") &&
            checkInput('location', "You must enter a location")
}
    
function checkInput(field, errorMessage) {
    var value = $("#create-event input[name='" + field + "']").val().trim()
    if (!value) {
        showToast(errorMessage, "error")
        return false
    }
    return true
}

function checkDate() {
    var date = new Date($("#create-event input[name='date']").val())
    var today = new Date();
    
    if (date < today) {
        showToast("Date can't be in the past", "error")
        return false
    }
    
    return true;
}
