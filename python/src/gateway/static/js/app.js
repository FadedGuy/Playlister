document.addEventListener("DOMContentLoaded", function(event){
    let sendURLRequest = document.getElementById("sendURL");
    sendURLRequest.addEventListener("submit", (e) => {
        e.preventDefault();
        let url = document.getElementById("yt-url");
        console.log(url.value);
    });
});
