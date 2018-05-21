from rest_framework import viewsets, permissions
from rest_framework_swagger.views import get_swagger_view
from .models import Rubric, QuestionGroup, Question
from .serializers import RubricSerializer, QuestionGroupSerializer, QuestionSerializer

docs = get_swagger_view(title='FAIRshakeAPI')

class RubricViewSet(viewsets.ModelViewSet):
    queryset = Rubric.objects.all()
    serializer_class = RubricSerializer

class QuestionGroupViewSet(viewsets.ModelViewSet):
    queryset = QuestionGroup.objects.all().order_by('index')
    serializer_class = QuestionGroupSerializer

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all().order_by('index')
    serializer_class = QuestionSerializer
