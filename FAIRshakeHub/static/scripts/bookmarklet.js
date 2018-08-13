body=document.getElementsByTagName("body")[0];

function doD3(callback){
   var script = document.createElement('script');
   script.src = 'https://d3js.org/d3.v3.min.js';
   document.getElementsByTagName('head')[0].appendChild(script);

   //when the new script's load event fires, execute the callback
   script.onload = callback;
};

function doJquery(callback){
   var script = document.createElement('script');
   script.src = 'https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min.js';
   document.getElementsByTagName('head')[0].appendChild(script);
   script.onload = callback;
}

function doBookmarklet(){
   var script = document.createElement('script');
   script.src = 'https://cdn.rawgit.com/lw453/fairshake/84995c6/bookmarklet2.js';
   document.getElementsByTagName('head')[0].appendChild(script);
};

var fairnessWrapper = document.createElement("div");
fairnessWrapper.id = "fairness-bklet-wrapper";

var fairness = document.createElement("div");
fairness.id = "fairness-bklet";
fairness.setAttribute("style","font-size:12px;text-align:left;font-family:arial, helvetica, clean, sans-serif;line-height:15px;width:120px;background-color:white;position:fixed;right:0;top:0;z-index:2147483636;padding:10px;-moz-box-shadow:0px 0px 5px #333333;-webkit-box-shadow:0px 0px 5px #333333;box-shadow:0px 0px 5px #333333");

var fairnessInsig = document.createElement("div");
fairnessInsig.setAttribute("class","fairness-bklet-insig");
fairnessInsig.setAttribute("style","margin:0 auto;")

var infoDiv = document.createElement("div");
var fairshakeInfo = document.createElement("p");
fairshakeInfo.setAttribute("id","fairshakeBkletInfo");
var fairshakeLink = document.createElement("a");
fairshakeLink.setAttribute("href","http://54.175.203.110/fairshake");
//fairshakeLink.setAttribute("href","http://127.0.0.1:5000/fairshake");
fairshakeLink.setAttribute("id","fairshakeBkletLink");
infoDiv.setAttribute("style","padding-top:10px;text-align:center;word-wrap:break-word;");
fairshakeLink.setAttribute("style","font-family:arial;line-height:15px;font-size:12px;color:#337ab7;");

var closeOverlay = document.createElement("a");
closeOverlay.setAttribute("class","close-overlay");
closeOverlay.setAttribute("style","line-height:10px;text-decoration:none;position:absolute;top:0;right:0;background:#eee;font-size:0.9em;padding:2px 5px;border:solid #ccc;border-width:0 0 1px 1px;display:block;")
closeOverlay.setAttribute("onclick","removeBklet();")
closeOverlay.setAttribute("href","javascript:void(0)")
closeOverlay.innerText = "X";

document.body.appendChild(fairnessWrapper);
fairnessWrapper.appendChild(fairness);
fairness.appendChild(fairnessInsig);
fairness.appendChild(infoDiv);
infoDiv.appendChild(fairshakeInfo);
infoDiv.appendChild(fairshakeLink);
fairness.appendChild(closeOverlay);

if (void 0 == window.jQuery){
    if ("undefined" == typeof d3){
        doJquery(doD3(doBookmarklet));
    } else {
        doJquery(doBookmarklet);
    }
} else {
    if ("undefined" == typeof d3){
        doD3(doBookmarklet);
    } else {
        doBookmarklet();
    }
}

function removeBklet(){
    a = document.getElementById("fairness-bklet-wrapper");
    a.parentNode.removeChild(a);
    b = document.getElementById("fairshakeBkletScript");
    b.parentNode.removeChild(b);
}