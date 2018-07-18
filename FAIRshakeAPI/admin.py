from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
  User,
  Author,
  DigitalObject,
  Project,
  Metric,
  Rubric,
  Assessment,
  Answer,
)

admin.site.register(User, UserAdmin)
admin.site.register(Author)
admin.site.register(DigitalObject)
admin.site.register(Project)
admin.site.register(Metric)
admin.site.register(Rubric)
admin.site.register(Assessment)
admin.site.register(Answer)
