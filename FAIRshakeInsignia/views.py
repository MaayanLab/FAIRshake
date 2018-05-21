import coreapi
from rest_framework import views, response, status, permissions, schemas
from rest_framework_swagger.views import get_swagger_view
from .models import Score

docs = get_swagger_view(title='FAIRshakeInsignia')

# TODO: Update score--API to do so
# TODO: Query to just return json score(s) as json

class InsigniaAPI(views.APIView):
    ''' Construct the insignia '''
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    schema = schemas.AutoSchema(
        manual_fields=[
            coreapi.Field('obj_uuid', required=True),
        ],
    )

    def get(self, request):
        import math as m
        scores = Score.objects.filter(obj=request.GET['obj_uuid'])

        def nearest_sq(n):
            ''' Find the nearest square to build the insignia '''
            return m.ceil(m.sqrt(n))
        
        def linearize(x1, y1, x2, y2, val):
            ''' Convert val from space x1,y1 into space x2,y2 '''
            return val * (y2 - y1) / (x2 - x1)
        
        def build_insignia(scores):
            ''' Construct the insignia with arbitrary scores and summaries
            
            This constructs a nested square where the outer square consists
            of square blocks corresponding to each score in scores and inner
            squares corresponding to each average in that particular score.
            
                    1<n<=4 summaries in second score
                        \/
            |--------|-------|
            |        |___|___|
            |        |   |   |
            |--------|-------|
            |--------|-------|
            |__|__|__|       | < 1 summary in 1st and fourth score
            |  |  |  |       | 
            |--------|-------|
                /\
            4<n<=9 summaries in third score
            
            Color is linarly chosen between Red (0) and Blue (1).
            '''
            scores_sq = nearest_sq(len(scores))
            for i, score in enumerate(scores):
                summary_sq = nearest_sq(len(score.summaries))
                for j, summary in enumerate(score.summaries):
                    yield '<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="#{fill}" />'.format(
                        x = (i % (scores_sq * summary_sq)) / (scores_sq * summary_sq),
                        y = m.ceil(i % (scores_sq * summary_sq)) / (scores_sq * summary_sq),
                        width = 1 / (scores_sq * summary_sq),
                        height = 1 / (scores_sq * summary_sq),
                        fill = linearize(0, 1, 0xff0000, 0x0000ff, score.average),
                    )
        
        return response.Response(
            '<svg viewBox="0 0 1 1">%s</svg>' % (
                ''.join(build_insignia(scores))
            ),
            status.HTTP_200_OK,
        )
