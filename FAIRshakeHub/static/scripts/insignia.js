// var d3 = require('d3')

function build_insignia_svg(container, scores) {
  // Construct the insignia with arbitrary scores and summaries
  //
  // params:
  //   container: div/element where the svg element will be appended
  //   scores: {rubric-id: {metrid-id: {average: 0, metric: ...}, ...}, ...}
  //
  // Description:
  // This constructs a nested square where the outer square consists
  // of square blocks corresponding to each score in scores and inner
  // squares corresponding to each average in that particular score.
  //
  //     1<n<=4 summaries in second score
  //       \/
  // |--------|-------|
  // |        |___|___|
  // |        |   |   |
  // |--------|-------|
  // |--------|-------|
  // |__|__|__|       | < 1 summary in 1st and fourth score
  // |  |  |  |       | 
  // |--------|-------|
  //   /\
  // 4<n<=9 summaries in third score
  //
  // Color is linarly chosen between Red (0) and Blue (1).

  var color =
    d3.scaleLinear()
    .domain([-1, 1])
    .interpolate(d3.interpolateRgb)
    .range([
      d3.rgb(255,0,0),
      d3.rgb(0,0,255),
    ])

  var svg =
    d3.select(container)
      .append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('preserveAspectRatio', 'xMinYMin')
      .attr('viewBox', '0 0 1 1')

  function nearest_sq(n) {
    // Find the nearest square to build the insignia
    return Math.ceil(Math.sqrt(n))
  }

  var scores_sq = nearest_sq(Object.keys(scores).length)
  var abs_unit = 1 / scores_sq
  Object.keys(scores).forEach(function(rubric, i) {
    var score = scores[rubric]
    var summary_sq = nearest_sq(Object.keys(score).length)
    var abs_x = (i % scores_sq) * abs_unit
    var abs_y = Math.floor(i / scores_sq) * abs_unit
    var local_unit = 1 / (scores_sq * summary_sq)

    Object.keys(score).forEach(function(summary, j) {
      var average = score[summary]
      var description = summary // TODO
      var local_x = (j % summary_sq) * local_unit
      var local_y = Math.floor(j / summary_sq) * local_unit

      svg
        .append('rect')
        .attr('x', abs_x + local_x)
        .attr('y', abs_y + local_y)
        .attr('width', local_unit)
        .attr('height', local_unit)
        .attr('stroke', '#ffffff')
        .attr('stroke-width', abs_unit / 10)
        .attr('fill', color(average))
        .attr('data-toggle', 'tooltip')
        .attr('data-placement', 'right')
        .attr('data-container', 'body')
        .attr('data-original-title', function(d) {
          return 'Score (' + average + '): ' + description
        })
        .attr('data-html', 'true')
    })
  })
}
