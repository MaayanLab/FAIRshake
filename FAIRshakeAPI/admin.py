from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models

class AnswerInline(admin.TabularInline):
  model = models.Answer

class AssessmentAdmin(admin.ModelAdmin):
  inlines = (AnswerInline,)

admin.site.register(models.Author, UserAdmin)
admin.site.register(models.Project)
admin.site.register(models.DigitalObject)
admin.site.register(models.Rubric)
admin.site.register(models.Metric)
admin.site.register(models.Assessment, AssessmentAdmin)
admin.site.register(models.Answer)
