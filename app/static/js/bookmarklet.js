require.config({
    paths: {
        "jquery": "https://ajax.googleapis.com/ajax/libs/jquery/1.4.4/jquery.min",
        "d3": "https://d3js.org/d3.v3.min"
    }
});
require(["jquery","d3"],function(){
    var browserURL = window.location.href;

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

    function removeBklet(){
        jQuery("#fairness-bklet-wrapper").remove();
    }

    function makeInsig(scores, questions) {

        scale = d3.scale.linear().domain([-1, 1])
            .interpolate(d3.interpolateRgb)
            .range([d3.rgb(255, 0, 0), d3.rgb(0, 0, 255)]);

        var body = d3.select(".fairness-bklet-insig").append("svg").attr("width", 40).attr("height", 40)
            .attr("style","display:block;margin:0 auto;padding-bottom:10px;");

        body.selectAll("rect.fairness-bklet-insig").data(getData(scores, questions)).enter().append("rect").attr("class", "fairness-bklet-insig")
            .attr("height",getSqDimension(questions)).attr("width",getSqDimension(questions))
            .attr("id", function (d, i) {
                return "insigBkletSq-" + (i + 1)
            })
            .attr("x", function (d) {
                return d.posx;
            }).attr("y", function (d) {
            return d.posy;
            }).style("fill", function (d) {
            return scale(d.numdata);
            })
            .style("stroke", "white").style("stroke-width", 1).style("shape-rendering", "crispEdges");

        body.selectAll("rect.btn").data(getData(scores, questions)).enter().append("rect").attr("class", "btn")
            .attr("height",getSqDimension(questions)).attr("width",getSqDimension(questions))
            .attr("x", function (d) {
                return d.posx;
            }).attr("y", function (d) {
            return d.posy;
            }).style("fill-opacity", 0)
            .on("mouseover", hoverOver)
            .on("mouseout", hoverOut)
        ;
    }

    function makeBlankInsig(questions) {
        var body = d3.select(".fairness-bklet-insig").append("svg").attr("width", 40).attr("height", 40)
            .attr("style","display:block;margin:0 auto;padding-bottom:10px;");

        body.selectAll("rect.fairness-bklet-insig").data(getBlankData(questions)).enter().append("rect").attr("class", "fairness-bklet-insig")
            .attr("id", function (d, i) {
                return "insigBkletSq-" + (i + 1)
            })
            .attr("height",getSqDimension(questions)).attr("width",getSqDimension(questions))
            .attr("x", function (d) {
                return d.posx;
            }).attr("y", function (d) {
            return d.posy;
            }).style("fill", "darkgray").style("stroke", "white").style("stroke-width", 1).style("shape-rendering", "crispEdges");

        body.selectAll("rect.btn").data(getBlankData(questions)).enter().append("rect").attr("class", "btn")
            .attr("height",getSqDimension(questions)).attr("width",getSqDimension(questions))
            .attr("x", function (d) {
                return d.posx;
            }).attr("y", function (d) {
            return d.posy;
            }).style("fill-opacity", 0)
            .on("mouseover", hoverOverGray)
            .on("mouseout", hoverOut)
        ;
    }

    function getData(scores,questions) {
        sqnum=questions[(questions.length-1)];

        if (sqnum==4){
            return [{numdata: scores[0], qdata: "1. " + questions[0], posx: 0, posy: 0},
                {numdata: scores[1], qdata: "2. " + questions[1], posx: 20, posy: 0},
                {numdata: scores[2], qdata: "3. " + questions[2], posx: 0, posy: 20},
                {numdata: scores[3], qdata: "4. " + questions[3], posx: 20, posy: 20}
            ]
        } else if (sqnum==9){
            return [{numdata: scores[0], qdata: "1. " + questions[0], posx: 0, posy: 0},
                {numdata: scores[1], qdata: "2. " + questions[1], posx: 13, posy: 0},
                {numdata: scores[2], qdata: "3. " + questions[2], posx: 26, posy: 0},
                {numdata: scores[3], qdata: "4. " + questions[3], posx: 0, posy: 13},
                {numdata: scores[4], qdata: "5. " + questions[4], posx: 13, posy: 13},
                {numdata: scores[5], qdata: "6. " + questions[5], posx: 26, posy: 13},
                {numdata: scores[6], qdata: "7. " + questions[6], posx: 0, posy: 26},
                {numdata: scores[7], qdata: "8. " + questions[7], posx: 13, posy: 26},
                {numdata: scores[8], qdata: "9. " + questions[8], posx: 26, posy: 26}
            ]
        } else if (sqnum==16){
            return [{numdata: scores[0], qdata: "1. " + questions[0], posx: 0, posy: 0},
                {numdata: scores[1], qdata: "2. " + questions[1], posx: 10, posy: 0},
                {numdata: scores[2], qdata: "3. " + questions[2], posx: 20, posy: 0},
                {numdata: scores[3], qdata: "4. " + questions[3], posx: 30, posy: 0},
                {numdata: scores[4], qdata: "5. " + questions[4], posx: 0, posy: 10},
                {numdata: scores[5], qdata: "6. " + questions[5], posx: 10, posy: 10},
                {numdata: scores[6], qdata: "7. " + questions[6], posx: 20, posy: 10},
                {numdata: scores[7], qdata: "8. " + questions[7], posx: 30, posy: 10},
                {numdata: scores[8], qdata: "9. " + questions[8], posx: 0, posy: 20},
                {numdata: scores[9], qdata: "10. " + questions[9], posx: 10, posy: 20},
                {numdata: scores[10], qdata: "11. " + questions[10], posx: 20, posy: 20},
                {numdata: scores[11], qdata: "12. " + questions[11], posx: 30, posy: 20},
                {numdata: scores[12], qdata: "13. " + questions[12], posx: 0, posy: 30},
                {numdata: scores[13], qdata: "14. " + questions[13], posx: 10, posy: 30},
                {numdata: scores[14], qdata: "15. " + questions[14], posx: 20, posy: 30},
                {numdata: scores[15], qdata: "16. " + questions[15], posx: 30, posy: 30}
            ]
        } else if (sqnum==25){
            return [{numdata: scores[0], qdata: "1. " + questions[0], posx: 0, posy: 0},
                {numdata: scores[1], qdata: "2. " + questions[1], posx: 8, posy: 0},
                {numdata: scores[2], qdata: "3. " + questions[2], posx: 16, posy: 0},
                {numdata: scores[3], qdata: "4. " + questions[3], posx: 24, posy: 0},
                {numdata: scores[4], qdata: "5. " + questions[4], posx: 32, posy: 0},
                {numdata: scores[5], qdata: "6. " + questions[5], posx: 0, posy: 8},
                {numdata: scores[6], qdata: "7. " + questions[6], posx: 8, posy: 8},
                {numdata: scores[7], qdata: "8. " + questions[7], posx: 16, posy: 8},
                {numdata: scores[8], qdata: "9. " + questions[8], posx: 24, posy: 8},
                {numdata: scores[9], qdata: "10. " + questions[9], posx: 32, posy: 8},
                {numdata: scores[10], qdata: "11. " + questions[10], posx: 0, posy: 16},
                {numdata: scores[11], qdata: "12. " + questions[11], posx: 8, posy: 16},
                {numdata: scores[12], qdata: "13. " + questions[12], posx: 16, posy: 16},
                {numdata: scores[13], qdata: "14. " + questions[13], posx: 24, posy: 16},
                {numdata: scores[14], qdata: "15. " + questions[14], posx: 32, posy: 16},
                {numdata: scores[15], qdata: "16. " + questions[15], posx: 0, posy: 24},
                {numdata: scores[16], qdata: "17. " + questions[16], posx: 8, posy: 24},
                {numdata: scores[17], qdata: "18. " + questions[17], posx: 16, posy: 24},
                {numdata: scores[18], qdata: "19. " + questions[18], posx: 24, posy: 24},
                {numdata: scores[19], qdata: "20. " + questions[19], posx: 32, posy: 24},
                {numdata: scores[20], qdata: "21. " + questions[20], posx: 0, posy: 32},
                {numdata: scores[21], qdata: "22. " + questions[21], posx: 8, posy: 32},
                {numdata: scores[22], qdata: "23. " + questions[22], posx: 16, posy: 32},
                {numdata: scores[23], qdata: "24. " + questions[23], posx: 24, posy: 32},
                {numdata: scores[24], qdata: "25. " + questions[24], posx: 32, posy: 32},
            ]
        }
    }

    function getSqDimension(questions){
        sqnum=questions[(questions.length-1)];
        var sqDimension=0;
        if(sqnum==4){
            var sqDimension=20;
        } else if(sqnum==9){
            var sqDimension=13;
        } else if(sqnum==16){
            var sqDimension=10;
        } else if(sqnum==25){
            var sqDimension=8;
        }
        return sqDimension;
    }

    function getBlankData(questions) {
        sqnum=questions[(questions.length-1)];

        if (sqnum==4){
            return [{qdata: "1. " + questions[0], posx: 0, posy: 0},
                {qdata: "2. " + questions[1], posx: 20, posy: 0},
                {qdata: "3. " + questions[2], posx: 0, posy: 20},
                {qdata: "4. " + questions[3], posx: 20, posy: 20}
            ]
        } else if (sqnum==9){
            return [{qdata: "1. " + questions[0], posx: 0, posy: 0},
                {qdata: "2. " + questions[1], posx: 13, posy: 0},
                {qdata: "3. " + questions[2], posx: 26, posy: 0},
                {qdata: "4. " + questions[3], posx: 0, posy: 13},
                {qdata: "5. " + questions[4], posx: 13, posy: 13},
                {qdata: "6. " + questions[5], posx: 26, posy: 13},
                {qdata: "7. " + questions[6], posx: 0, posy: 26},
                {qdata: "8. " + questions[7], posx: 13, posy: 26},
                {qdata: "9. " + questions[8], posx: 26, posy: 26}
            ]
        } else if (sqnum==16){
            return [{qdata: "1. " + questions[0], posx: 0, posy: 0},
                {qdata: "2. " + questions[1], posx: 10, posy: 0},
                {qdata: "3. " + questions[2], posx: 20, posy: 0},
                {qdata: "4. " + questions[3], posx: 30, posy: 0},
                {qdata: "5. " + questions[4], posx: 0, posy: 10},
                {qdata: "6. " + questions[5], posx: 10, posy: 10},
                {qdata: "7. " + questions[6], posx: 20, posy: 10},
                {qdata: "8. " + questions[7], posx: 30, posy: 10},
                {qdata: "9. " + questions[8], posx: 0, posy: 20},
                {qdata: "10. " + questions[9], posx: 10, posy: 20},
                {qdata: "11. " + questions[10], posx: 20, posy: 20},
                {qdata: "12. " + questions[11], posx: 30, posy: 20},
                {qdata: "13. " + questions[12], posx: 0, posy: 30},
                {qdata: "14. " + questions[13], posx: 10, posy: 30},
                {qdata: "15. " + questions[14], posx: 20, posy: 30},
                {qdata: "16. " + questions[15], posx: 30, posy: 30}
            ]
        } else if (sqnum==25){
            return [{qdata: "1. " + questions[0], posx: 0, posy: 0},
                {qdata: "2. " + questions[1], posx: 8, posy: 0},
                {qdata: "3. " + questions[2], posx: 16, posy: 0},
                {qdata: "4. " + questions[3], posx: 24, posy: 0},
                {qdata: "5. " + questions[4], posx: 32, posy: 0},
                {qdata: "6. " + questions[5], posx: 0, posy: 8},
                {qdata: "7. " + questions[6], posx: 8, posy: 8},
                {qdata: "8. " + questions[7], posx: 16, posy: 8},
                {qdata: "9. " + questions[8], posx: 24, posy: 8},
                {qdata: "10. " + questions[9], posx: 32, posy: 8},
                {qdata: "11. " + questions[10], posx: 0, posy: 16},
                {qdata: "12. " + questions[11], posx: 8, posy: 16},
                {qdata: "13. " + questions[12], posx: 16, posy: 16},
                {qdata: "14. " + questions[13], posx: 24, posy: 16},
                {qdata: "15. " + questions[14], posx: 32, posy: 16},
                {qdata: "16. " + questions[15], posx: 0, posy: 24},
                {qdata: "17. " + questions[16], posx: 8, posy: 24},
                {qdata: "18. " + questions[17], posx: 16, posy: 24},
                {qdata: "19. " + questions[18], posx: 24, posy: 24},
                {qdata: "20. " + questions[19], posx: 32, posy: 24},
                {qdata: "21. " + questions[20], posx: 0, posy: 32},
                {qdata: "22. " + questions[21], posx: 8, posy: 32},
                {qdata: "23. " + questions[22], posx: 16, posy: 32},
                {qdata: "24. " + questions[23], posx: 24, posy: 32},
                {qdata: "25. " + questions[24], posx: 32, posy: 32},
            ]
        }
    }

    function roundTwo(num) {
        return +(Math.round(num + "e+2") + "e-2");
    }

    function hoverOver(d, i) {
        d3.select("#insigBkletSq-" + (i + 1)).style("fill-opacity",".3");
        var div = d3.select("body").append("div")
            .attr("class", "tooltip").attr("id","fairnessBkletTooltip").style("opacity", 0)
            .style("position","absolute").style("padding","2px").style("font","13px sans-serif").style("background","black").style("color","white")
            .style("border-radius","2px").style("pointer-events","none").style("z-index","2147483637").style("text-align","left").style("visibility","visible")
            .style("display","block");

        div.transition().style("opacity", .8);
        div.html("Score: " + roundTwo(d.numdata) + "<br>" + d.qdata)
            .style("left", (d3.event.pageX - 50) + "px")
            .style("top", (d3.event.pageY + 25) + "px");
    }

    function hoverOverGray(d, i) {
        d3.select("#insigBkletSq-" + (i + 1)).style("fill-opacity",".3");
        var div = d3.select("body").append("div")
            .attr("class", "tooltip").attr("id","fairnessBkletTooltip").style("opacity", 0)
            .style("position","absolute").style("padding","2px").style("font","13px sans-serif").style("background","black").style("color","white")
            .style("border-radius","2px").style("pointer-events","none").style("z-index","2147483637").style("text-align","left").style("visibility","visible")
            .style("display","block");

        div.transition().style("opacity", .8);
        div.html("Score: " + "N/A" + "<br>" + d.qdata)
            .style("left", (d3.event.pageX - 50) + "px")
            .style("top", (d3.event.pageY + 25) + "px");
    }

    function hoverOut(d, i) {
        d3.select("#insigBkletSq-" + (i + 1)).style("fill-opacity","1");
        jQuery("#fairnessBkletTooltip").remove();
    }

    function notFound(){
        jQuery("#fairshakeBkletLink").html("FAIRness data unavailable.");
    }

    jQuery(document).ready(function(){

        jQuery("body").append(
            "<div id='fairness-bklet-wrapper'>" +
                "<div id='fairness-bklet' style='font-size:12px;text-align:left;font-family:arial, helvetica, clean, sans-serif;line-height:15px;width:120px;background-color:white;position:fixed;right:0;top:0;z-index:2147483636;padding:10px;-moz-box-shadow:0px 0px 5px #333333;-webkit-box-shadow:0px 0px 5px #333333;box-shadow:0px 0px 5px #333333'>" +
                    "<div class='fairness-bklet-insig'></div>" +
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
    });
});