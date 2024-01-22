displayView = function () {
    // the code required to display a view
    document.getElementById("view").innerHTML = document.getElementById("welcome-view").innerHTML;
};
window.onload = function () {
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    displayView();
};