$(document).ready(function(){
    var form = $("#create-event");
    
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
                        showToast(res.error, "error");
                        console.log(res);
                    }
                },
                error: function(xhr, status, error) {
                    showToast(error.error, "error");
                    console.log(error);
                }
            });
        }
    });
    
    function sanitiseInputs(){
        return checkStartTime() && checkDuration() && checkDate();
    }
    
    function checkDate() {
        var selectedDate = new Date($("#create-event input[name='date']").val());
        var today = new Date();
        
        if (selectedDate <= today) {
            showToast("Date must after today", "error")
            return false;
        }
        
        return true; 
    }
    
    function checkStartTime() {
        var startTime = $("#create-event input[name='start_time']").val();
        if (!startTime.trim()){
            return false
        }
        return true; 
    }
    
    function checkDuration() {
        var duration = $("#create-event input[name='duration']").val();
        if (!duration.trim()){
            return false
        }
        return true;
    }
});
