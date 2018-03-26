var theURL = window.location.href;
jQuery(document).ready(function(){
var theQ = JSON.parse(jQuery.ajax({
    async: false,
    url: 'http://54.175.203.110/fairshake/api/getQ?',
//    url: 'http://127.0.0.1:5000/fairshake/api/getQ?',
    data: {
        'url': theURL
    },
    success: function   (data) {
        if (data == 'None') {
            notFound();
        }
    }
}).responseText);

if (theQ == undefined){ // something went wrong: the ajax request did not load or gave an error
    notFound();
} else if (theQ !== 'None'){

    var fairshakeInfo = document.getElementById("fairshakeBkletInfo");
    fairshakeInfo.innerText = "FAIRness Insignia\n" + theQ[(theQ.length)-3]; //add resource name in overlay
    var fairshakeLink = document.getElementById("fairshakeBkletLink");
    fairshakeLink.innerText = "Submit evaluation";
    fairshakeLink.setAttribute("href","http://54.175.203.110/fairshake/newevaluation?resourceid="+theQ[(theQ.length)-2]) //link to evaluation form

    jQuery.ajax({
        async: false,
        url: 'http://54.175.203.110/fairshake/api/getAvg?',
//        url: 'http://127.0.0.1:5000/fairshake/api/getAvg?',
        data: {
    //        'select': 'URL',
            'url': theURL
        },
        success: function (data) {
            if (data == 'None') {
                makeBlankInsig(theQ); //if getQ returns something but getAvg returns none - in database but no evaluations submitted yet
            } else {
                makeInsig(data, theQ);
            }
        }
    });
}

function makeInsig(avg, qstns) {

    scale = d3.scale.linear().domain([-1, 1])
        .interpolate(d3.interpolateRgb)
        .range([d3.rgb(255, 0, 0), d3.rgb(0, 0, 255)]);

    var body = d3.select(".fairness-bklet-insig").append("svg").attr("width", 40).attr("height", 40).attr("style","display:block;margin:0 auto;");

    body.selectAll("rect.fairness-bklet-insig").data(getData(avg, qstns)).enter().append("rect").attr("class", "fairness-bklet-insig")
        .attr("height",getSqDimension(qstns)).attr("width",getSqDimension(qstns))
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

    body.selectAll("rect.btn").data(getData(avg, qstns)).enter().append("rect").attr("class", "btn")
        .attr("height",getSqDimension(qstns)).attr("width",getSqDimension(qstns))
        .attr("x", function (d) {
            return d.posx;
        }).attr("y", function (d) {
        return d.posy;
        }).style("fill-opacity", 0)
        .on("mouseover", opac)
        .on("mouseout", bopac)
    ;
}

function makeBlankInsig(qstns) {
    var body = d3.select(".fairness-bklet-insig").append("svg").attr("width", 40).attr("height", 40).attr("style","display:block;margin:0 auto;");

    body.selectAll("rect.fairness-bklet-insig").data(getBlankData(qstns)).enter().append("rect").attr("class", "fairness-bklet-insig")
        .attr("id", function (d, i) {
            return "insigBkletSq-" + (i + 1)
        })
        .attr("height",getSqDimension(qstns)).attr("width",getSqDimension(qstns))
        .attr("x", function (d) {
            return d.posx;
        }).attr("y", function (d) {
        return d.posy;
        }).style("fill", "darkgray").style("stroke", "white").style("stroke-width", 1).style("shape-rendering", "crispEdges");

    body.selectAll("rect.btn").data(getBlankData(qstns)).enter().append("rect").attr("class", "btn")
        .attr("height",getSqDimension(qstns)).attr("width",getSqDimension(qstns))
        .attr("x", function (d) {
            return d.posx;
        }).attr("y", function (d) {
        return d.posy;
        }).style("fill-opacity", 0)
        .on("mouseover", opacBlank)
        .on("mouseout", bopac)
    ;
}

function getData(avg,qstns) {
    sqnum=qstns[(qstns.length-1)];
  
    if (sqnum==4){
        return [{numdata: avg[0], qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {numdata: avg[1], qdata: "2. " + qstns[1], posx: 20, posy: 0},
            {numdata: avg[2], qdata: "3. " + qstns[2], posx: 0, posy: 20},
            {numdata: avg[3], qdata: "4. " + qstns[3], posx: 20, posy: 20}
        ]
    } else if (sqnum==9){
        return [{numdata: avg[0], qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {numdata: avg[1], qdata: "2. " + qstns[1], posx: 13, posy: 0},
            {numdata: avg[2], qdata: "3. " + qstns[2], posx: 26, posy: 0},
            {numdata: avg[3], qdata: "4. " + qstns[3], posx: 0, posy: 13},
            {numdata: avg[4], qdata: "5. " + qstns[4], posx: 13, posy: 13},
            {numdata: avg[5], qdata: "6. " + qstns[5], posx: 26, posy: 13},
            {numdata: avg[6], qdata: "7. " + qstns[6], posx: 0, posy: 26},
            {numdata: avg[7], qdata: "8. " + qstns[7], posx: 13, posy: 26},
            {numdata: avg[8], qdata: "9. " + qstns[8], posx: 26, posy: 26}
        ]
    } else if (sqnum==16){
        return [{numdata: avg[0], qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {numdata: avg[1], qdata: "2. " + qstns[1], posx: 10, posy: 0},
            {numdata: avg[2], qdata: "3. " + qstns[2], posx: 20, posy: 0},
            {numdata: avg[3], qdata: "4. " + qstns[3], posx: 30, posy: 0},
            {numdata: avg[4], qdata: "5. " + qstns[4], posx: 0, posy: 10},
            {numdata: avg[5], qdata: "6. " + qstns[5], posx: 10, posy: 10},
            {numdata: avg[6], qdata: "7. " + qstns[6], posx: 20, posy: 10},
            {numdata: avg[7], qdata: "8. " + qstns[7], posx: 30, posy: 10},
            {numdata: avg[8], qdata: "9. " + qstns[8], posx: 0, posy: 20},
            {numdata: avg[9], qdata: "10. " + qstns[9], posx: 10, posy: 20},
            {numdata: avg[10], qdata: "11. " + qstns[10], posx: 20, posy: 20},
            {numdata: avg[11], qdata: "12. " + qstns[11], posx: 30, posy: 20},
            {numdata: avg[12], qdata: "13. " + qstns[12], posx: 0, posy: 30},
            {numdata: avg[13], qdata: "14. " + qstns[13], posx: 10, posy: 30},
            {numdata: avg[14], qdata: "15. " + qstns[14], posx: 20, posy: 30},
            {numdata: avg[15], qdata: "16. " + qstns[15], posx: 30, posy: 30}
        ]
    } else if (sqnum==25){
        return [{numdata: avg[0], qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {numdata: avg[1], qdata: "2. " + qstns[1], posx: 8, posy: 0},
            {numdata: avg[2], qdata: "3. " + qstns[2], posx: 16, posy: 0},
            {numdata: avg[3], qdata: "4. " + qstns[3], posx: 24, posy: 0},
            {numdata: avg[4], qdata: "5. " + qstns[4], posx: 32, posy: 0},
            {numdata: avg[5], qdata: "6. " + qstns[5], posx: 0, posy: 8},
            {numdata: avg[6], qdata: "7. " + qstns[6], posx: 8, posy: 8},
            {numdata: avg[7], qdata: "8. " + qstns[7], posx: 16, posy: 8},
            {numdata: avg[8], qdata: "9. " + qstns[8], posx: 24, posy: 8},
            {numdata: avg[9], qdata: "10. " + qstns[9], posx: 32, posy: 8},
            {numdata: avg[10], qdata: "11. " + qstns[10], posx: 0, posy: 16},
            {numdata: avg[11], qdata: "12. " + qstns[11], posx: 8, posy: 16},
            {numdata: avg[12], qdata: "13. " + qstns[12], posx: 16, posy: 16},
            {numdata: avg[13], qdata: "14. " + qstns[13], posx: 24, posy: 16},
            {numdata: avg[14], qdata: "15. " + qstns[14], posx: 32, posy: 16},
            {numdata: avg[15], qdata: "16. " + qstns[15], posx: 0, posy: 24},
            {numdata: avg[16], qdata: "17. " + qstns[16], posx: 8, posy: 24},
            {numdata: avg[17], qdata: "18. " + qstns[17], posx: 16, posy: 24},
            {numdata: avg[18], qdata: "19. " + qstns[18], posx: 24, posy: 24},
            {numdata: avg[19], qdata: "20. " + qstns[19], posx: 32, posy: 24},
            {numdata: avg[20], qdata: "21. " + qstns[20], posx: 0, posy: 32},
            {numdata: avg[21], qdata: "22. " + qstns[21], posx: 8, posy: 32},
            {numdata: avg[22], qdata: "23. " + qstns[22], posx: 16, posy: 32},
            {numdata: avg[23], qdata: "24. " + qstns[23], posx: 24, posy: 32},
            {numdata: avg[24], qdata: "25. " + qstns[24], posx: 32, posy: 32},
        ]
    }
}

function getSqDimension(qstns){
    sqnum=qstns[(qstns.length-1)];
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

function getBlankData(qstns) {
    sqnum=qstns[(qstns.length-1)];

    if (sqnum==4){
        return [{qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {qdata: "2. " + qstns[1], posx: 20, posy: 0},
            {qdata: "3. " + qstns[2], posx: 0, posy: 20},
            {qdata: "4. " + qstns[3], posx: 20, posy: 20}
        ]
    } else if (sqnum==9){
        return [{qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {qdata: "2. " + qstns[1], posx: 13, posy: 0},
            {qdata: "3. " + qstns[2], posx: 26, posy: 0},
            {qdata: "4. " + qstns[3], posx: 0, posy: 13},
            {qdata: "5. " + qstns[4], posx: 13, posy: 13},
            {qdata: "6. " + qstns[5], posx: 26, posy: 13},
            {qdata: "7. " + qstns[6], posx: 0, posy: 26},
            {qdata: "8. " + qstns[7], posx: 13, posy: 26},
            {qdata: "9. " + qstns[8], posx: 26, posy: 26}
        ]
    } else if (sqnum==16){
        return [{qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {qdata: "2. " + qstns[1], posx: 10, posy: 0},
            {qdata: "3. " + qstns[2], posx: 20, posy: 0},
            {qdata: "4. " + qstns[3], posx: 30, posy: 0},
            {qdata: "5. " + qstns[4], posx: 0, posy: 10},
            {qdata: "6. " + qstns[5], posx: 10, posy: 10},
            {qdata: "7. " + qstns[6], posx: 20, posy: 10},
            {qdata: "8. " + qstns[7], posx: 30, posy: 10},
            {qdata: "9. " + qstns[8], posx: 0, posy: 20},
            {qdata: "10. " + qstns[9], posx: 10, posy: 20},
            {qdata: "11. " + qstns[10], posx: 20, posy: 20},
            {qdata: "12. " + qstns[11], posx: 30, posy: 20},
            {qdata: "13. " + qstns[12], posx: 0, posy: 30},
            {qdata: "14. " + qstns[13], posx: 10, posy: 30},
            {qdata: "15. " + qstns[14], posx: 20, posy: 30},
            {qdata: "16. " + qstns[15], posx: 30, posy: 30}
        ]
    } else if (sqnum==25){
        return [{qdata: "1. " + qstns[0], posx: 0, posy: 0},
            {qdata: "2. " + qstns[1], posx: 8, posy: 0},
            {qdata: "3. " + qstns[2], posx: 16, posy: 0},
            {qdata: "4. " + qstns[3], posx: 24, posy: 0},
            {qdata: "5. " + qstns[4], posx: 32, posy: 0},
            {qdata: "6. " + qstns[5], posx: 0, posy: 8},
            {qdata: "7. " + qstns[6], posx: 8, posy: 8},
            {qdata: "8. " + qstns[7], posx: 16, posy: 8},
            {qdata: "9. " + qstns[8], posx: 24, posy: 8},
            {qdata: "10. " + qstns[9], posx: 32, posy: 8},
            {qdata: "11. " + qstns[10], posx: 0, posy: 16},
            {qdata: "12. " + qstns[11], posx: 8, posy: 16},
            {qdata: "13. " + qstns[12], posx: 16, posy: 16},
            {qdata: "14. " + qstns[13], posx: 24, posy: 16},
            {qdata: "15. " + qstns[14], posx: 32, posy: 16},
            {qdata: "16. " + qstns[15], posx: 0, posy: 24},
            {qdata: "17. " + qstns[16], posx: 8, posy: 24},
            {qdata: "18. " + qstns[17], posx: 16, posy: 24},
            {qdata: "19. " + qstns[18], posx: 24, posy: 24},
            {qdata: "20. " + qstns[19], posx: 32, posy: 24},
            {qdata: "21. " + qstns[20], posx: 0, posy: 32},
            {qdata: "22. " + qstns[21], posx: 8, posy: 32},
            {qdata: "23. " + qstns[22], posx: 16, posy: 32},
            {qdata: "24. " + qstns[23], posx: 24, posy: 32},
            {qdata: "25. " + qstns[24], posx: 32, posy: 32},
        ]
    }
}

function roundTwo(num) {
    return +(Math.round(num + "e+2") + "e-2");
}

function opac(d, i) {
    d3.select("#insigBkletSq-" + (i + 1)).style("fill-opacity", .3);
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

function opacBlank(d, i) {
    d3.select("#insigBkletSq-" + (i + 1)).style("fill-opacity", .3);
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

function bopac(d, i) {
    d3.select("#insigBkletSq-" + (i + 1)).style("fill-opacity", 1);
    d3.selectAll("#fairnessBkletTooltip").remove();
}

function notFound(){
    document.getElementById("fairshakeBkletLink").innerText = "FAIRness data unavailable.";
}
});