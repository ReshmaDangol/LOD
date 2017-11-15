$(document).ready(function(){
    url="http://localhost:5000/";
    $.get(url+"classlist", function(data){
         console.log(data)
    });
});