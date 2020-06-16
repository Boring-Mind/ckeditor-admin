document.getElementById("button-id-next").onclick = function() {
    document.getElementById("form1").classList.add("d-none");
    document.getElementById("form2").classList.remove("d-none");
    scroll(0,0);
};