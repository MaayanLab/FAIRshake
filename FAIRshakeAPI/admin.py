from django.contrib import admin
from .models import API, APIDependency

class APIDependencyAdmin(admin.TabularInline):
    ''' Select new dependencies in Django Admin interface '''
    model = APIDependency
    fk_name = 'api'
    raw_id_fields = ('dependency',)

class APIAdmin(admin.ModelAdmin):
    ''' Update API model via Django Admin '''
    fields = ('name', 'url', 'type', )
    inlines = [APIDependencyAdmin,]

admin.site.register(API, APIAdmin)
