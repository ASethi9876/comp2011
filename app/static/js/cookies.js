window.addEventListener("load",function(){
  window.cookieconsent.initialise({
    "pallette":{
        "popup":{
          "background": "#eaf7f7",
          "text": "#5c7291"
        },
        "button":{
          "background":"#56cbdb",
           "text": "#ffffff"
        }
      },
      "content": {
        "message": "This website uses cookies",
        "dismiss": "Accept"
      },
      onStatusChange: function(status) {
        if (status == "dismiss") {
          document.querySelector(".cc-window").style.display = "none";
        }
      },

  })});