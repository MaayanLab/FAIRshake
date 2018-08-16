require.config({
  paths: {
    d3: 'https://cdnjs.cloudflare.com/ajax/libs/d3/5.5.0/d3.min',
    tippy: 'https://unpkg.com/tippy.js@2.5.2/dist/tippy.all.min',
    coreapi: 'https://fairshake.cloud/v2/static/rest_framework/js/coreapi-0.1.1',
    schema: 'https://fairshake.cloud/v2/coreapi/schema',
  },
  shims: {
    schema: ['coreapi']
  }
})

define(function(require) {
  function nearest_sq(n) {
    // Find the nearest square to build the insignia
    return Math.ceil(Math.sqrt(n))
  }

  function create_sq(svg, props) {
    // Add a square to an svg
    // props: svg, x, y, size, strokeSize, fillColor, link, tooltip
    var sq = svg.append('rect')
    sq
      .attr('x', props.x)
      .attr('y', props.y)
      .attr('width', props.size)
      .attr('height', props.size)
      .attr('stroke', '#ffffff')
      .attr('stroke-width', props.strokeSize)
      .attr('fill', props.fillColor)

    if (props.tooltip !== undefined) {
      sq
        .attr('class', 'insignia-tooltip')
        .attr('data-tippy-delay', '0')
        .attr('data-tippy-size', 'large')
        .attr('data-tippy-placement', 'right')
        .attr('data-container', 'body')
        .attr('title', props.tooltip)
    }
    
    if (props.link !== undefined) {
      sq.on('click', function() {
        window.location = props.link
      })
    }

    return sq
  }

  function build_svg(container, scores, settings) {
    // Construct the insignia with arbitrary scores and summaries
    //
    // params:
    //   container: div/element where the svg element will be appended
    //   scores: {rubric-id: {metrid-id: 0, ...}, ...}
    //   settings (optional): {tooltips: {}, color: d3 range, svg: container, tooltip: boolean}
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

    // D3 Dependency
    var d3 = require('d3')

    // Default settings
    if (settings === undefined)
      settings = {}

    var tooltips = settings.tooltips
    var links = settings.links

    var color = settings.color !== undefined ? settings.color :
      d3.scaleLinear()
        .domain([-1, 1])
        .interpolate(d3.interpolateRgb)
        .range([
          d3.rgb(255, 0, 0),
          d3.rgb(0, 0, 255),
        ])

    var svg = settings.svg !== undefined ? settings.svg :
      d3.select(container)
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('preserveAspectRatio', 'xMinYMin')
        .attr('viewBox', '0 0 1 1')

    var n_scores = Object.keys(scores).length
    var scores_sq = n_scores > 0 ? nearest_sq(n_scores) : 3
    var abs_unit = 1 / scores_sq
    Object.keys(scores).forEach(function (rubric, i) {
      var score = scores[rubric]
      var n_score = Object.keys(score).length
      var summary_sq = n_score > 0 ? nearest_sq(n_score) : 3
      var abs_x = (i % scores_sq) * abs_unit
      var abs_y = Math.floor(i / scores_sq) * abs_unit
      var local_unit = 1 / (scores_sq * summary_sq)

      Object.keys(score).forEach(function (summary, j) {
        var average = score[summary]
        var local_x = (j % summary_sq) * local_unit
        var local_y = Math.floor(j / summary_sq) * local_unit

        create_sq(svg, {
          x: abs_x + local_x,
          y: abs_y + local_y,
          size: local_unit,
          strokeSize: abs_unit / 40,
          fillColor: isNaN(average) ? 'darkgray' : color(average),
          tooltip: tooltips !== undefined ? tooltips(rubric, summary, average) : undefined,
          link: links !== undefined ? links(rubric, summary, average) : undefined,
        })
      })

      for(var j = n_score; j < summary_sq*summary_sq; j++) {
        var local_x = (j % summary_sq) * local_unit
        var local_y = Math.floor(j / summary_sq) * local_unit

        create_sq(svg, {
          x: abs_x + local_x,
          y: abs_y + local_y,
          size: local_unit,
          strokeSize: abs_unit / 40,
          fillColor: 'lightgrey',
        })
      }
    })

    for(var i = n_scores; i < scores_sq*scores_sq; i++) {
      var abs_x = (i % scores_sq) * abs_unit
      var abs_y = Math.floor(i / scores_sq) * abs_unit

      create_sq(svg, {
        x: abs_x,
        y: abs_y,
        size: abs_unit,
        strokeSize: abs_unit / 40,
        fillColor: 'lightgrey',
      })
    }

    if (tooltips !== undefined) {
      var tippy = require('tippy')
      tippy('.insignia-tooltip')
    }
  }

  function build_svg_from_score(container, params) {
    var coreapi = window.coreapi = require('coreapi')
    require(['schema'], function() {
      var schema = window.schema
      var client = new window.coreapi.Client()
      client
        .action(schema, ['score', 'list'], params)
        .then(function (results) {
          build_svg(
            container,
            results.scores,
            {
              tooltips: function(rubric, metric, score) {
                return 'Score: ' + ((score + 1) * 50).toFixed(0) + '%<br />' + results.metrics[metric]
              },
              links: function(rubric, metric, score) {
                return 'https://fairshake.cloud/v2/metric/' + metric + '/'
              },
            }
          )
        })
    })
  }
  
  return {
    build_svg: build_svg,
    build_svg_from_score: build_svg_from_score
  }
})
