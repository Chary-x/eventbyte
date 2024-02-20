// no idea hwo to import this yet

export default function showToast(message, type) {
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

