$(document).ready(function(){
    console.log("E4ta")
    $("#modal-btn").click(function(){
        console.log("Working")
        $('.ui.modal')
        .modal('show')
        ;
    })
    $(".ui.dropdown").dropdown()
})
