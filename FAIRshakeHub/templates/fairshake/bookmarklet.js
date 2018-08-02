require.config({
  paths: {
      "jquery": "https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min",
      "insignia": "https://fairshake.cloud/v2/static/scripts/insignia"
  }
});
require(["insignia","jquery"],function(insignia){

  var browserURL = window.location.href;

  if (jQuery("#removeBkletScript").length == 0){
      jQuery("body").append("<script id='removeBkletScript'>function removeBklet(){jQuery('#fairness-bklet-wrapper').remove();}</script>")
  }

  var fairQuestions = JSON.parse(jQuery.ajax({
      async: false,
      url: 'https://fairshake.cloud/api/getQ?',
      data: {
          'url': browserURL
      },
      success: function (data) {
          if (data == 'None') {
              notFound();
          }
      }
  }).responseText);

  var fairScores = JSON.parse(jQuery.ajax({
      async: false,
      url: 'https://fairshake.cloud/api/getAvg?',
      data: {
          'url': browserURL
      }
  }).responseText);

  function makeInsig(scoreReturned, questions) {
      scoreDict = {}
      for (i=0;i<scoreReturned.length;i++){
          scoreDict[(i+1)] = scoreReturned[i];
      }
      scores = {1: scoreDict};
      insignia.build_svg(".fairness-bklet-insig",scores,questions);
  }

  function makeBlankInsig(questions) {
  }

  function notFound(){
      jQuery("#fairshakeBkletLink").html("FAIRness data unavailable.");
  }

  jQuery(document).ready(function(){
      if (jQuery("fairness-bklet-wrapper").length == 0){
          jQuery("body").append(
              "<div id='fairness-bklet-wrapper'>" +
                  "<div id='fairness-bklet' style='font-size:12px;text-align:left;font-family:arial, helvetica, clean, sans-serif;line-height:15px;width:120px;background-color:white;position:fixed;right:0;top:0;z-index:2147483636;padding:10px;-moz-box-shadow:0px 0px 5px #333333;-webkit-box-shadow:0px 0px 5px #333333;box-shadow:0px 0px 5px #333333'>" +
                      "<div class='fairness-bklet-insig' style='width:40px; height:40px; margin:0 auto; padding-bottom:10px; shape-rendering:crispEdges;'></div>" +
                      "<div id='fairshakeBkletInfo' style='text-align:center;word-wrap:break-word;'>" +
                          "<a id='fairshakeBkletLink' href='https://fairshake.cloud' style='font-family:arial;line-height:15px;font-size:12px;color:#337ab7;'></a>" +
                      "</div>" +
                      "<a id='close-overlay' onclick='removeBklet();' href='javascript:void(0)' style='line-height:10px;text-decoration:none;position:absolute;top:0;right:0;background:#eee;font-size:0.9em;padding:2px 5px;border:solid #ccc;border-width:0 0 1px 1px;display:block;'>X</a>" +
                  "</div>" +
              "</div>"
          );

          if (fairQuestions == undefined || fairQuestions == 'None'){
              notFound();
          } else {
              jQuery("#fairshakeBkletInfo").append("<p>FAIRness Insignia\n" + fairQuestions[(fairQuestions.length)-3] + "</p>");
              jQuery("#fairshakeBkletLink").html("Submit evaluation");
              jQuery("#fairshakeBkletLink").attr("href","https://fairshake.cloud/newevaluation?resourceid="+fairQuestions[(fairQuestions.length)-2]);

              if (fairScores == 'None'){
                  makeBlankInsig(fairQuestions);
              } else {
                  makeInsig(fairScores, fairQuestions);
              }
          }
      }
  });
});
