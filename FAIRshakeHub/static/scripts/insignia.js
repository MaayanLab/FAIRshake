var url = 'http://fairshake.cloud'

require.config({
  paths: {
    d3: 'https://cdnjs.cloudflare.com/ajax/libs/d3/5.5.0/d3.min',
    coreapi: url + '/api/static/rest_framework/js/coreapi-0.1.1',
    schema: url + '/api/coreapi/schema',
  },
  shims: {
    schema: {
      deps: ['coreapi'],
      exports: 'window.schema',
      init: function(coreapi) {
        window.coreapi = this.window.coreapi = coreapi
        return this
      }
    }
  }
})

define(function(require) {
  return {
    build_svg: function (container, scores, metrics) {
      require(['d3'], function(d3) {
        // Construct the insignia with arbitrary scores and summaries
        //
        // params:
        //   container: div/element where the svg element will be appended
        //   scores: {rubric-id: {metrid-id: 0, ...}, ...}
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
              d3.rgb(255, 0, 0),
              d3.rgb(0, 0, 255),
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

        var n_scores = Object.keys(scores).length
        var scores_sq = nearest_sq(n_scores)
        var abs_unit = 1 / scores_sq
        Object.keys(scores).forEach(function (rubric, i) {
          var score = scores[rubric]
          var n_score = Object.keys(score).length
          var summary_sq = nearest_sq(n_score)
          var abs_x = (i % scores_sq) * abs_unit
          var abs_y = Math.floor(i / scores_sq) * abs_unit
          var local_unit = 1 / (scores_sq * summary_sq)

          Object.keys(score).forEach(function (summary, j) {
            var average = score[summary]
            var description = ''// TODO: metrics[summary].description
            var local_x = (j % summary_sq) * local_unit
            var local_y = Math.floor(j / summary_sq) * local_unit

            svg
              .append('rect')
              .attr('x', abs_x + local_x)
              .attr('y', abs_y + local_y)
              .attr('width', local_unit)
              .attr('height', local_unit)
              .attr('stroke', '#ffffff')
              .attr('stroke-width', abs_unit / 40)
              .attr('fill', color(average))
              .attr('data-toggle', 'tooltip')
              .attr('data-placement', 'right')
              .attr('data-container', 'body')
              .attr('data-original-title', function (d) {
                return 'Score (' + average + '): ' + description
              })
              .attr('data-html', 'true')
          })
          // For filling in the rest with grey squares
          // for(var j = n_score - 1; j < summary_sq; j++) {
          //   var local_x = (j % summary_sq) * local_unit
          //   var local_y = Math.floor(j / summary_sq) * local_unit

          //   svg
          //     .append('rect')
          //     .attr('x', abs_x + local_x)
          //     .attr('y', abs_y + local_y)
          //     .attr('width', local_unit)
          //     .attr('height', local_unit)
          //     .attr('stroke', '#ffffff')
          //     .attr('stroke-width', abs_unit / 10)
          //     .attr('fill', '#aaaaaa')
          // }
        })
        // For filling in the rest with grey squares
        // for(var i = n_scores.length - 1; i < scores_sq; i++) {
        //   var abs_x = (i % scores_sq) * abs_unit
        //   var abs_y = Math.floor(i / scores_sq) * abs_unit

        //   svg
        //     .append('rect')
        //     .attr('x', abs_x)
        //     .attr('y', abs_y)
        //     .attr('width', abs_unit)
        //     .attr('height', abs_unit)
        //     .attr('stroke', '#ffffff')
        //     .attr('stroke-width', abs_unit / 10)
        //     .attr('fill', '#aaaaaa')
        // }
      })
    },
    build_svg_from_score: function (container, params) {
      require(['coreapi', 'schema'], function(coreapi, schema) {
        var client = new coreapi.Client()
        client
          .action(schema, ['score', 'list'], params)
          .then(function (score) {
            build_svg(
              container,
              score,
            )
        })
      })
    }
  }
})
